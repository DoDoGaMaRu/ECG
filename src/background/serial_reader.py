import struct

from serial import Serial
from threading import Thread
from typing import Callable


class SerialReader:
    def __init__(self,
                 port: str,
                 handler: Callable[[int], None],
                 baudrate: int = 9600,
                 timeout: int = 5):
        self.handler = handler
        self.s = Serial(port=port, baudrate=baudrate, timeout=timeout)

        self.t = None

    def read_start(self) -> None:
        self.t = Thread(target=self.read_loop, daemon=True)
        self.t.start()

    def read_loop(self) -> None:
        while True:
            if self.s.inWaiting() > 0:
                try:
                    data = self.s.read(2)
                    if data:
                        data = struct.unpack('<h', data)[0]
                    self.handler(data)
                except:
                    pass
