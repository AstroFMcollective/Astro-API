import re

def is_kpop(video_json: dict) -> bool:
    """
        Returns True if the video looks like a K-pop music video, False otherwise.
    """
    snippet = video_json.get("snippet", {})
    category_id = snippet.get("categoryId", None)
    channel_title = snippet.get("channelTitle", "").lower()
    description = snippet.get("description", "").lower()
    title = snippet.get("title", "").lower()

    # Quick reject: must be in music category
    if category_id != "10":
        return False
    if channel_title.endswith(" - topic"):
        return False  # Art Tracks are not considered MVs

    # Title-based signals
    if " mv" in title or "m/v" in title:
        return True

    # Description-based signals
    if "kpop" in description or "k-pop" in description:
        return True

    # Channel-based signals (common K-pop channels)
    kpop_channels = [
        "hybe labels",
        "jyp entertainment",
        "smtown",
        "yg entertainment",
        "1thek",
        "starshiptv",
        "starship",
        "cube entertainment",
        "woolliment",
        "kq entertainment"
    ]
    if any(ch in channel_title for ch in kpop_channels):
        return True

    # Hangul detection (Unicode range for Korean letters)
    if re.search(r'[\uac00-\ud7af]', title):
        return True

    return False
