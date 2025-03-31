import os

API_KEY_DB_PATH = f"{os.getcwd()}/db/api_key.db"
SQLITE_REALTIME_DB_PATH = f"/{os.getcwd()}/db/realtime.db"
SQLITE_TEST_REALTIME_DB_PATH = f"/{os.getcwd()}/db/test_realtime.db"
POSTGRESQL_METRO_DB_URL = "/metro"
UDS_ADDRESS = '/tmp/uds_address'
INTERVAL = 10