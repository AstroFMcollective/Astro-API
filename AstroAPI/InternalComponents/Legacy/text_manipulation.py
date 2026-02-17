import re
import difflib
from unidecode import unidecode
from better_profanity import profanity
from discord.utils import escape_markdown

"""
	--- TEXT MANIPULATION FUNCTIONS ---

	A collection of functions used to manipulate and change text to be more
	easy to work with in filtering or query search.
"""

# --- CONSTANTS & PATTERNS ---

# List of characters that should be replaced with no character ('') instead of a space.
# Add any future characters to this list to ensure they are deleted entirely.
CHARS_TO_REMOVE_COMPLETELY = [
	"'", 
	"’"  # Smart apostrophe commonly used by Apple Music and Spotify
]

# Dynamically compile the pattern from the list
REMOVE_COMPLETELY_PATTERN = re.compile(f"[{re.escape(''.join(CHARS_TO_REMOVE_COMPLETELY))}]")

# Regex for punctuation removal
# "All" includes everything standard.
PUNC_ALL_PATTERN = re.compile(r'[!()[\];:\'",<>./?@#$%^*`_~]')
# "Some" excludes @, #, $, %, ^, &, * (common in stylizations)
PUNC_SOME_PATTERN = re.compile(r'[!()[\];:\'",<>./?`_~]')

# Regex for replacing punctuation with spaces
PUNC_TO_SPACE_PATTERN = re.compile(r'[!()[\];:\'",<>./?^*_`~-]')

# Regex for removing "feat." and "with" credits
# Matches: (feat. X), [with X], feat. X, with X at the end of strings
FEAT_PATTERN = re.compile(r'\s*[\(\[]?(?:feat\.|with)\s+.*', re.IGNORECASE)

# Music Video Declarations
MV_DECLARATIONS = [
	'(official video)',
	'(official music video)',
	'[official video]',
	'[official music video]'
]


# --- CORE FUNCTIONS ---

def remove_punctuation(text: str, remove_all: bool = True) -> str:
	"""Removes punctuation from the string using compiled regex."""
	text = REMOVE_COMPLETELY_PATTERN.sub('', text)
	
	if remove_all:
		return PUNC_ALL_PATTERN.sub('', text)
	return PUNC_SOME_PATTERN.sub('', text)

def replace_punctuation_with_spaces(text: str) -> str:
	"""Replaces certain punctuation marks with a space."""
	text = REMOVE_COMPLETELY_PATTERN.sub('', text)
	
	return PUNC_TO_SPACE_PATTERN.sub(' ', text)

def transliterate_to_ascii(text: str) -> str:
	"""Converts unicode text to its closest ASCII representation."""
	return unidecode(text)

def bare_bones(text: str, remove_all_punctuation: bool = True) -> str:
	"""
	Standardizes text: Transliterates to ASCII, lowers case, removes punctuation,
	and collapses multiple spaces.
	"""
	# 1. Transliterate first
	text = unidecode(text)
	# 2. Lowercase
	text = text.lower()
	# 3. Remove punctuation
	text = remove_punctuation(text, remove_all_punctuation)
	# 4. Fix whitespace
	return ' '.join(text.split())

def optimize_for_search(text: str, encode_special_chars: bool = True) -> str:
	"""
	Heavy optimization for API queries. 
	Fixes edge cases like block characters turning into hashes.
	"""
	# 1. Remove Feature Credits first (to avoid matching them after other manipulations)
	text = remove_feat(text)
	
	# 2. Encode special URL characters (# and &)
	# We do this BEFORE bare_bones so they aren't treated as punctuation or artifacts.
	if encode_special_chars:
		text = text.replace('#', '%23')
		text = text.replace('&', '%26')
	
	# 3. Replace punctuation with spaces (excluding apostrophes)
	# "It's a/b" -> "It's a b"
	text = replace_punctuation_with_spaces(text)
	
	# 4. Run bare_bones (Transliterate -> Lower -> Remove Punctuation(False))
	# remove_punctuation(False) will remove apostrophes ("It's" -> "its")
	# It preserves '%' so our encoded characters survive.
	text = bare_bones(text, remove_all_punctuation=False)
	
	# 5. Explicitly clean up artifacts that survive bare_bones(False)
	# Since we encoded real '#' to '%23' in step 2, any '#' remaining here 
	# must be an artifact from transliteration.
	text = text.replace('#', '')
		
	# 6. Normalize " l " to pipes (often used in Apple Music titles)
	if ' l ' in text:
		text = text.replace(' l ', ' | ')
		
	# 7. Final whitespace cleanup
	return ' '.join(text.split())

def optimize_string(text: str) -> list[str]:
	"""
	Optimizes a string and returns a list of words, removing empty elements.
	"""
	text = remove_feat(text)
	text = replace_punctuation_with_spaces(text)
	# Use standard bare_bones (False) to keep some structure
	text = bare_bones(text, remove_all_punctuation=False)
	# Split and filter empty strings in one go
	return [word for word in text.split(' ') if word]


# --- UTILITIES ---

def remove_feat(text: str) -> str:
	"""Removes 'feat.' and 'with' credits using regex."""
	# This also handles the brackets/parentheses logic automatically via the regex pattern
	return FEAT_PATTERN.sub('', text).strip()

def split_artists(text: str) -> list[str]:
	"""Splits artist strings by comma or ampersand."""
	# Split by , or &
	parts = re.split(r'[,&]', text)
	# Clean whitespace and filter empty
	return [p.strip() for p in parts if p.strip()]

def calculate_similarity(reference: str, input_str: str) -> float:
	"""Calculates similarity ratio (0-1000)."""
	return difflib.SequenceMatcher(None, reference, input_str).ratio() * 1000

def sort_similarity_lists(data_list: list, similarity_index: int = 0) -> list:
	"""Sorts a list of lists/tuples based on the similarity score at the given index."""
	return sorted(data_list, key=lambda x: x[similarity_index], reverse=True)

def percentage(hundred_percent: int, number: int) -> float:
	if hundred_percent == 0:
		return 0.0
	return number * (100 / hundred_percent)

def remove_duplicates(items: list) -> list:
	"""Removes duplicates while preserving order."""
	return list(dict.fromkeys(items))


# --- SPECIFIC DOMAIN LOGIC ---

def has_music_video_declaration(text: str) -> bool:
	"""Checks if the string contains official video markers."""
	lower_text = text.lower()
	return any(decl in lower_text for decl in MV_DECLARATIONS)

def remove_music_video_declaration(text: str) -> str:
	"""Removes official video markers from the string."""
	lower_text = text.lower()
	for decl in MV_DECLARATIONS:
		if decl in lower_text:
			# Replace case-insensitively effectively
			# (Simple approach since declarations are specific)
			pattern = re.escape(decl)
			text = re.sub(pattern, '', text, flags=re.IGNORECASE)
	return text.strip()

def clean_up_collection_title(text: str) -> str:
	"""Removes ' - Single' or ' - EP' suffixes."""
	return text.replace(' - Single', '').replace(' - EP', '')

def censor_text(text: str) -> str:
	"""Censors profanity using the wordlist."""
	if not text:
		return text
		
	path_to_file = "AstroAPI/InternalComponents/Legacy/profanity_wordlist.txt"
	profanity.load_censor_words_from_file(path_to_file)
	
	words = text.split()
	censored_words = []
	
	for word in words:
		if profanity.contains_profanity(word):
			# Censor format: F**** (First char + * + Last char)
			if len(word) > 2:
				new_word = word[0] + '*' * (len(word) - 2) + word[-1]
			else:
				new_word = '*' * len(word)
			censored_words.append(escape_markdown(new_word))
		else:
			censored_words.append(word)
			
	return ' '.join(censored_words)


print('[ServiceCatalogAPI] Text manipulation module initialized')