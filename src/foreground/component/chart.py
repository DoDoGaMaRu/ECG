import pygame
import numpy as np

from foreground.common import Palette, Font
from util.mutex_manager import MutexManager


class Chart:
    def __init__(self,
                 screen,
                 pos: (int, int),
                 size: (int, int),
                 view_cnt: int,
                 data_range: float):
        self.screen = screen
        self.pos = pos
        self.size = size
        self.view_cnt = view_cnt
        self.data_range = data_range

        self.surface = pygame.Surface(size)

        self.ci_p = 25
        self.ci_w = self.size[0] - 2 * self.ci_p
        self.ci_h = self.size[1] - 2 * self.ci_p
        self.ci_rh = 30
        self.ci = ChartInner(
            self.surface,
            (self.ci_p, self.ci_p),
            (self.ci_w, self.ci_h),
            view_cnt,
            data_range,
            self.ci_rh
        )
        self.font1 = pygame.font.Font(Font.SCD5, 11)
        self.font2 = pygame.font.Font(Font.SCD5, 12)

    def redraw(self, data):
        self.screen.blit(self.surface, self.pos)
        self.surface.fill(Palette.WHITE)

        self.ci.redraw(data)

        for i in range(5):
            cur = self.data_range - (i*self.data_range/2)
            sx = self.ci_p
            ex = self.ci_p + 5
            y = (self.ci_p + self.ci_rh) + (i * ((self.ci_h - 2*self.ci_rh) / 4))
            pygame.draw.line(self.surface, Palette.DARKGRAY, (sx, y), (ex, y), width=2)

            ts = self.font1.render(f'{cur:.1f}', True, Palette.BLACK)
            tr = ts.get_rect(right=sx-2)
            tr.y = y-5
            self.surface.blit(ts, tr)
        ts = self.font2.render('-3s', True, Palette.BLACK)
        self.surface.blit(ts, (self.ci_p-ts.get_width()/2, self.ci_p+self.ci_h+2))
        ts = self.font2.render('0s', True, Palette.BLACK)
        self.surface.blit(ts, (self.ci_p+self.ci_w-ts.get_width()/2, self.ci_p+self.ci_h+2))


class ChartInner:
    def __init__(self,
                 screen,
                 pos: (int, int),
                 size: (int, int),
                 view_cnt: int,
                 data_range: float,
                 remain_height: int):
        self.screen = screen
        self.pos = pos
        self.size = size
        self.view_cnt = view_cnt

        self.bs = 2
        self.b_surface = pygame.Surface(self.size)
        self.size = (self.size[0] - 2*self.bs, self.size[1] - 2*self.bs)

        self.enlargement = (1 / data_range) * (self.size[1] // 2 - remain_height)
        self.surface = pygame.Surface(self.size)

        mm = MutexManager()
        self.data_lock = mm.get('data')
        self.line_width = self.size[0] / self.view_cnt

    def redraw(self, data):
        c_data = self.conv(data)
        std_height = self.size[1] // 2
        shift = self.line_width * (self.view_cnt - len(c_data))

        self.screen.blit(self.b_surface, self.pos)
        self.b_surface.fill(Palette.DARKGRAY)

        self.b_surface.blit(self.surface, (self.bs, self.bs))
        self.surface.fill(Palette.WHITE)

        pygame.draw.line(
            self.surface, Palette.GRAY,
            (0, std_height), (self.size[0], std_height),
            width=1
        )
        for i in range(1, len(c_data)):
            x = i * self.line_width + shift

            sx = int(x - self.line_width)
            sy = std_height - c_data[i - 1]
            ex = x
            ey = std_height - c_data[i]
            pygame.draw.line(
                self.surface, Palette.BLUE,
                (sx, sy), (ex, ey),
                width=2
            )

    def conv(self, data):
        with self.data_lock:
            c_data = np.array(data[-self.view_cnt:])

        # c_data = np.array(c_data) - np.mean(arr)
        c_data = c_data * self.enlargement
        return c_data
