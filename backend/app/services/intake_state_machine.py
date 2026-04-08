ORDER = ["template", "style", "positioning", "content", "features", "generate"]


def next_stage_for_session(
    *,
    current_stage: str,
    selected_template,
    selected_style,
    summary_payload: dict,
    user_action: str,
):
    if current_stage == "template" and user_action in {"selected", "skip"}:
        return "style"
    if current_stage == "style" and user_action in {"selected", "skip"}:
        return "positioning"
    if current_stage == "positioning" and summary_payload.get("positioning_ready"):
        return "content"
    if current_stage == "content" and summary_payload.get("content_ready"):
        return "features"
    if current_stage == "features" and summary_payload.get("features_ready"):
        return "generate"
    return current_stage
