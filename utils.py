import random
import re
import tiktoken
from string import ascii_lowercase, ascii_uppercase

from telegram import Update, Bot, TelegramError, constants as tg_constants
from telegram.ext import CallbackContext

import data
from config.logger import logger

word_file = "static/words.txt"
WORDS = open(word_file).read().splitlines()
LETTER_DICTIONARY = {}
for character in ascii_lowercase:
    LETTER_DICTIONARY[character] = [word for word in WORDS
                                    if word.lower().startswith(character)]


def _try_send(bot: Bot, attempts: int,
              function: callable, error_message: str, **params):
    """
    Make multiple attempts to send a message.
    """
    chat_id = params["chat_id"]
    attempt = 1
    while attempt <= attempts:
        try:
            ret = function(**params)
        except TelegramError as e:
            logger.error((
                f"[Attempt {attempt}/{attempts}] {error_message} {chat_id} "
                f"raised following error: {type(e).__name__}: {e}"))
        else:
            break
        attempt += 1

    if attempt > attempts:
        logger.error((f"Max attempts reached for chat {str(chat_id)}."
                      "Aborting message and raising exception."))

    return ret


def try_msg(bot: Bot, attempts: int = 2, **params) -> None:
    """
    Make multiple attempts to send a text message.
    """
    error_message = "Messaging chat"
    message = _try_send(bot, attempts, bot.send_message,
                        error_message, **params)
    if message:
        data.Messages.add(
            message.message_id,
            message.date,
            message.from_user.id,
            message.from_user.username,
            message.text,
            message.reply_to_message.message_id if message.reply_to_message else None
        )


def try_edit(bot: Bot, attempts: int = 2, **params) -> None:
    """
    Make multiple attempts to edit a message.
    """
    error_message = f"Editing message {params['message_id']} in chat"
    _try_send(bot, attempts, bot.edit_message_text, error_message, **params)


def try_sticker(bot: Bot, attempts: int = 2, **params) -> None:
    """
    Make multiple attempts to send a sticker.
    """
    error_message = "Stickering chat"
    _try_send(bot, attempts, bot.send_sticker, error_message, **params)


def try_poll(bot: Bot, attempts: int = 2, **params) -> None:
    """
    Make multiple attempts to send a poll.
    """
    error_message = "Sending poll to chat"
    _try_send(bot, attempts, bot.send_poll, error_message, **params)


def try_delete(bot: Bot, attempts: int = 2, **params) -> None:
    """
    Make multiple attempts to delete a message.
    """
    error_message = f"Deleting message {params['message_id']} in chat"
    _try_send(bot, attempts, bot.delete_message, error_message, **params)


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


def get_arg_reply(update: Update) -> str:
    """
    Returns the argument of a command or the text of a reply.
    (Preference towards replies)
    """
    if update.message.reply_to_message is None:
        return get_arg(update)
    try:
        arg = update.message.reply_to_message.text
    except AttributeError:
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


def guard_reply_to_message(update: Update) -> bool:
    """
    Guard statement:
    Verifies if a message is a reply.
    To be used in conjunction with a return.
    False if the code should keep running.
    True if the code should stop running.
    """
    return not update.message.reply_to_message


def guard_reply_to_bot_message(update: Update,
                               context: CallbackContext) -> bool:
    """
    Guard statement:
    Verifies if a reply is replying to a message from the actual bot.
    To be used in conjunction with a return.
    False if the code should keep running.
    True if the code should stop running.
    """
    return context.bot.id != update.message.reply_to_message.from_user.id


def guard_hashtag(content: str, match: str) -> bool:
    """
    Guard statement:
    Verifies if a reply is replying to a message from the actual bot.
    To be used in conjunction with a return.
    False if the code should keep running.
    True if the code should stop running.
    """
    return not content.startswith(match)


def guard_editable_bot_message(update: Update,
                               context: CallbackContext,
                               match: str) -> bool:
    """
    Guard statement:
    Verifies if a reply is replying to a message from the actual bot that
    begins with a specific hashtag.
    To be used in conjunction with a return.
    False if the code should keep running.
    True if the code should stop running.
    """
    if guard_reply_to_message(update):
        return True

    if guard_reply_to_bot_message(update, context):
        return True

    if guard_hashtag(update.message.reply_to_message.text, match):
        return True

    return False


def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.encoding_for_model("gpt-4o")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def get_names_in_message(message: str) -> list[str]:
    """
    Returns a list of usernames in a message.
    """
    return re.findall(r"(?:\B|\/\w+)@(\w{5,32}\b)", message)


def generate_aliases(names: list[str]) -> dict[str, str]:
    """
    Generates a dictionary associating usernames with aliases.
    """
    alias_dict = {}
    for name in names:
        if name not in alias_dict:
            alias_type = "Persona" if not name.lower().endswith("bot") else "Bot"
            alias = None
            while alias is None or alias in alias_dict.values():
                alias = f"{alias_type}{''.join([random.choice(ascii_uppercase) for _ in range(5)])}"
            alias_dict[name] = alias
    return alias_dict


def get_alias_dict_from_string(text: str) -> dict[str, str]:
    """
    Returns a dictionary associating usernames mentioned in a string with aliases.
    """
    return generate_aliases(get_names_in_message(text))


def get_alias_dict_from_messages_list(messages):
    """
    Returns a dictionary associating usernames from a list of messages with aliases.
    Considers message authors and mentions.
    """
    names = []
    for message in messages:
        names.append(message["username"])
        names += get_names_in_message(message["message"])
    return generate_aliases(names)


def anonymize(messages, alias_dict):
    """
    Anonymizes the usernames in a list of messages.
    """
    for message in messages:
        if isinstance(message, str):
            for username, alias in alias_dict.items():
                message = message.replace(username, alias)
        else:
            for username, alias in alias_dict.items():
                message["message"] = message["message"].replace(username, alias)
            message["username"] = alias_dict[message["username"]]
    return messages


def deanonymize(generated_message, alias_dict):
    """
    Deanonymizes the usernames in a generated message
    """
    for username, alias in alias_dict.items():
        generated_message = generated_message.replace(alias, username)
    return generated_message
