import time

from background import SerialReader
from config import *
from runner import Runner
from util import MutexManager


class App:
    def __init__(self):
        mm = MutexManager()
        self.data = [0]
        self.data_lock = mm.get('data')

        self.dummy_data = self.road_dummy_data()
        self.serial_reader = SerialReader(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            handler=self.data_handler
        )

        self.start_time = time.perf_counter()
        self.runner = Runner(
            title=TITLE,
            data=self.data,
            view_cnt=VIEW_ELEMENT,
            data_range=DATA_RANGE,
            refresh_interval=REFRESH_INTERVAL
        )

    def run(self) -> None:
        self.serial_reader.read_start()
        self.runner.run()

    def data_handler(self, new_data) -> None:
        d = 0
        if THRESHOLD < new_data:
            d = self.dummy_data[self.get_current_idx()]

        with self.data_lock:
            if SHOW_REAL_DATA:
                print(new_data)
            self.data.append(d)
            if DATA_LEN < len(self.data):
                del self.data[0]

    def road_dummy_data(self) -> [float]:
        dummy_data = []
        with open(DUMMY_PATH, mode='r') as f:
            for line in f:
                d = line.split()[0]
                dummy_data.append(float(d))
            dummy_data = dummy_data[:DUMMY_LEN]
        return dummy_data

    def get_current_idx(self) -> int:
        end_time = time.perf_counter()
        cur_ms = (end_time - self.start_time) * 1000
        return int(cur_ms) % DUMMY_LEN
