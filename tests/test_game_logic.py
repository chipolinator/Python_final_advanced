import pytest

from src.game_logic import (
    CROSS,
    FREE_SPACE,
    ZERO,
    apply_move,
    available_moves,
    check_winner,
    choose_random_move,
    get_default_state,
    is_draw,
    parse_callback_data,
)


def test_available_moves_initial_board():
    board = get_default_state()
    moves = available_moves(board)
    assert len(moves) == 9
    assert (0, 0) in moves
    assert (2, 2) in moves


def test_apply_move_and_occupied_cell():
    board = get_default_state()
    board = apply_move(board, (0, 0), CROSS)
    assert board[0][0] == CROSS
    with pytest.raises(ValueError):
        apply_move(board, (0, 0), ZERO)


def test_check_winner_rows_cols_diags():
    board = get_default_state()
    board[0] = [CROSS, CROSS, CROSS]
    assert check_winner(board, CROSS)

    board = get_default_state()
    for r in range(3):
        board[r][1] = ZERO
    assert check_winner(board, ZERO)

    board = get_default_state()
    for i in range(3):
        board[i][i] = CROSS
    assert check_winner(board, CROSS)


def test_draw_detection():
    board = [
        [CROSS, ZERO, CROSS],
        [CROSS, ZERO, ZERO],
        [ZERO, CROSS, CROSS],
    ]
    assert is_draw(board)


def test_choose_random_move_none_when_full():
    board = [
        [CROSS, ZERO, CROSS],
        [CROSS, ZERO, ZERO],
        [ZERO, CROSS, CROSS],
    ]
    assert choose_random_move(board) is None


def test_parse_callback_data():
    assert parse_callback_data("02") == (0, 2)
    with pytest.raises(ValueError):
        parse_callback_data("3a")
    with pytest.raises(ValueError):
        parse_callback_data("99")
