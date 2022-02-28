# noinspection PyPackageRequirements
import logging

from telegram.ext import Updater, Dispatcher, JobQueue

from config.auth import TOKEN
from config.logger import logger
from config.persistence import persistence
from data import DataBaseDriver
from handlers.text_processing import AcronymHandler, MiscTextHandler
from handlers.utility import HelperHandler


class OfisalitaBot:
    """Main class of the bot."""
    db: DataBaseDriver
    updater: Updater
    dispatcher: Dispatcher
    job_queue: JobQueue
    logger: logging.Logger

    def __init__(self):
        self.db = DataBaseDriver()
        self._start_updater(TOKEN)
        self.dispatcher = self.updater.dispatcher
        self.job_queue = self.updater.job_queue
        HelperHandler(dispatcher=self.dispatcher)
        AcronymHandler(self.dispatcher, self.db)
        MiscTextHandler(self.dispatcher)

    def _start_updater(self, token: str) -> None:
        """Starts the bot updater with a given token."""
        self.updater = Updater(token=TOKEN, use_context=True, persistence=persistence)
        logger.info("Updater started")

    def run(self):
        logger.info("Starting bot polling service.")
        self.updater.start_polling()
        self.updater.idle()
