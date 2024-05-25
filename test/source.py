import struct
import sys
import time

import pygame
import threading
import numpy as np
import serial

SERIAL_PORT = 'COM5'
BAUDRATE = 9600
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 600
VIEW_ELEMENT = 300
THRESHOLD = 700
ENLARGEMENT = 1000
DUMMY_LEN = 16000


dummy_data = []
with open('./resources/ECG2.txt', mode='r') as f:
    for line in f:
        d = line.split()[0]
        dummy_data.append(float(d))
    dummy_data = dummy_data[:DUMMY_LEN]

lock = threading.Lock()
arr = [0]
pre = 0
v = 0

# 시리얼 세팅
s = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

# pygame 세팅
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
start_time = time.perf_counter()

# 색상 설정
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
gray = (50, 50, 50)

# 구성 요소
ft_input = pygame.Rect(100, 700, 140, 32)


def get_current_idx() -> int:
    end_time = time.perf_counter()
    cur_ms = (end_time - start_time) * 1000
    return int(cur_ms) % DUMMY_LEN


def read_from_port(s):
    global arr
    global v
    global dummy_data
    global start_time

    while True:
        if s.inWaiting() > 0:
            try:
                v = (v+1) % 1000
                data = s.read(2)
                if data:
                    data = struct.unpack('<h', data)[0]

                    if data > THRESHOLD:
                        data = dummy_data[get_current_idx()]
                    else:
                        data = 0

                    with lock:
                        arr.append(data)
                        if len(arr) > VIEW_ELEMENT:
                            del arr[0]
            except:
                pass

        # elapsed_time = time.time() - s_time
        # time_to_sleep = max(0, delay - elapsed_time)
        # time.sleep(time_to_sleep)


def conv():
    with lock:
        data = np.array(arr)

    # data = np.array(data) - np.mean(arr)
    data = data * ENLARGEMENT
    return data


def run_game():
    global v
    global pre
    running = True

    base_font = pygame.font.Font(None, 32)

    line_width = SCREEN_WIDTH//VIEW_ELEMENT
    ft_active = False
    ft_text = ''

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN:
                if ft_input.collidepoint(e.pos):
                    ft_active = True
                else:
                    ft_active = False
            if ft_active and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    ft_text = ft_text[:-1]
                else:
                    c = e.unicode
                    if '0' <= c <= '9': ft_text += c

        if v != pre: pre = v
        else: continue

        screen.fill(white)

        y = SCREEN_HEIGHT // 2
        pygame.draw.line(screen, red, (0, y), (SCREEN_WIDTH, y), width=1)

        tmp = conv()
        with lock:
            for i in range(1, len(tmp)):
                x = i*line_width
                pygame.draw.line(
                    screen, blue,
                    (x - line_width, SCREEN_HEIGHT//2 - tmp[i-1]),
                    (x, SCREEN_HEIGHT//2 - tmp[i]),
                    width=2
                )

        pygame.draw.rect(screen, gray, ft_input)
        text_surface = base_font.render(ft_text, True, (255, 255, 255))
        screen.blit(text_surface, (ft_input.x + 5, ft_input.y + 5))

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    read_thread = threading.Thread(target=read_from_port, args=(s,), daemon=True)
    read_thread.start()

    run_game()
    pygame.quit()
    sys.exit()
