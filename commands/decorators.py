import functools
import inspect
from typing import Callable

from telegram import Update
from telegram.ext import CallbackContext

from config.auth import group_id, debug
from config.logger import logger, log_command
from utils import try_msg
from commands.base import Command


def member_exclusive(func: Callable):
    """Decorator that checks whether the update was sent by a member of the
    group configured in auth.py. If it wasn't, sends a "forbidden" message.

    DEPRECATED: Use @command(member_exclusive=True) instead.
    """

    @functools.wraps(func)
    def member_check(update: Update, context: CallbackContext) -> None:
        if debug:
            func(update, context)
            return

        chat_member = context.bot.getChatMember(group_id, update.message.from_user.id)

        if chat_member.status not in ["administrator", "creator", "member"]:
            try_msg(
                context.bot,
                chat_id=update.message.chat_id,
                parse_mode="HTML",
                text="<b>403 FORBIDDEN</b>",
            )
            logger.warning(
                (
                    f"[NOT A MEMBER] [Command '{update.message.text}' "
                    f"was called by {update.message.chat_id}]"
                )
            )
            return

        func(update, context)
        return

    return member_check


def group_exclusive(func: Callable):
    """Decorator that checks whether the update was sent in the group
    configured in auth.py. If it wasn't, sends a "forbidden" message.

    DEPRECATED: Use @command(group_exclusive=True) instead.
    """

    @functools.wraps(func)
    def group_check(update: Update, context: CallbackContext) -> None:
        if debug:
            func(update, context)
            return

        if update.message.chat_id != group_id:
            try_msg(
                context.bot,
                chat_id=update.message.chat_id,
                parse_mode="HTML",
                text="<b>403 FORBIDDEN</b>",
            )
            logger.warning(
                (
                    f"[NOT IN GROUP] [Command '{update.message.text}' "
                    f"was called by {update.message.chat_id}]"
                )
            )
            return

        func(update, context)
        return

    return group_check


## Only to avoid name conflicts in the newer 'command' decorator
_member_exclusive = member_exclusive
_group_exclusive = group_exclusive


def command(member_exclusive: bool = False, group_exclusive: bool = False):
    """Decorator that wraps a command function."""

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(update: Update, context: CallbackContext) -> None:
            command = Command(update.message)
            log_command(update)
            try:
                if inspect.signature(func).parameters.get("command") is not None:
                    func(update, context, command=command)
                else:
                    func(update, context)
            except Exception as e:
                update.message.reply_text(
                    f"Ocurrió un error uwu:\n{str(e)}",
                )
                raise e
            return

        if member_exclusive:
            wrapper = _member_exclusive(wrapper)
        if group_exclusive:
            wrapper = _group_exclusive(wrapper)
        return wrapper

    return decorator
