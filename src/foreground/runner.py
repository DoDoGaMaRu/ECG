import pygame

from typing import Callable

from .common import Palette, Image
from .component import Chart
from .content import Content


class Runner:
    def __init__(self,
                 title,
                 data,
                 view_cnt,
                 data_range,
                 refresh_interval):
        self.data = data
        self.event_handlers: [Callable[[pygame.event.Event], None]] = []

        pygame.init()
        pygame.display.set_caption(title)
        self.screen_width = 800
        self.screen_height = 680
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()

        self.chart = Chart(
            self.screen, (20, 15), (self.screen_width-40, 500),
            view_cnt,
            data_range
        )
        self.content = Content(
            self.screen, (20, 530), (self.screen_width-40, 130),
            self.event_handlers, refresh_interval
        )
        self.running = True

    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                for eh in self.event_handlers:
                    eh(e)

            self.screen.fill(Palette.PINK)
            self.chart.redraw(self.data)
            self.content.redraw(self.data)

            pygame.display.flip()
            self.clock.tick(60)
