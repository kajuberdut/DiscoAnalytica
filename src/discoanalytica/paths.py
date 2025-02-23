import platformdirs

CACHE_PATH = platformdirs.user_cache_path(appname="discoanalytica", ensure_exists=True)
DATA_PATH = platformdirs.user_data_path(appname="discoanalytica", ensure_exists=True)
