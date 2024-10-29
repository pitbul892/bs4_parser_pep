from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
PEP_URL = 'https://peps.python.org/'
TABLE_VIEW = 'pretty'
FILE_VIEW = 'file'
LOGS_FILE = 'logs'
ONE_MB = 1 * 1024 * 1024
RESULTS_FILE = 'results'
DOWNLOADS_FILE = 'downloads'
