from AstroAPI.ServiceCatalogAPI.media_services import music, knowledge
from AstroAPI.InternalComponents.SystemMediaObjects import Error, Empty
from AstroAPI.ServiceCatalogAPI.components.media import Meta
from AstroAPI.InternalComponents.Legacy.ini import version, deployment_channel
from AstroAPI.InternalComponents.Legacy.time import current_unix_time, current_unix_time_ms, save_json
print('[ServiceCatalogAPI] Up with flying colors!')