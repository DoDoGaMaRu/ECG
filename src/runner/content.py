import time
import requests

import numpy as np
import pygame

from typing import Callable

from scipy.signal import lfilter

from .common import Palette, Image, Font
from util import MutexManager
from config import *


class Content:
    def __init__(self,
                 screen,
                 pos: (int, int),
                 size: (int, int),
                 event_handlers: [Callable[[pygame.event.Event], None]],
                 refresh_interval: int):
        self.screen = screen
        self.event_handlers = event_handlers
        self.size = size
        self.pos = pos

        self.main_img = pygame.transform.scale(
            pygame.image.load(Image.main),
            (50, 50)
        )
        self.surface = pygame.Surface(size)

        self.info_size = (size[0] // 2, size[1])
        self.info_surface = pygame.Surface(self.info_size)
        self.info_pos = self.info_surface.get_rect(topright=(size[0] - 10, 10))

        self.last_time = time.time()
        self.refresh_interval = refresh_interval
        self.cur_freq = 0.0
        self.font = pygame.font.Font(Font.SCD4, 16)
        self.title_font = pygame.font.Font(Font.SCD4, 32)

        mm = MutexManager()
        self.data_lock = mm.get('data')

        self.threshold = '1.17'
        self.th_border = pygame.Rect(290, 35, 58, 24)
        self.th_input = pygame.Rect(291, 36, 56, 22)
        self.th_input_real = pygame.Rect(291 + pos[0] + self.info_pos[0], 36 + pos[1] + self.info_pos[1], 56, 22)
        self.th_active = False

        def th_event(e):
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.th_input_real.collidepoint(e.pos):
                    self.th_active = True
                else:
                    self.th_active = False
            if self.th_active and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    self.threshold = self.threshold[:-1]
                    if len(self.threshold) == 0:
                        self.threshold += '0'
                else:
                    if len(self.threshold) < 4:
                        c = e.unicode
                        if '0' <= c <= '9':
                            if len(self.threshold) == 1 and self.threshold[0] == '0':
                                self.threshold = self.threshold[:-1]
                            self.threshold += c
                        if c == '.' and '.' not in self.threshold:
                            self.threshold += c

        self.event_handlers.append(th_event)

    def redraw(self, data):
        self.freq_refresh(data)

        self.screen.blit(self.surface, self.pos)
        self.surface.fill(Palette.WHITE)

        self.surface.blit(self.main_img, (30, 15))

        title_text = self.title_font.render('DaSiMa', True, Palette.BLACK)
        self.surface.blit(title_text, (87, 28))

        # INFO
        self.surface.blit(self.info_surface, self.info_pos)
        self.info_surface.fill(Palette.WHITE)

        freq = f'{self.cur_freq:.2f} Hz'.rjust(13)
        freq_text = self.font.render(f'Current frequency : {freq}', True, Palette.BLACK)
        freq_pos = freq_text.get_rect(topright=(self.info_size[0] - 10, 10))

        self.info_surface.blit(freq_text, freq_pos)

        th_bolder_color = Palette.BLACK if self.th_active else Palette.GRAY
        pygame.draw.rect(self.info_surface, th_bolder_color, self.th_border)
        pygame.draw.rect(self.info_surface, Palette.WHITE, self.th_input)

        threshold = f'{self.threshold} Hz'.rjust(13)
        th_label = self.font.render('Threshold :', True, Palette.BLACK)
        th_label_pos = th_label.get_rect(topright=(self.info_size[0] - 104, 20 + freq_text.get_height()))
        self.info_surface.blit(th_label, th_label_pos)
        th_text = self.font.render(f'{threshold}', True, Palette.BLACK)
        th_pos = th_text.get_rect(topright=(self.info_size[0] - 10, 20 + freq_text.get_height()))
        self.info_surface.blit(th_text, th_pos)

        is_safe = self.cur_freq < float(self.threshold)
        safe_text = self.font.render('Safe :', True, Palette.BLACK)
        safe_pos = safe_text.get_rect(topright=(self.info_size[0] - 104, 45 + th_text.get_height()))
        self.info_surface.blit(safe_text, safe_pos)
        safe_box_border = pygame.Rect(290, 61, 80, 24)
        safe_box = pygame.Rect(291, 62, 78, 22)
        safe_color = Palette.GREEN if is_safe else Palette.WHITE
        pygame.draw.rect(self.info_surface, Palette.GRAY, safe_box_border)
        pygame.draw.rect(self.info_surface, safe_color, safe_box)

        danger_text = self.font.render('Danger :', True, Palette.BLACK)
        danger_pos = danger_text.get_rect(topright=(self.info_size[0] - 104, 70 + safe_text.get_height()))
        self.info_surface.blit(danger_text, danger_pos)
        danger_box_border = pygame.Rect(290, 87, 80, 24)
        danger_box = pygame.Rect(291, 88, 78, 22)
        danger_color = Palette.WHITE if is_safe else Palette.RED
        pygame.draw.rect(self.info_surface, Palette.GRAY, danger_box_border)
        pygame.draw.rect(self.info_surface, danger_color, danger_box)

    def freq_refresh(self, data):
        cur_time = time.time()
        if self.refresh_interval < (cur_time - self.last_time) * 1000:
            self.last_time = cur_time
            try:
                tmp = self.get_freq(data)
                if tmp < NOISE_THRESHOLD:
                    self.cur_freq = tmp
                    self.send_freq()
            except:
                pass

    def get_freq(self, data) -> float:
        with self.data_lock:
            if len(data) < DATA_LEN: raise Exception
            c_data = np.array(data)
        # filtered_deep = np.array(c_data) - np.mean(c_data)
        #
        # # 평균 필터링
        # b = (1 / 10) * np.ones(10)
        # a = 1
        # average_filter_y = lfilter(b, a, filtered_deep)
        #
        # # 미분 필터
        # b = (1 / 1.0025) * np.array([1, -1])
        # a = np.array([1, -0.995])
        # derivative_filter_y = lfilter(b, a, average_filter_y)
        #
        # # 60Hz 저역 통과 필터 (LPF)
        # b = np.convolve([1, 1], [0.6310, -0.2149, 0.1512, -0.1288, 0.1227, -0.1288, 0.1512, -0.2149, 0.6310])
        # a = 1
        # comb = lfilter(b, a, derivative_filter_y)
        #
        # fs = 100
        # sd = comb[:]
        #
        # max_sd = np.max(sd)
        # trans_result = []
        #
        # for i in range(5, len(sd) - 5):
        #     if 0 < sd[i]:
        #         if sd[i-1] < sd[i] and sd[i] >= sd[i+1] and sd[i-5] < sd[i] and sd[i] >= sd[i+5]:
        #             if sd[i] > max_sd * 0.9:
        #                 trans_result.append(i)
        #
        # distance = np.diff(trans_result)
        # min_dist = np.min(distance)
        # min_dist_pos = np.where(distance == min_dist)[0][0]
        #
        # dist_rr = trans_result[min_dist_pos + 1] - trans_result[min_dist_pos]
        # t_distance = fs / dist_rr


        fs = SAMPLING_RATE
        limit = 0.15

        sd = c_data[:]
        max_sd = np.max(sd)
        if max_sd < limit: return 0

        trans_result = []
        maximum = 0
        maximum_idx = 0
        flag = False
        for i in range(5, len(sd)):
            if sd[i] > limit and sd[i] > sd[i-5]:
                flag = True
                if maximum < sd[i]:
                    maximum = sd[i]
                    maximum_idx = i
            if flag and sd[i] < limit:
                flag = False
                trans_result.append(maximum_idx)
                maximum = 0

        distance = np.diff(trans_result)
        min_dist = np.min(distance)
        min_dist_pos = np.where(distance == min_dist)[0][0]

        dist_rr = trans_result[min_dist_pos + 1] - trans_result[min_dist_pos]
        t_distance = fs / dist_rr

        return t_distance

    def send_freq(self):
        try:
            requests.post(
                DATA_SEND_URL,
                json={
                    'frequency': self.cur_freq,
                    'threshold': self.threshold
                },
                timeout=0.1
            )
        except Exception as e:
            print(e)
