import random
import re
from string import ascii_lowercase

from config.logger import logger
from telegram import Update, Bot, TelegramError, constants as tg_constants

word_file = "static/words.txt"
WORDS = open(word_file).read().splitlines()
LETTER_DICTIONARY = {}
for character in ascii_lowercase:
    LETTER_DICTIONARY[character] = [word for word in WORDS
                                    if word.lower().startswith(character)]


def try_msg(bot: Bot, attempts: int = 2, **params) -> None:
    """
    Make multiple attempts to send a message.
    """
    chat_id = params["chat_id"]
    attempt = 1
    while attempt <= attempts:
        try:
            bot.send_message(**params)
        except TelegramError as e:
            logger.error((
                f"[Attempt {attempt}/{attempts}] Messaging chat {chat_id} "
                f"raised following error: {type(e).__name__}: {e}"
            )
            )
        else:
            break
        attempt += 1

    if attempt > attempts:
        logger.error((
            f"Max attempts reached for chat {str(chat_id)}."
            "Aborting message and raising exception."
        )
        )


def send_long_message(bot: Bot, **params) -> None:
    """
    Recursively breaks long texts into multiple messages,
    prioritizing newlines for slicing.
    """
    text = params.pop("text", "")

    params_copy = params.copy()
    maxl = params.pop("max_length", tg_constants.MAX_MESSAGE_LENGTH)
    slice_str = params.pop("slice_str", "\n")
    if len(text) > maxl:
        slice_index = text.rfind(slice_str, 0, maxl)
        if slice_index <= 0:
            slice_index = maxl
        sliced_text = text[:slice_index]
        rest_text = text[slice_index + 1:]
        try_msg(bot, text=sliced_text, **params)
        send_long_message(bot, text=rest_text, **params_copy)
    else:
        try_msg(bot, text=text, **params)


def get_arg(update: Update) -> str:
    try:
        arg = update.message.text[(update.message.text.index(" ") + 1):]
    except ValueError:
        arg = ""
    return arg


def generate_acronym(string: str) -> str:
    """
    Generates a lowercase acronym of the input string.

    Examples:
        >>>generate_acronym("qué querís que te diga")
        qqqtd
        >>>generate_acronym("*se resbala y se cambia a movistar*")
        *sryscam*
        >>>generate_acronym(":j_____:")
        :j:
        >>>generate_acronym("(broma pero si quieres no es broma)")
        (bpsqneb)
    """

    parentheses = (["(", "[", "{"], [")", "]", "}"])
    bra, ket = '', ''

    if string[0] in parentheses[0]:
        bra = string[0]
        bra_index = parentheses[0].index(bra)
        ket = parentheses[1][bra_index]

    delimiters = list(filter(None, ['*', ':', bra, ket]))
    regex_pattern = fr"\s+|({'|'.join(map(re.escape, delimiters))})"

    string_list = list(filter(None, re.split(regex_pattern, string)))

    out = ""

    for word in string_list:
        out += word[0]
        if word.find("?") > 0:
            out += "?"

    return out.lower()


def reverse_acronym(string: str) -> str:
    """
    Makes a random phrase from an acronym
    """
    string_list = list(string)
    out = ""
    for initial in string_list:
        if initial in LETTER_DICTIONARY:
            out += random.choice(LETTER_DICTIONARY[initial])
        else:
            out += initial
        out += " "
    return out.lower().title()
