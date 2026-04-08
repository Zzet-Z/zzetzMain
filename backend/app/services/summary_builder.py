def should_refresh_summary(*, current_stage: str, stage_completed: bool, generation_requested: bool) -> bool:
    if current_stage in {"template", "style"}:
        return True
    if stage_completed:
        return True
    if generation_requested:
        return True
    return False


def merge_summary(existing: dict, extracted: dict) -> dict:
    merged = dict(existing)
    merged.update({key: value for key, value in extracted.items() if value not in (None, "", [], {})})
    return merged
