import re

_HANGUL_RE = re.compile(r'[\uac00-\ud7af]')

def cleanup_mv_title(video_json: dict) -> str:
    """
   		Cleans up a MV title to only leave the song name.
    """
    title = video_json.get("snippet", {}).get("title", "") or ""
    title = title.strip()
    if not title:
        return title

    # 1) Remove trailing "official" style markers (brackets or plain)
    title = re.sub(
        r'\s*(?:\(?\s*(official\s+music\s+video|official\s+video|official\s+audio|lyric\s+video|music\s+video)\s*\)?|\[.*?(official\s+video|music\s+video).*?\])\s*$',
        '',
        title,
        flags=re.IGNORECASE
    ).strip()
    # also strip raw MV/M/V at the end
    title = re.sub(r'\s*\b(MV|M/V)\b\s*$', '', title, flags=re.IGNORECASE).strip()

    # 2) Quoted song title
    quote_segments = re.findall(r'["“”‘’\'](.+?)["“”‘’\']', title)
    for seg in quote_segments:
        seg = seg.strip()
        # Handle K-pop style Hangul(English) inside quotes
        paren = re.search(r'\(([^)]+)\)', seg)
        if paren:
            inside = _HANGUL_RE.sub('', paren.group(1)).strip()
            if re.match(r'^[A-Za-z0-9 ]+$', inside):
                return inside
        seg_clean = _HANGUL_RE.sub('', seg).strip()
        seg_clean = re.sub(r'^[\(\[\{\'"“”‘’\s]+|[\)\]\}\'"“”‘’\s]+$', '', seg_clean).strip()
        if seg_clean:
            return seg_clean

    # 3) K-pop Hangul(English) outside quotes
    m = re.search(r'[\uac00-\ud7af]+(?:\s*)\(([^)]+)\)', title)
    if m:
        inside = _HANGUL_RE.sub('', m.group(1)).strip()
        inside = re.sub(r'^[\(\[\{\'"“”‘’\s]+|[\)\]\}\'"“”‘’\s]+$', '', inside).strip()
        if inside:
            return inside

    # 4) Western: Artist - Song
    if " - " in title:
        candidate = title.split(" - ", 1)[1].strip()
    else:
        candidate = title

    # 5) Cleanup: remove Hangul, stray quotes, empty brackets
    candidate = _HANGUL_RE.sub('', candidate).strip()
    candidate = candidate.strip('"“”‘’').strip()
    candidate = re.sub(r'\([\s]*\)|\[[\s]*\]|\{[\s]*\}', '', candidate).strip()

    # If candidate is fully wrapped in brackets, unwrap if contents are simple
    m_wrap = re.match(r'^[\(\[\{]+(.+?)[\)\]\}]+$', candidate)
    if m_wrap:
        inner = m_wrap.group(1).strip()
        if re.match(r'^[A-Za-z0-9 ]+$', inner):
            return inner

    return candidate


def get_kpop_artist_name(video_json: dict) -> str:
    """
    	Extracts the artist name for a K-pop MV.
    """
    snippet = video_json.get("snippet", {})
    title = snippet.get("title", "").strip()
    channel_title = snippet.get("channelTitle", "").strip()

    # Common label patterns to exclude
    label_patterns = [
        "vevo",
        "hybe labels",
        "jyp entertainment",
        "smtown",
        "yg entertainment",
        "1thek",
        "starshiptv",
        "cube entertainment",
        "woolliment",
        "kq entertainment",
        "starship"
    ]

    # 1) Use channel if present and not a label
    if channel_title and not any(label.lower() in channel_title.lower() for label in label_patterns):
        artist = _HANGUL_RE.sub('', channel_title)  # Remove Hangul
        artist = re.sub(r'\([^\w]*\)|\[[^\w]*\]|\{[^\w]*\}', '', artist).strip()  # Remove empty brackets
        return artist

    # 2) Artist in title before quotes (e.g., "TWICE 'Song'")
    m = re.match(r'^([A-Za-z0-9\-\s]+)', title)
    if m:
        artist_candidate = m.group(1).strip()
        if artist_candidate:
            return re.sub(r'\s+', ' ', artist_candidate)

    # 3) Fallback: split by " - "
    if " - " in title:
        artist_candidate = title.split(" - ", 1)[0].strip()
        artist_candidate = re.sub(r'(vevo|labels|entertainment)', '', artist_candidate, flags=re.IGNORECASE).strip()
        artist_candidate = _HANGUL_RE.sub('', artist_candidate).strip()
        artist_candidate = re.sub(r'\([^\w]*\)|\[[^\w]*\]|\{[^\w]*\}', '', artist_candidate).strip()
        if artist_candidate:
            return artist_candidate

    # 4) Fallback cleaned channel name
    cleaned_channel = channel_title
    for label in label_patterns:
        cleaned_channel = re.sub(label, "", cleaned_channel, flags=re.IGNORECASE).strip()
    cleaned_channel = _HANGUL_RE.sub('', cleaned_channel).strip()
    cleaned_channel = re.sub(r'\([^\w]*\)|\[[^\w]*\]|\{[^\w]*\}', '', cleaned_channel).strip()
    return cleaned_channel




def devevoify(video_json: dict) -> str:
	"""
		Returns the artist name, handling VEVO-type channels.
	"""
	snippet = video_json.get("snippet", {})
	title = snippet.get("title", "").strip()
	channel_title = snippet.get("channelTitle", "").strip()

	# VEVO-style channel detection
	vevo_patterns = ["vevo"]

	is_vevo = any(pattern.lower() in channel_title.lower() for pattern in vevo_patterns)

	if is_vevo:
		# Extract artist from title: before " - " if present
		if " - " in title:
			artist = title.split(" - ", 1)[0].strip()
		else:
			# Fallback: text before first quote, or whole title
			quote_match = re.match(r'^([^\["“”‘’]+)', title)
			if quote_match:
				artist = quote_match.group(1).strip()
			else:
				artist = title

		# Remove empty parentheses/brackets
		artist = re.sub(r'\([\s]*\)|\[[\s]*\]|\{[\s]*\}', '', artist).strip()
		return artist

	# Not VEVO: return channel name
	return channel_title.replace(" - Topic", "")
