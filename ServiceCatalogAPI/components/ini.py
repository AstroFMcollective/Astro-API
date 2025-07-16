import configparser

# Nothing to see here, just a script that imports .ini file contents

config = configparser.ConfigParser()
config.read('ServiceCatalogAPI/config.ini')

keys = configparser.ConfigParser()
keys.read('ServiceCatalogAPI/keys.ini')

text = configparser.ConfigParser()
text.read('ServiceCatalogAPI/text.ini')