def get_confidence(selected_intents):
    if not selected_intents:
        return 0.0

    top1 = selected_intents[0]["score"]
    top2 = selected_intents[1]["score"] if len(selected_intents) > 1 else 0.0

    return round(top1 - top2, 3)


def extract_confidence_details(selected_intents):
    if not selected_intents:
        return 0.0, 0.0, 0.0

    top1 = selected_intents[0]["score"]
    top2 = selected_intents[1]["score"] if len(selected_intents) > 1 else 0.0
    gap = round(top1 - top2, 3)

    return top1, top2, gap