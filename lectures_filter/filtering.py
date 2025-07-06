from icalendar.cal import Event


def filter_for_karasss(event: Event) -> bool:
    summary = event["SUMMARY"]

    if summary.startswith("W - Knowledge Management in Critical Infrastructure"):
        return True

    if summary.startswith("CWP - Development Workshop"):
        return False

    return not summary.startswith("W")
