import os
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext
from typing import Text
from utils import generate_acronym, get_arg, reverse_acronym, try_msg

import data
from config.logger import log_command
from utils import generate_acronym, get_arg, try_msg


def start(update: Update, context: CallbackContext) -> None:
    """
    Send a message when the command /start is issued.
    """
    log_command(update)
    message = "ola ceamos hamigos"
    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


def tup(update: Update, context: CallbackContext) -> None:
    """
    Responds with the message 'tup'
    """
    log_command(update)
    message = "tup"
    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


def desiglar(update: Update, context: CallbackContext) -> None:
    """
    Turns an acronym into its corresponding phrase
    """
    log_command(update)
    arg = get_arg(update)
    if update.message.reply_to_message and not arg:
        arg = update.message.reply_to_message.text

    message = data.Acronyms.get(arg.lower())
    if message is None:
        message = reverse_acronym(arg)
        message += "\n<i>Para hacer una sigla real:</i> /siglar"

    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


def siglar(update: Update, context: CallbackContext) -> None:
    """
    Saves a phrase as an acronym
    """
    log_command(update)
    arg = get_arg(update)
    if update.message.reply_to_message and not arg:
        arg = update.message.reply_to_message.text

    acronym = generate_acronym(arg)

    old_acronym = data.Acronyms.set(acronym, arg)

    message = acronym
    if old_acronym is not None:
        message += f"\n<i>(Reemplaza '{old_acronym}')</i>"

    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


def slashear(update, context):
    log_command(update)
    if update.message.reply_to_message:
        words = update.message.reply_to_message.text.split()
        response = "/" + words[0].lower()
        for word in words[1:]:
            response += word.capitalize()
        try_msg(context.bot,
                chat_id=update.message.chat_id,
                parse_mode="HTML",
                text=response)


def uwuspeech(update: Update, context: CallbackContext) -> None:
    """
    Converts a phrase into an uwu-ized version
    """
    log_command(update)
    arg = get_arg(update)
    if update.message.reply_to_message and not arg:
        arg = update.message.reply_to_message.text

    message = arg.replace('r', 'w') \
        .replace('l', 'w') \
        .replace('k', 'c') \
        .replace('p', 'pw') \
        .replace('R', 'W') \
        .replace('L', 'W') \
        .replace('K', 'C') \
        .replace('P', 'PW')

    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


# Admin Commands

def get_log(update: Update, context: CallbackContext) -> None:
    """
    Gets the bot's command log
    """
    log_command(update)
    context.bot.send_document(chat_id=update.message.from_user.id,
                              document=open(os.path.relpath(
                                  'log/bot.log'), 'rb'),
                              filename=(
                                  "pasoapasobot_log_"
                                  f"{datetime.now().strftime('%d%b%Y-%H%M%S')}"
                                  ".txt"
                              ))
