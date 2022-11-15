import copy

import pathlib
import random

from typing import List, Optional, Tuple

Cell = Tuple[int, int]
Cells = List[int]
Grid = List[Cells]


class GameOfLife:
    def __init__(
        self,
        size: Tuple[int, int],
        randomize: bool = True,
        max_generations: Optional[float] = float("inf"),
    ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.generations = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        grid: Grid = []
        for y in range(0, self.rows):
            grid.append([])
            for x in range(0, self.cols):
                if randomize:
                    grid[y].append(random.randint(0, 1))
                else:
                    grid[y].append(0)

        return grid

    def get_neighbours(self, cell: Cell) -> Cells:
        neighbours = []
        high_border = max(0, cell[0] - 1)
        down_border = min(self.rows, cell[0] + 2)
        left_border = max(0, cell[1] - 1)
        right_border = min(self.cols, cell[1] + 2)
        for row in range(high_border, down_border):
            for col in range(left_border, right_border):
                if cell[0] != row or cell[1] != col:
                    neighbours.append(self.curr_generation[row][col])

        return neighbours

    def get_next_generation(self) -> Grid:
        new_grid = copy.deepcopy(self.curr_generation)

        for y in range(0, self.rows):
            for x in range(0, self.cols):
                cell_sum = sum(self.get_neighbours((y, x)))
                if self.curr_generation[y][x] == 1 and (cell_sum < 2 or cell_sum > 3):
                    new_grid[y][x] = 0
                    continue
                if self.curr_generation[y][x] == 0 and cell_sum == 3:
                    new_grid[y][x] = 1
                    continue

        return new_grid

    def step(self) -> None:
        """
        Выполнить один шаг игры.
        """
        if not self.is_max_generations_exceeded:
            self.prev_generation = self.curr_generation
            self.curr_generation = self.get_next_generation()
            self.generations += 1

    @property
    def is_max_generations_exceeded(self) -> bool:
        """
        Не превысило ли текущее число поколений максимально допустимое.
        """
        return self.generations >= self.max_generations  # type: ignore

    @property
    def is_changing(self) -> bool:
        """
        Изменилось ли состояние клеток с предыдущего шага.
        """
        return not self.curr_generation == self.prev_generation

    @staticmethod
    def from_file(filename: pathlib.Path) -> "GameOfLife":
        """
        Прочитать состояние клеток из указанного файла.
        """
        grid: Grid = []
        with filename.open() as f:
            for line in f.read().split():
                grid.append([])
                for element in line:
                    grid[-1].append(int(element))
        life = GameOfLife((len(grid), len(grid[0])))
        life.curr_generation = grid

        return life

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл.
        """
        with filename.open("w") as f:
            for line in self.curr_generation:
                f.write("".join(map(str, line)))
                f.write("\n")