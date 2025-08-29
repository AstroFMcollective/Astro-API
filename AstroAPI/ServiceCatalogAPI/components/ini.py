import configparser

# Nothing to see here, just a script that imports .ini file contents

config = configparser.ConfigParser()
config.read('AstroAPI/config.ini')

deployment_channel = config['system']['deployment_channel']
version = config['system']['version']

keys = configparser.ConfigParser()
keys.read('AstroAPI/ServiceCatalogAPI/keys.ini')

text = configparser.ConfigParser()
text.read('AstroAPI/ServiceCatalogAPI/text.ini')

print('[ServiceCatalogAPI] .ini files initialized')
