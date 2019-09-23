"""Solves a sudoku puzzle using a combination of two algorithms.

The first algorithm iterates through each empty space in the puzzle and tries to find what goes there by checking
that space's row, column and 3x3 box and eliminating possibilities.  If there is only one possibility, that number
is used.  If there are multiple possibilities, the space is skipped and revisited on a later iteration when more
information is available.

This first algorithm is quick, but it is only capable of solving simpler puzzles.  If it is unable to find a solution,
backtracking is used instead, which finds a solution using brute force via a depth-first search algorithm.  This is
guaranteed to find a solution, but can take a while to run for puzzles with few clues.
"""

import numpy as np
import logging


class Sudoku_Puzzle:
    """A class for creating a Sudoku puzzle object"""
    def __init__(self):
        self.puzzle = np.zeros((9,9))
        self.clues = []

    def __iter__(self):
        for row in range(9):
            for col in range(9):
                yield (row, col, self.puzzle[row, col])

    def __reversed__(self):
        for row in reversed(range(9)):
            for col in reversed(range(9)):
                yield (row, col, self.puzzle[row, col])

    def __str__(self):
        return str(self.puzzle)

    def input_puzzle(self):
        """Uses user input to build a new puzzle"""
        for num in range(9):
            while True:
                try:
                    user_input = input(f"Enter row {num + 1}: ")
                    user_input.replace(" ", "")  # removes all spaces from the user input
                    assert len(user_input) == 9
                    user_input_digits = list(map(lambda x: int(x), list(user_input)))
                    self.puzzle[num] = user_input_digits
                    break
                except (AssertionError, ValueError):
                    print("Invalid input.  Make sure you type nine digits.")

    def set_clues(self):
        """Records the currently filled spaces as given clues so they won't be overwritten by the backtracking
        algorithm"""
        self.clues = []
        for row, col, space in self:
            if space != 0:
                self.clues.append((row, col))

    def row(self, row) -> np.array:
        """Returns the specified row of the puzzle"""
        return self.puzzle[row]

    def column(self, col) -> np.array:
        """Returns the specified column of the puzzle"""
        return self.puzzle.T[col]

    def box(self, row, col) -> np.array:
        """Returns the 3x3 box that contains the specified space"""
        box_row = row - row % 3
        box_col = col - col % 3
        return self.puzzle[box_row:box_row + 3, box_col:box_col + 3]

    def set_space(self, row, col, num):
        """Sets the space at the specified row and column to the specified value"""
        self.puzzle[row, col] = num

    @property
    def has_empty_spaces(self) -> bool:
        """Returns a boolean indicating if there are any empty spaces in the puzzle"""
        for row, col, space in self:
            if space == 0:
                return True
        return False

    @property
    def has_conflict(self) -> bool:
        """Returns a boolean indicating if the most recently filled space conflicts with another space"""
        for row, col, space in reversed(self):
            if space != 0 and (row, col) not in self.clues:
                return np.count_nonzero(self.row(row) == space) > 1 \
                    or np.count_nonzero(self.column(col) == space) > 1 \
                    or np.count_nonzero(self.box(row, col) == space) > 1

    def increment_solution(self):
        for row, col, space in reversed(self):
            if space != 0 and (row, col) not in self.clues:
                if space == 9:
                    self.set_space(row, col, 0)
                else:
                    self.set_space(row, col, space + 1)
                    break

    def change_to_1(self):
        for row, col, space in self:
            if space == 0:
                self.set_space(row, col, 1)
                break


def simple_algorithm(puzzle: Sudoku_Puzzle) -> np.array:
    """The first, simple sudoku-solving algorithm.  Attempts to fill in spaces by eliminating all but one possible
    number that could fill that space.

    Arguments:
        puzzle: The sudoku puzzle to be solved

    Returns:
        np.array: The original puzzle with as much information filled in as the algorithm can manage.
    """

    def get_valid_numbers(row: int, col: int) -> list:
        """Finds all possible numbers that could go in a given space

        Arguments:
            row: row of the space
            col: column of the space

        Returns:
            list: list of all possible numbers that could occupy that space
        """

        invalid_numbers = list(puzzle.row(row))
        invalid_numbers.extend(puzzle.column(col))
        invalid_numbers.extend(puzzle.box(row, col).flat)
        valid_numbers = []
        for i in range(1, 10):
            if i not in invalid_numbers:
                valid_numbers.append(i)
        return valid_numbers

    spaces_filled = 0
    puzzle_updated = True
    while puzzle.has_empty_spaces and puzzle_updated:
        puzzle_updated = False
        for row, col, space in puzzle:
            if space == 0:
                valid_numbers = get_valid_numbers(row, col)
                if len(valid_numbers) == 1:
                    puzzle.set_space(row, col, valid_numbers[0])
                    spaces_filled += 1
                    puzzle_updated = True
    return puzzle


def backtracking(puzzle: Sudoku_Puzzle) -> Sudoku_Puzzle:
    """A brute force sudoku solving algorithm that uses a depth-first search to find a valid solution

    Arguments:
        puzzle: The sudoku puzzle to be solved

    Returns:
        Sudoku_Puzzle: The solved Sudoku puzzle
    """
    while True:
        if puzzle.has_conflict:
            puzzle.increment_solution()
        elif puzzle.has_empty_spaces:
            puzzle.change_to_1()
        else:
            break
    return puzzle


puzzle = Sudoku_Puzzle()
puzzle.input_puzzle()
puzzle = simple_algorithm(puzzle)
if puzzle.has_empty_spaces:
    print("Simple algorithm did not find a solution.  Running backtracking...")
    puzzle.set_clues()
    puzzle = backtracking(puzzle)
print(puzzle)
