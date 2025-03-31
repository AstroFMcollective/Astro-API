from time import time
import json



"""
	--- UNIX TIME FUNCTIONS ---

	Commands that return Unix epoch timestamps (and save_json() because I didn't
	know where else to put it).
"""



def current_unix_time():
	return int(time())

def current_unix_time_ms():
	return int(time() * 1000)

def save_json(json_data: dict):
	with open('save_json_data.json', 'w', encoding = 'utf-8') as f:
		json.dump(json_data, f, ensure_ascii = False, indent = 4)