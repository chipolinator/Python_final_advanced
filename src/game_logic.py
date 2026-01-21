from __future__ import annotations

from copy import deepcopy
import random
from typing import Iterable, List, Optional, Tuple

FREE_SPACE = '.'
CROSS = 'X'
ZERO = 'O'

DEFAULT_STATE = [[FREE_SPACE for _ in range(3)] for _ in range(3)]


def get_default_state() -> List[List[str]]:
    return deepcopy(DEFAULT_STATE)


def available_moves(board: List[List[str]]) -> List[Tuple[int, int]]:
    return [
        (r, c)
        for r in range(3)
        for c in range(3)
        if board[r][c] == FREE_SPACE
    ]


def apply_move(
    board: List[List[str]],
    move: Tuple[int, int],
    symbol: str,
) -> List[List[str]]:
    r, c = move
    if board[r][c] != FREE_SPACE:
        raise ValueError("Cell is already occupied")
    new_board = deepcopy(board)
    new_board[r][c] = symbol
    return new_board


def iter_lines(board: List[List[str]]) -> Iterable[List[str]]:
    rows = board
    cols = [[board[r][c] for r in range(3)] for c in range(3)]
    diags = [
        [board[i][i] for i in range(3)],
        [board[i][2 - i] for i in range(3)],
    ]
    for line in rows + cols + diags:
        yield line


def check_winner(board: List[List[str]], symbol: str) -> bool:
    return any(
        all(cell == symbol for cell in line)
        for line in iter_lines(board)
    )


def is_draw(board: List[List[str]]) -> bool:
    return all(cell != FREE_SPACE for row in board for cell in row)


def choose_random_move(board: List[List[str]]) -> Optional[Tuple[int, int]]:
    moves = available_moves(board)
    if not moves:
        return None
    return random.choice(moves)


def parse_callback_data(data: str) -> Tuple[int, int]:
    if len(data) != 2 or not data.isdigit():
        raise ValueError("Invalid callback data")
    r, c = int(data[0]), int(data[1])
    if not (0 <= r < 3 and 0 <= c < 3):
        raise ValueError("Callback out of bounds")
    return r, c
