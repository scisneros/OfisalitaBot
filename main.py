import data
from telegram.ext import CommandHandler, Filters

from bot import updater, dp
from commands import start, tup, desiglar, siglar,  slashear, get_log
from config.auth import admin_ids


def main():
    data.init()

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('tup', tup))
    dp.add_handler(CommandHandler('desiglar', desiglar))
    dp.add_handler(CommandHandler('siglar', siglar))
    dp.add_handler(CommandHandler('slashear', slashear))
    # Admin commands
    dp.add_handler(CommandHandler('get_log', get_log,
                   filters=Filters.user(admin_ids)))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
