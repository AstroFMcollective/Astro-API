from unidecode import *
import difflib
import re
from ServiceCatalogAPI.components.time import save_json



"""
	--- TEXT MANIPULATION FUCTIONS ---

	A collection of functions used to manipulate and change text to be more
	easy to work with in filtering or query search.

	All of these are pretty terribly made and will be rewritten whenever everything
	else works great. But hey, they work!
"""



def remove_punctuation(string: str, remove_all: bool):
	# This is the worst thing of all time, up there with Adolf Hitler and whoever decided to remove headphone jacks from iPhones
	all_punc = f'''!()[];:'",<>./?@#$%^&*`_~'''
	some_punc = f'''!()[];:'",<>./?^*_~`'''
	for element in string:
		if remove_all == True:
			if element in all_punc:
				string = string.replace(element, '')
		elif remove_all == False:
			if element in some_punc:
				string = string.replace(element, '')
	return string

def replace_punctuation_with_spaces(string: str):
	punc = f'''!()[];:'",<>./?^*_`-~'''
	for element in string:
		if element in punc:
			string = string.replace(element, ' ')
	return string

def replace_with_ascii(string: str):
	return unidecode(string) # This is the most pointless thing of all time but I like the "replace with ASCII" name more than "unidecode"

def bare_bones(string: str, remove_all_punctuation: bool = True):
	"""
		Replaces with ASCII, removes punctuation, turns text into lowercase and deals with double spaces
	"""
	return replace_with_ascii(remove_punctuation(string, remove_all_punctuation)).lower().replace('  ',' ')

def split_artists(string: str):
	"""
		For YouTube Music and the iTunes API that often times don't have separate JSON for artists.
		Use this when it's not feasible to run another API request to get that data due to speed and efficiency concerns.
	"""
	strings = re.split(r",|\&", string)
	fixed_strings = []
	for element in strings:
		if element == ' ':
			continue
		if element[0] == ' ':
			element = element[1:]
		if element[-1] == ' ':
			element = element[:-1]
		fixed_strings.append(element)
	return fixed_strings

def get_common_data(data: list):
	# I lowkey forgot what this does don't worry about it
	element_counts = {}
	for element in data:
		if element in element_counts:
			element_counts[element] += 1
		else:
			element_counts[element] = 1
 
	max_count = max(element_counts.values(), default=0)

	most_common = [key for key, value in element_counts.items() if value == max_count]

	return most_common[0] if most_common else None

def remove_feat(string: str):
	"""
		Use ONLY when forming search queries (or if the collection name has features in it)
	"""
	if string.lower().find('feat. ') >= 0:
		if string[string.lower().index('feat. ')-1] == '[':
			first_bracket = string.lower().index('feat. ')-1
			second_bracket = string.lower().index('feat. ')-1
			while string[second_bracket-1] != ']':
				second_bracket += 1
			string = string.replace(string[first_bracket:second_bracket],'')
		elif string[string.lower().index('feat. ')-1] == '(':
			first_bracket = string.lower().index('feat. ')-1
			second_bracket = string.lower().index('feat. ')-1
			while string[second_bracket-1] != ')':
				second_bracket += 1
			string = string.replace(string[first_bracket:second_bracket],'')
		elif string[string.lower().index('feat. ')-1] == ' ':
			string = string[:string.lower().index('feat. ')-1]
	if string.lower().find('(with ') >= 0 or string.lower().find('[with ') >= 0:
		if string[string.lower().index('with ')-1] == '[':
			first_bracket = string.lower().index('with ')-1
			second_bracket = string.lower().index('with ')-1
			while string[second_bracket-1] != ']':
				second_bracket += 1
			string = string.replace(string[first_bracket:second_bracket],'')
		elif string[string.lower().index('with ')-1] == '(':
			first_bracket = string.lower().index('with ')-1
			second_bracket = string.lower().index('with ')-1
			while string[second_bracket-1] != ')':
				second_bracket += 1
			string = string.replace(string[first_bracket:second_bracket],'')
	if string[len(string)-1] == ' ':
		string = string[:len(string)-1]
	return string

def optimize_string(string: str):
	"""
		Removes most special characters that would interfere with API query searches.
	"""
	string = remove_feat(string)
	string = replace_punctuation_with_spaces(string)
	string = bare_bones(string, False)
	string_list = string.split(sep = ' ')
	for counter in range(string_list.count('')):
		string_list.remove('')
	return string_list

def calculate_similarity(reference_string: str, input_string: str):
	return difflib.SequenceMatcher(None, reference_string, input_string).ratio() * 1000

def sort_similarity_lists(data_list: list, similarity_index: int = 0):
	# Sorts media lists from most to least similar media to the query parameters
	return sorted(data_list, key = lambda x: x[similarity_index], reverse = True)

def percentage(hundred_percent: int, number: int):
	thing = 100 / hundred_percent
	return number * thing

def optimize_for_search(string: str):
	"""
		Deals with additional edge-cases which can cause services to freak out.
	"""
	# If you find a service or multiple services struggle with a character or have some weird quirk, put it in here
	optimized_string = string
	optimized_string = optimized_string.replace('#','')
	optimized_string = remove_feat(optimized_string)
	if optimized_string[0] == '&':
		optimized_string = optimized_string[1:]
	if ' l ' in optimized_string:
		for instances in range(optimized_string.count(' l ')):
			optimized_string = optimized_string.replace(' l ', ' | ')
	return optimized_string

def has_music_video_declaration(string: str):
	# Sometimes music videos are distributed in a weird way where they retain the MV declaration on YouTube music, which obv messes with search queries
	declarations = [
		'(official video)',
		'(official music video)',
		'[official video]',
		'[official music video]'
	]
	for declaration in declarations:
		if declaration in string.lower():
			return True
	return False

def remove_music_video_declaration(string: str):
	# Sometimes music videos are distributed in a weird way where they retain the MV declaration on YouTube music, which obv messes with search queries
	og_string = string
	optimized_string = string.lower()
	declarations = [
		'(official video)',
		'(official music video)',
		'[official video]',
		'[official music video]'
	]
	for declaration in declarations:
		if declaration in optimized_string:
			optimized_string = optimized_string.replace(declaration, '')
			optimized_string = optimized_string[:len(optimized_string)-1]
	og_string = og_string[:len(optimized_string)]
	return og_string

def track_is_explicit(is_explicit: bool | None):
	# LMAOOO this is a 2024 Astro 1.0 relic when Astro was nothing more than a Discord bot, those were the days
	# This just adds an emoji that no longer exists to the end of the song name
	# This is 100% deprecated but I'm keeping it for old times' sake
	# If you delete this you're fired idgaffffffff
	if is_explicit != None:
		if is_explicit:
			return '  <:explicit:1282046436598480907>'
		else:
			return ''
	else:
		return ''

def clean_up_collection_title(string: str):
	if ' - Single' in string:
		return string.replace(' - Single','')
	elif ' - EP' in string:
		return string.replace(' - EP','')
	else:
		return string

def remove_duplicates(items: list):
	return list(dict.fromkeys(items))

def convert_genius_desc_into_discord_str(description: dict):
	# TODO: this blows and I'm rewritting it as soon as we start working on the phone app
	converted_description = ''

	description = description['dom']['children'][0]['children']
	#save_json(description)
	
	for element in description:
		if isinstance(element, str):
			converted_description += element
		elif isinstance(element, dict):
			if element['tag'] == 'a':
				if isinstance(element['children'][0], dict):
					if element['children'][0]['tag'] == 'em' or element['children'][0]['tag'] == 'i':
						converted_description += f'*[{element['children'][0]['children'][0]}]({element['attributes']['href']})*'
				else:
					converted_description += f'[{element['children'][0]}]({element['attributes']['href']})'
			if element['tag'] == 'em':
				converted_description += f'*{element['children'][0]}*'



	return converted_description

print('[ServiceCatalogAPI] Text manipulation module initialized')
