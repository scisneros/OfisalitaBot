import os
from datetime import datetime

from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, CommandHandler

from commands import Commands, log_command
from handlers.common import OfisalitaHandler
from root import ROOT_DIR
from utils import try_msg


class HelperHandler(OfisalitaHandler):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__(dispatcher)
        self._dispatcher.add_handler(CommandHandler(Commands.START, self._send_hello_message))
        self._dispatcher.add_handler(CommandHandler(Commands.TUP, self._send_tup))
        self._dispatcher.add_handler(CommandHandler(Commands.GET_LOG, self.get_log))

    @staticmethod
    def _send_hello_message(update: Update, context: CallbackContext):
        """
        Send a message when the command /start is issued.
        """
        log_command(update)
        message = "ola ceamos hamigos"
        try_msg(context.bot,
                chat_id=update.message.chat_id,
                parse_mode="HTML",
                text=message)

    @staticmethod
    def _send_tup(update: Update, context: CallbackContext) -> None:
        """
        Responds with the message 'tup'
        """
        log_command(update)
        message = "tup"
        try_msg(context.bot,
                chat_id=update.message.chat_id,
                parse_mode="HTML",
                text=message)

    def get_log(self, update: Update, context: CallbackContext) -> None:
        """
        Gets the bot's command log
        """
        log_command(update)
        context.bot.send_document(chat_id=update.message.from_user.id,
                                  document=open(ROOT_DIR / "log" / "log.bot", 'rb'),
                                  filename=(
                                      "pasoapasobot_log_"
                                      f"{datetime.now().strftime('%d%b%Y-%H%M%S')}"
                                      ".txt"
                                  ))
