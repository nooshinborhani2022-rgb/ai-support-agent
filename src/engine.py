from src.main import (
    load_faq,
    build_tfidf_index,
    create_conversation_state,
    detect_intents,
    select_top_intents,
    detect_sentiment,
    has_success_signal,
    has_no_issue_signal,
    is_vague_query,
    detect_clarification_domain,
    generate_domain_clarification,
    apply_sentiment_routing,
    apply_confidence_sentiment_rules,
    should_skip_clarification_for_strong_multi_intent,
    get_confidence,
    extract_confidence_details,
    get_low_confidence_multi_intent_response,
    generate_response,
    get_final_action,
    add_empathy_and_politeness,
    apply_action_tone,
    apply_confidence_tone,
    get_clarification_refined_response,
    should_treat_as_clarification_followup,
    merge_with_clarification_context,
    DEFAULT_GENERAL_HELP_INTENT,
    SUCCESS_RESPONSES,
    NO_ISSUE_RESPONSES,
    should_keep_followup_context,
)


class SupportEngine:
    def __init__(self):
        self.faq_data = load_faq()
        self.vectorizer, self.matrix, self.mapping = build_tfidf_index(self.faq_data)
        self.state = create_conversation_state()

    def handle_message(self, user):
        effective_user = user
        skip_clarify_tail = False
        is_followup_clarification = should_treat_as_clarification_followup(user, self.state)

        if is_followup_clarification:
            effective_user = merge_with_clarification_context(user, self.state)

        sentiment = detect_sentiment(effective_user)
        sentiment_label = sentiment["label"]

        if has_success_signal(effective_user):
            selected = [{
                "topic": "success",
                "score": 1.0,
                "action": "answer",
                "responses": SUCCESS_RESPONSES
            }]
        elif has_no_issue_signal(effective_user):
            selected = [{
                "topic": "no_issue",
                "score": 1.0,
                "action": "answer",
                "responses": NO_ISSUE_RESPONSES
            }]
        elif is_vague_query(effective_user):
            domain = detect_clarification_domain(effective_user)

            if domain:
                clarification = generate_domain_clarification(domain)

                if clarification:
                    selected = [{
                        "topic": f"{domain}_clarification",
                        "score": 1.0,
                        "action": "clarify",
                        "responses": [clarification],
                    }]
                else:
                    selected = [DEFAULT_GENERAL_HELP_INTENT]
            else:
                selected = [DEFAULT_GENERAL_HELP_INTENT]

            selected = apply_sentiment_routing(selected, sentiment_label)
        else:
            ranked = detect_intents(
                effective_user,
                self.faq_data,
                self.vectorizer,
                self.matrix,
                self.mapping,
                sentiment_label=sentiment_label
            )

            if not ranked:
                selected = [{
                    "topic": "no_issue",
                    "score": 1.0,
                    "action": "answer",
                    "responses": NO_ISSUE_RESPONSES
                }]
            else:
                selected = select_top_intents(ranked, effective_user)
                selected = apply_sentiment_routing(selected, sentiment_label)

        predicted_topics_before_rules = [intent["topic"] for intent in selected]
        pre_rule_confidence = get_confidence(selected)

        selected, routing_reason = apply_confidence_sentiment_rules(
            selected,
            pre_rule_confidence,
            sentiment_label,
        )

        for intent in selected:
            if intent["topic"].endswith("_clarification"):
                intent["action"] = "clarify"

        if (
            routing_reason == "low_confidence_multi_intent"
            and should_skip_clarification_for_strong_multi_intent(
                effective_user,
                predicted_topics_before_rules
            )
        ):
            updated = []
            for intent in selected:
                new_intent = intent.copy()
                new_intent["action"] = "answer"
                updated.append(new_intent)
            selected = updated
            routing_reason = "strong_multi_intent_answer"

        if routing_reason == "low_confidence_multi_intent":
            updated = []
            for intent in selected:
                new_intent = intent.copy()
                new_intent["action"] = "clarify"
                updated.append(new_intent)
            selected = updated
        elif routing_reason == "strong_multi_intent_answer":
            updated = []
            for intent in selected:
                new_intent = intent.copy()
                new_intent["action"] = "answer"
                updated.append(new_intent)
            selected = updated

        final_topics_after_rules = [intent["topic"] for intent in selected]

        confidence = get_confidence(selected)
        top1_score, top2_score, score_gap = extract_confidence_details(selected)

        if is_followup_clarification:
            refined_response = get_clarification_refined_response(effective_user, selected)
            if refined_response is not None:
                response = refined_response
                skip_clarify_tail = True

                updated = []
                for intent in selected:
                    new_intent = intent.copy()
                    new_intent["action"] = "answer"
                    updated.append(new_intent)
                selected = updated
            elif routing_reason in {"low_confidence_fallback", "low_confidence_multi_intent"} and len(predicted_topics_before_rules) > 1:
                response = get_low_confidence_multi_intent_response(predicted_topics_before_rules)
            else:
                response = generate_response(selected, sentiment_label=sentiment_label)
        else:
            if routing_reason in {"low_confidence_fallback", "low_confidence_multi_intent"} and len(predicted_topics_before_rules) > 1:
                response = get_low_confidence_multi_intent_response(predicted_topics_before_rules)
            else:
                response = generate_response(selected, sentiment_label=sentiment_label)

        final_topics_after_rules = [intent["topic"] for intent in selected]

        confidence = get_confidence(selected)
        top1_score, top2_score, score_gap = extract_confidence_details(selected)

        final_action = get_final_action(selected)

        final_response = add_empathy_and_politeness(
            response,
            sentiment_label,
            final_topics_after_rules,
            pre_rule_confidence,
        )

        final_response = apply_action_tone(
            final_response,
            final_action,
            skip_clarify_tail=skip_clarify_tail
        )
        final_response = apply_confidence_tone(final_response, pre_rule_confidence)

        self.state["awaiting_clarification"] = final_action == "clarify"
        self.state["followup_context_active"] = should_keep_followup_context(
            final_topics_after_rules,
            final_action
        )
        self.state["last_user_message"] = user
        self.state["last_topics"] = final_topics_after_rules
        self.state["last_action"] = final_action
        self.state["last_routing_reason"] = routing_reason

        return {
            "response": final_response,
            "sentiment": sentiment_label,
            "intents": final_topics_after_rules,
            "confidence": confidence,
            "action": final_action,
            "routing_reason": routing_reason,
            "top1_score": top1_score,
            "top2_score": top2_score,
            "score_gap": score_gap,
            "predicted_topics_before_rules": predicted_topics_before_rules,
            "final_topics_after_rules": final_topics_after_rules,
        }