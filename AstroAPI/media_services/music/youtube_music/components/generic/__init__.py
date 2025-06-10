from ytmusicapi import YTMusic, OAuthCredentials
from AstroAPI.components.ini import keys
from AstroAPI.components.time import current_unix_time
from .about import service, component

ytm = YTMusic(
    auth =
    {
        "scope": keys['youtube_music_oauth']['scope'],
        "token_type": keys['youtube_music_oauth']['token_type'],
        "access_token": keys['youtube_music_oauth']['access_token'],
        "refresh_token": keys['youtube_music_oauth']['refresh_token'],
        "expires_at": int(keys['youtube_music_oauth']['expires_at']),
        "expires_in": int(keys['youtube_music_oauth']['expires_in'])
    },
    oauth_credentials = 
        OAuthCredentials(
            client_id = str(keys['youtube_music']['client_id']),
            client_secret = str(keys['youtube_music']['client_secret'])
        )
) if int(keys['youtube_music_oauth']['expires_at']) > current_unix_time() else YTMusic()