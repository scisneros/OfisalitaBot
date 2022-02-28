from telegram.ext import Dispatcher


class OfisalitaHandler:
    _dispatcher: Dispatcher

    def __init__(self, dispatcher: Dispatcher):
        self._dispatcher = dispatcher
