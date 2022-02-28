from telegram import Update
from telegram.ext import CallbackContext, Dispatcher, CommandHandler

import data
from commands import Commands, log_command
from handlers.common import OfisalitaHandler
from utils import get_arg, try_msg, generate_acronym


class AcronymHandler(OfisalitaHandler):
    def __init__(self, dispatcher: Dispatcher, db: data.DataBaseDriver):
        super().__init__(dispatcher)
        self.db = db
        self._dispatcher.add_handler(CommandHandler(Commands.DESIGLAR, self.unacronymize_message))
        self._dispatcher.add_handler(CommandHandler(Commands.SIGLAR, self.acronymize_message))

    def unacronymize_message(self, update: Update, context: CallbackContext) -> None:
        """
        Turns an acronym into its corresponding phrase
        """
        log_command(update)
        arg = get_arg(update)
        if update.message.reply_to_message and not arg:
            arg = update.message.reply_to_message.text

        acronym = self.db.get_acronym(arg.lower())
        message = acronym if acronym is not None else "🤷"

        try_msg(context.bot,
                chat_id=update.message.chat_id,
                parse_mode="HTML",
                text=message)

    def acronymize_message(self, update: Update, context: CallbackContext) -> None:
        """
        Saves a phrase as an acronym
        """
        log_command(update)
        arg = get_arg(update)
        if update.message.reply_to_message and not arg:
            arg = update.message.reply_to_message.text

        acronym = generate_acronym(arg)
        old_acronym = self.db.insert_acronym(acronym, arg)

        message = acronym
        if old_acronym is not None:
            message += f"\n<i>(Reemplaza '{old_acronym}')</i>"

        try_msg(context.bot,
                chat_id=update.message.chat_id,
                parse_mode="HTML",
                text=message)


class MiscTextHandler(OfisalitaHandler):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__(dispatcher)
        self._dispatcher.add_handler(CommandHandler(Commands.SLASHEAR, self.slashear))
        self._dispatcher.add_handler(CommandHandler(Commands.UWUSPEECH, self.uwuspeech))

    def slashear(self, update, context):
        log_command(update)
        if update.message.reply_to_message:
            words = update.message.reply_to_message.text.split()
            response = "/" + words[0].lower()
            for word in words[1:]:
                response += word.capitalize()
            try_msg(context.ofisalita_bot,
                    chat_id=update.message.chat_id,
                    parse_mode="HTML",
                    text=response)

    def uwuspeech(self, update: Update, context: CallbackContext) -> None:
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
