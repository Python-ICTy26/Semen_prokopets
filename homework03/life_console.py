import argparse
import curses
import curses.ascii
import pathlib
import time

from life import GameOfLife
from ui import UI

class Console(UI):
    def __init__(self, life: GameOfLife) -> None:
        super().__init__(life)

    def draw_borders(self, screen) -> None:
        """ Отобразить рамку. """
        screen.border()

    def draw_grid(self, screen) -> None:
        """ Отобразить состояние клеток. """
        for y in range(0, self.life.rows):
            for x in range(0, self.life.cols):
                if self.life.curr_generation[y][x] == 1:
                    screen.addch(y + 1, x + 1, "*")
                else:
                    screen.addch(y + 1, x + 1, " ")

    def run(self) -> None:
        curses.initscr()
        screen = curses.newwin(self.life.rows + 2, self.life.cols + 2)
        self.draw_borders(screen)
        screen.nodelay(True)
        curses.noecho()

        running = True
        pause = False

        while running:
            event = screen.getch()
            if event == curses.ascii.SP:
                pause = not pause
            if event == ord("s"):
                self.life.save(pathlib.Path("My game"))
            if event == ord("q"):
                running = False
            if not pause:
                self.draw_grid(screen)
                screen.refresh()
                self.life.step()
                time.sleep(1)
        curses.endwin()


if __name__ == "__main__":
    analyzing = argparse.ArgumentParser()
    analyzing.add_argument("--rows", "-r", type=int, default=4, help="Количество строк")
    analyzing.add_argument("--cols", "-c", type=int, default=30, help="Количество столбцов")
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
            size=(args.rows, args.cols), randomize=args.random, max_generations=args.max_generations
        )
    console = Console(life)
    console.run()