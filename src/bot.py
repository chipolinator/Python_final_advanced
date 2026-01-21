from copy import deepcopy
import logging
import os
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

TOKEN = os.getenv('TG_TOKEN')

CONTINUE_GAME, FINISH_GAME = range(2)

FREE_SPACE = '.'
CROSS = 'X'
ZERO = 'O'


DEFAULT_STATE = [[FREE_SPACE for _ in range(3)] for _ in range(3)]


def get_default_state():
    return deepcopy(DEFAULT_STATE)


def generate_keyboard(
    state: list[list[str]],
) -> list[list[InlineKeyboardButton]]:
    return [
        [
            InlineKeyboardButton(state[r][c], callback_data=f'{r}{c}')
            for r in range(3)
        ]
        for c in range(3)
    ]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['keyboard_state'] = get_default_state()
    keyboard = generate_keyboard(context.user_data['keyboard_state'])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Твой ход: поставь X.',
        reply_markup=reply_markup,
    )
    return CONTINUE_GAME


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query is None:
        return CONTINUE_GAME

    await query.answer()

    state = context.user_data.get('keyboard_state')
    if state is None:
        state = get_default_state()

    data = query.data or ''
    if len(data) != 2 or not data.isdigit():
        return CONTINUE_GAME

    row, col = int(data[0]), int(data[1])
    if state[row][col] != FREE_SPACE:
        return CONTINUE_GAME

    state[row][col] = CROSS
    fields = [cell for row in state for cell in row]

    if won(fields):
        context.user_data['keyboard_state'] = state
        keyboard = generate_keyboard(state)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            'Ты победил! Нажми /start, чтобы сыграть снова.',
            reply_markup=reply_markup,
        )
        return FINISH_GAME

    if FREE_SPACE not in fields:
        context.user_data['keyboard_state'] = state
        keyboard = generate_keyboard(state)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            'Ничья! Нажми /start, чтобы сыграть снова.',
            reply_markup=reply_markup,
        )
        return FINISH_GAME

    free_moves = [
        (r, c)
        for r in range(3)
        for c in range(3)
        if state[r][c] == FREE_SPACE
    ]
    if free_moves:
        ai_row, ai_col = random.choice(free_moves)
        state[ai_row][ai_col] = ZERO

    fields = [cell for row in state for cell in row]

    if won(fields):
        context.user_data['keyboard_state'] = state
        keyboard = generate_keyboard(state)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            'Бот победил! Нажми /start, чтобы сыграть снова.',
            reply_markup=reply_markup,
        )
        return FINISH_GAME

    if FREE_SPACE not in fields:
        context.user_data['keyboard_state'] = state
        keyboard = generate_keyboard(state)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            'Ничья! Нажми /start, чтобы сыграть снова.',
            reply_markup=reply_markup,
        )
        return FINISH_GAME

    context.user_data['keyboard_state'] = state
    keyboard = generate_keyboard(state)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        'Твой ход: поставь X.',
        reply_markup=reply_markup,
    )
    return CONTINUE_GAME


def won(fields: list[str]) -> bool:
    win_positions = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ]
    for a, b, c in win_positions:
        if fields[a] != FREE_SPACE and fields[a] == fields[b] == fields[c]:
            return True
    return False


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['keyboard_state'] = get_default_state()
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONTINUE_GAME: [
                CallbackQueryHandler(game, pattern='^' + f'{r}{c}' + '$')
                for r in range(3)
                for c in range(3)
            ],
            FINISH_GAME: [
                CallbackQueryHandler(end, pattern='^' + f'{r}{c}' + '$')
                for r in range(3)
                for c in range(3)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
