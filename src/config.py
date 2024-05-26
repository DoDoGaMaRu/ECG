from configparser import ConfigParser

conf = ConfigParser()
conf.read('./resources/config.ini', encoding='utf-8')

# SERIAL
SERIAL_PORT = conf['SERIAL']['SERIAL_PORT']
BAUDRATE = int(conf['SERIAL']['BAUDRATE'])
THRESHOLD = int(conf['SERIAL']['THRESHOLD'])
SAMPLING_RATE = 100
SHOW_REAL_DATA = conf.getboolean('SERIAL', 'SHOW_REAL_DATA')

# DUMMY
DUMMY_PATH = conf['DUMMY']['DUMMY_PATH']
DUMMY_LEN = int(conf['DUMMY']['DUMMY_LEN'])
DATA_LEN = 300

# RUNNER
TITLE = 'ECG Monitor'
VIEW_ELEMENT = 300
DATA_RANGE = 0.4
REFRESH_INTERVAL = 1000
NOISE_THRESHOLD = 50

# NETWORK
DATA_SEND_URL = conf['NETWORK']['DATA_SEND_URL']
