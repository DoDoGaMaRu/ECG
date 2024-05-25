import pygame
import sys
import serial
import threading


import struct
import numpy as np
from scipy.signal import lfilter
lock = threading.Lock()
v = 0

def read():
    data_size = 2
    data = ser.read(data_size)  # 데이터 읽기

    # 데이터가 완전히 수신되었는지 확인
    if len(data) == data_size:
        # struct.unpack을 사용해 바이트 데이터를 int로 변환
        ints = struct.unpack('<H', data)  # 'H'는 부호 없는 16비트 정수, '<'는 리틀 엔디언
        #print(ints)
        return list(ints)
    else:
        print("Full data not received")
        return [0]

def read_from_port(ser):
    global v
    global arr
    while True:
        if ser.in_waiting > 0:
            # tmp2 = read()
            # with lock:
            #     v += 1
            #     v %= 1000
            #     arr += tmp2

            try:
                v+=1
                v%=1000
                data = ser.read(2)  # 2바이트 읽기
                if data:
                    number = struct.unpack('<h', data)[0]  # '<h'는 리틀 엔디안 2바이트 부호 있는 정수
                    with lock:
                        arr.append(number)
                        if len(arr) > screen_width:
                            del arr[0]
            except:
                pass

def filter_signal(data, b, a=1):
    return lfilter(b, a, data)

def conv():
    # 평균 필터링
    with lock:
        FilteredDeep = np.array(arr) - np.mean(arr)

        # b = (1 / 10) * np.ones(10)
        # a = 1
        # average_filter_Y = filter_signal(FilteredDeep, b, a)
        # 미분 필터
        # b = (1 / 1.0025) * np.array([1, -1])
        # a = np.array([1, -0.995])
        # derivative_filter_Y = filter_signal(average_filter_Y, b, a)
        #
        # # 60Hz 저역 통과 필터 (LPF)
        # b = np.convolve([1, 1], [0.6310, -0.2149, 0.1512, -0.1288, 0.1227, -0.1288, 0.1512, -0.2149, 0.6310])
        # a = 1
        # comb = filter_signal(derivative_filter_Y, b, a)
    return FilteredDeep


ser = serial.Serial('COM5', 9600, timeout=1)

thread = threading.Thread(target=read_from_port, args=(ser,))
thread.start()

# 파이게임 초기화
pygame.init()

# 스크린 설정
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

# 색상 설정
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)

# 상자 초기 위치
box_x = 300
box_y = 300
box_size = 50
clock = pygame.time.Clock()

# 게임 루프 플래그
running = True
arr = [0]
pre = 0
# 게임 루프
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if v != pre:
        pre = v
    else:
        continue

    screen.fill(white)

    pygame.draw.line(screen, red, (0, 400), (800, 400), width=2)
    tmp = conv()

    with lock:
        for i in range(1,len(tmp)):
            pygame.draw.line(
                screen,
                (blue),
                ((i-1), screen_height//2 - tmp[i-1]),
                (i,screen_height//2 - tmp[i]), 2)

    pygame.display.flip()
    #clock.tick(60)

# 파이게임 종료
pygame.quit()
sys.exit()