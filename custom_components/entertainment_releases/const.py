DOMAIN = "entertainment_releases"

CONF_API_TOKEN = "api_token"
CONF_REGION = "region"

CONF_THEATRICAL_DAYS = "theatrical_days"
CONF_DIGITAL_DAYS = "digital_days"
CONF_TV_DAYS = "tv_days"
CONF_REFRESH_INTERVAL = "refresh_interval"

CONF_MOVIE_LANGUAGE = "movie_language"
CONF_MOVIE_MIN_SCORE = "movie_min_score"

CONF_TV_PROVIDERS = "tv_providers"
CONF_TV_GENRES = "tv_genres"
CONF_TV_LANGUAGE = "tv_language"

DEFAULT_REGION = "US"

DEFAULT_THEATRICAL_DAYS = 7
DEFAULT_DIGITAL_DAYS = 1
DEFAULT_TV_DAYS = 1
DEFAULT_REFRESH_INTERVAL = 6

DEFAULT_MOVIE_LANGUAGE = "en"
DEFAULT_MOVIE_MIN_SCORE = 1.0
DEFAULT_TV_LANGUAGE = "en"

# Common US subscription streaming providers in TMDB.
DEFAULT_TV_PROVIDERS = [
    "8",     # Netflix
    "9",     # Amazon Prime Video
    "15",    # Hulu
    "337",   # Disney Plus
    "350",   # Apple TV Plus
    "386",   # Peacock Premium
    "531",   # Paramount Plus
    "1899",  # Max
]

DEFAULT_TV_GENRES = []

MIN_LOOKAHEAD_DAYS = 1
MAX_LOOKAHEAD_DAYS = 30

MIN_REFRESH_INTERVAL = 1
MAX_REFRESH_INTERVAL = 24

MIN_MOVIE_SCORE = 0.0
MAX_MOVIE_SCORE = 10.0

API_BASE = "https://api.themoviedb.org/3"

PLATFORMS = ["sensor"]
