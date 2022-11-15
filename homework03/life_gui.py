import argparse
import pathlib
import random

import pygame
from pygame.constants import K_SPACE, KEYDOWN, MOUSEBUTTONUP, QUIT, K_s

from life import GameOfLife
from ui import UI


class GUI(UI):
    def __init__(self, life: GameOfLife, cell_size: int = 10, speed: int = 10) -> None:
        super().__init__(life)
        self.cell_size = cell_size
        self.speed = speed
        self.height = self.life.rows * cell_size
        self.width = self.life.cols * cell_size
        self.screen = pygame.display.set_mode((self.width, self.height))

    def draw_lines(self) -> None:
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (0, y), (self.width, y))

    def draw_grid(self) -> None:
        for y in range(0, self.life.rows):
            for x in range(0, self.life.cols):
                if self.life.curr_generation[y][x] == 1:
                    pygame.draw.rect(
                        self.screen,
                        pygame.Color(0, 255, 0),
                        (
                            x * self.cell_size + 1,
                            y * self.cell_size + 1,
                            self.cell_size - 1,
                            self.cell_size - 1,
                        ),
                    )
                else:
                    pygame.draw.rect(
                        self.screen,
                        pygame.Color(255, 255, 255),
                        (
                            x * self.cell_size + 1,
                            y * self.cell_size + 1,
                            self.cell_size - 1,
                            self.cell_size - 1,
                        ),
                    )

    def run(self) -> None:
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game of Life")
        self.screen.fill(pygame.Color("white"))

        running = True
        pause = False
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_SPACE:
                    pause = not pause
                if event.type == QUIT:
                    running = False
                if event.type == KEYDOWN and event.key == K_s:
                    self.life.save(pathlib.Path("My game"))
                if event.type == MOUSEBUTTONUP and event.button == 1:
                    position = pygame.mouse.get_pos()
                    x = position[0] // self.cell_size
                    y = position[1] // self.cell_size
                    self.life.curr_generation[y][x] = int(not self.life.curr_generation[y][x])
            if not pause:
                self.draw_lines()
                # Выполнение одного шага игры (обновление состояния ячеек)
                self.life.step()
            # Отрисовка списка клеток
            self.draw_grid()

            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()


def main():
    if __name__ == "__main__":
        analyzing = argparse.ArgumentParser()
        analyzing.add_argument("--rows", "-r", type=int, default=4, help="Количество строк")
        analyzing.add_argument("--cols", "-c", type=int, default=30, help="Количество столбцов")
        analyzing.add_argument("--cell_size", type=int, default=60, help="Размер клетки")
        analyzing.add_argument("--speed", "-s", type=float, default=10, help="Скорость игры")
        analyzing.add_argument("--random", action="store_true", default=True, help="Рандом")
        analyzing.add_argument(
            "--max_generations",
            type=float,
            default=float("inf"),
            help="Максимальное количество поколений",
        )
        analyzing.add_argument(
            "--from_file_path", type=str, default="", help="Путь к файлу из которого прочитать игру"
        )
        args = analyzing.parse_args()
        if args.from_file_path != "":
            life = GameOfLife.from_file(pathlib.Path(args.source))
        else:
            life = GameOfLife(
                size=(args.rows, args.cols),
                randomize=args.random,
                max_generations=args.max_generations,
            )
        gui = GUI(life, cell_size=args.cell_size, speed=args.speed)
        gui.run()


if __name__ == "__main__":
    main()