"""This module contains the main entry point of the bot.

Avoid implementing functionalities in this file, prefer creating or modifying other modules.
"""
# noinspection PyPackageRequirements
import data
from bot import OfisalitaBot
from config.auth import admin_ids
from telegram.ext import CommandHandler, Filters

if __name__ == '__main__':
    ofisalita_bot = OfisalitaBot()
    ofisalita_bot.run()
