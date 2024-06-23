from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import data
from bot import updater, dp
from config.auth import admin_ids, group_id, debug

from commands.acronym import desiglar, siglar, glosario
from commands.admin import get_log, prohibir
from commands.counter import contador, sumar, restar
from commands.list import lista, agregar, quitar, editar, deslistar
from commands.response import start, tup, gracias, weekly_poll, reply_hello
from commands.summary import resumir, button
from commands.text import slashear, uwuspeech, repetir
from commands.gpt import reply_gpt, reply_fill, desigliar
from commands.stats import stats, stats_detail


def add_command(command: str | list[str], callback: callable, **kwargs):
    """
    Helper: Adds a command with one or more aliases to the dispatcher.
    """
    if isinstance(command, list):
        for c in command:
            dp.add_handler(CommandHandler(c, callback, **kwargs))
    else:
        dp.add_handler(CommandHandler(command, callback, **kwargs))


def receive_message(update, context):
    """
    Receives a message and stores it in the database.
    This doesn't receive messages from the bot itself.
    """
    author_id = update.message.from_user.id
    author_username = update.message.from_user.username
    if update.message.forward_from:
        author_id = update.message.forward_from.id
        author_username = update.message.forward_from.username
    elif update.message.forward_sender_name:
        author_id = 0
        author_username = update.message.forward_sender_name
    if update.message.text is not None:
        data.Messages.add(
            update.message.message_id,
            update.message.date,
            author_id,
            author_username,
            update.message.text,
            update.message.reply_to_message.message_id if update.message.reply_to_message else None
        )


def main():
    data.init()

    # Acronym
    add_command('desiglar', desiglar)
    add_command('siglar', siglar)
    add_command('glosario', glosario)

    # Admin
    add_command('get_log', get_log, filters=Filters.user(admin_ids))
    add_command('prohibir', prohibir)

    # Counter
    add_command('contador', contador)
    add_command(['sumar', 'incrementar'], sumar)
    add_command(['restar', 'decrementar'], restar)

    # List
    add_command(['lista', 'listar'], lista)
    add_command('agregar', agregar)
    add_command('quitar', quitar)
    add_command('editar', editar)
    add_command(['deslistar', 'cerrar'], deslistar)

    # Text
    add_command(['uwuspeech', 'uwuspeak', 'uwuizar', 'uwu'], uwuspeech)
    add_command('slashear', slashear)
    add_command('repetir', repetir)

    # Response
    add_command('tup', tup)
    add_command('start', start)
    add_command(['gracias', 'garcias'], gracias)
    add_command('asistencia', weekly_poll)
    add_command('hello', reply_hello)

    # AI
    add_command('gpt', reply_gpt)
    add_command('gb', reply_fill)
    add_command('desigliar', desigliar)

    # Summary
    add_command('resumir', resumir)

    # Stats
    add_command('stats', stats)
    add_command('stats_detail', stats_detail)

    dp.add_handler(CallbackQueryHandler(button))

    # Message handler to store messages in the database.
    dp.add_handler(MessageHandler(
        (Filters.text &
         Filters.chat_type.group &
         Filters.chat(chat_id=group_id))
        if not debug else Filters.text,
        receive_message),
        group=1)  # Group must be != 0 so it doesn't conflict with command handlers.

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
