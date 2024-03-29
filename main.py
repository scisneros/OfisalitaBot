from telegram.ext import CommandHandler, Filters

import data
from bot import updater, dp
from config.auth import admin_ids

from commands.acronym import desiglar, siglar, glosario
from commands.admin import get_log, prohibir
from commands.counter import contador, sumar, restar
from commands.list import lista, agregar, quitar, editar, deslistar
from commands.response import start, tup, gracias, weekly_poll, reply_hello
from commands.text import slashear, uwuspeech, repetir
from commands.gpt import reply_gpt, reply_qa, reply_fill


def add_command(command: str | list[str], callback: callable, **kwargs):
    """
    Helper: Adds a command with one or more aliases to the dispatcher.
    """
    if isinstance(command, list):
        for c in command:
            dp.add_handler(CommandHandler(c, callback, **kwargs))
    else:
        dp.add_handler(CommandHandler(command, callback, **kwargs))


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
    add_command('qa', reply_qa)
    add_command('gb', reply_fill)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
