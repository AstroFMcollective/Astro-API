import configparser
import json
from pathlib import Path

# Nothing to see here, just a script that imports .ini file contents

config = configparser.ConfigParser()
config.read('AstroAPI/config.ini')

deployment_channel = config['system']['deployment_channel']
version = config['system']['version']

keys = configparser.ConfigParser()
keys.read('AstroAPI/InternalComponents/Legacy/keys.ini')

text = configparser.ConfigParser()
text.read('AstroAPI/InternalComponents/Legacy/text.ini')

credentials_path = Path(__file__).resolve().parent / "credentials.json"
with credentials_path.open("r", encoding="utf-8") as f:
    credentials = json.load(f)

print('[ServiceCatalogAPI] .ini files initialized')
