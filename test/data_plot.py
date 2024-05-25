import sys
import pygame
import numpy as np
from scipy.signal import lfilter


SCREEN_HEIGHT = 800
SCREEN_WIDTH = 800
ENLARGEMENT = 1000


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# 색상 설정
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)


data = []
with open('../resources/ECG2.txt', mode='r') as f:
    for line in f:
        d = line.split()[0]
        data.append(float(d)*ENLARGEMENT)

filtered_deep = np.array(data) - np.mean(data)

# 평균 필터링
b = (1 / 10) * np.ones(10)
a = 1
average_filter_y = lfilter(b, a, filtered_deep)

# 미분 필터
b = (1 / 1.0025) * np.array([1, -1])
a = np.array([1, -0.995])
derivative_filter_y = lfilter(b, a, average_filter_y)

# 60Hz 저역 통과 필터 (LPF)
b = np.convolve([1, 1], [0.6310, -0.2149, 0.1512, -0.1288, 0.1227, -0.1288, 0.1512, -0.2149, 0.6310])
a = 1
comb = lfilter(b, a, derivative_filter_y)
data = comb


freq = (len(data) // 1000) // 16

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    screen.fill(white)

    y = SCREEN_HEIGHT // 2
    pygame.draw.line(screen, red, (0, y), (SCREEN_WIDTH, y), width=2)

    for i in range(1, SCREEN_WIDTH):
        x = i
        sy = data[freq * i - freq]
        ey = data[freq * i]
        pygame.draw.line(
            screen, blue,
            (x-1, SCREEN_HEIGHT//2 - sy),
            (x, SCREEN_HEIGHT//2 - ey)
        )
    pygame.display.flip()


pygame.quit()
sys.exit()
