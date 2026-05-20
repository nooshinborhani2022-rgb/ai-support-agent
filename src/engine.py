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
    get_clarification_refined_response,
    should_treat_as_clarification_followup,
    merge_with_clarification_context,
    DEFAULT_GENERAL_HELP_INTENT,
    SUCCESS_RESPONSES,
    NO_ISSUE_RESPONSES,
    should_keep_followup_context,
    update_conversation_memory,
)
from src.retrieval import retrieve_support_context

def get_retrieval_domain(final_topics):
    topic_domain_map = {
        "login_issue": "account",
        "password_reset": "account",
        "account_locked": "account",
        "account_clarification": "account",

        "billing_question": "billing",
        "billing_clarification": "billing",
        "payment_failed": "billing",
        "payment_clarification": "billing",

        "charge_explanation": "charge",
        "double_charge": "charge",
        "refund_request": "charge",
        "charge_clarification": "charge",

        "fraud_report": "security",
        "security_clarification": "security",

        "order_status": "order",
        "delivery_issue": "order",
        "order_clarification": "order",
    }

    if not final_topics:
        return None

    return topic_domain_map.get(final_topics[0])


def get_clear_multi_intent_response(topics):
    parts = []

    if "login_issue" in topics:
        parts.append(
            "🔐 For your login issue, try resetting your password first. "
            "If that doesn’t work, let me know if you see an error message or a lockout notice."
        )

    if "refund_request" in topics:
        parts.append(
            "💸 For your refund request, please open your account dashboard or billing/order history section "
            "and start a refund request from the relevant charge."
        )

    if "payment_failed" in topics:
        parts.append(
            "💳 For your payment issue, check whether your card was declined, the transaction failed, "
            "or the checkout process did not complete."
        )

    if "double_charge" in topics:
        parts.append(
            "🔁 For the duplicate charge, compare the dates and amounts in your billing history. "
            "If the same payment appears more than once, this should be reviewed by support."
        )

    if "fraud_report" in topics:
        parts.append(
            "🚨 For the security concern, this may involve unauthorized activity, "
            "so it should be escalated to a support or security specialist."
        )

    if len(parts) < 2:
        return None

    return "I can help with both issues.\n\n" + "\n\n".join(parts)

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
        
        elif detect_clarification_domain(effective_user) == "security":
            selected = [{
                "topic": "fraud_report",
                "score": 3.0,
                "action": "escalate",
                "responses": [
                    "This may involve fraud, so I'm escalating it immediately.",
                    "I'll send this to a specialist right away for investigation.",
                    "This looks like a security issue, so I'm escalating it."
                ],
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

                    if intent["topic"] in {"fraud_report", "security_clarification"}:
                        new_intent["action"] = "escalate"
                    else:
                        new_intent["action"] = "answer"

                    updated.append(new_intent)

                selected = updated
            elif routing_reason in {"low_confidence_fallback", "low_confidence_multi_intent"} and len(predicted_topics_before_rules) > 1:
                response = get_low_confidence_multi_intent_response(predicted_topics_before_rules)
            else:
                response = generate_response(selected, sentiment_label=sentiment_label)
        else:
            if len(selected) > 1:
                response = get_low_confidence_multi_intent_response(
                [intent["topic"] for intent in selected]
        )
            elif routing_reason in {"low_confidence_fallback", "low_confidence_multi_intent"} and len(predicted_topics_before_rules) > 1:
                response = get_low_confidence_multi_intent_response(predicted_topics_before_rules)
            else:
                response = generate_response(selected, sentiment_label=sentiment_label)
                final_topics_after_rules = [intent["topic"] for intent in selected]

        confidence = get_confidence(selected)
        top1_score, top2_score, score_gap = extract_confidence_details(selected)

        clear_multi_response = get_clear_multi_intent_response(final_topics_after_rules)

        if clear_multi_response and not is_followup_clarification:
            response = clear_multi_response

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
        final_topics_after_rules,
        skip_clarify_tail=skip_clarify_tail
        )

        retrieval_domain = [
        get_retrieval_domain([topic])
        for topic in final_topics_after_rules
        ]

        retrieval_domain = [domain for domain in retrieval_domain if domain]

        retrieved_context = retrieve_support_context(
        user,
        domain=retrieval_domain
        )

        retrieved_context_text = None
        retrieved_source = None
        retrieved_score = None

        if retrieved_context:
            retrieved_context_text = retrieved_context.get("context")
            retrieved_source = retrieved_context.get("source")
            retrieved_score = retrieved_context.get("score")


        self.state["awaiting_clarification"] = final_action == "clarify"
        self.state["followup_context_active"] = should_keep_followup_context(
            final_topics_after_rules,
            final_action
        )
        self.state["last_user_message"] = user
        self.state["last_topics"] = final_topics_after_rules
        self.state["last_action"] = final_action
        self.state["last_routing_reason"] = routing_reason
        update_conversation_memory(
            self.state,
            user,
            final_topics_after_rules,
            final_action
        )
        self.state["active_domain"] = self.state.get("memory", {}).get("active_domain")

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
            "memory": self.state.get("memory", {}),
            "retrieved_context": retrieved_context_text,
            "retrieved_source": retrieved_source,
            "retrieved_score": retrieved_score,
        }
    