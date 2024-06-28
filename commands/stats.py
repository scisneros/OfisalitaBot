from datetime import datetime
import data

from telegram import Update
from telegram.ext import CallbackContext

from commands.decorators import member_exclusive
from config.logger import log_command
from utils import send_long_message, try_msg


@member_exclusive
def stats_detail(update: Update, context: CallbackContext) -> None:
    """
    Sends a message with the number of tokens used by user by model.
    """
    log_command(update)
    try:
        usage = data.AIRequests.get()

        usage_map = {}
        users_map = {}
        for r in usage:
            if r["model"] not in usage_map:
                usage_map[r["model"]] = {}
            if r["user_id"] not in usage_map[r["model"]]:
                usage_map[r["model"]][r["user_id"]] = {
                    "input": 0,
                    "output": 0,
                    "cost": 0,
                }
            users_map[r["user_id"]] = r["username"]
            usage_map[r["model"]][r["user_id"]]["input"] += r["input_tokens"]
            usage_map[r["model"]][r["user_id"]]["output"] += r["output_tokens"]
            usage_map[r["model"]][r["user_id"]]["cost"] += r["cost"]
            usage_map[r["model"]] = dict(
                sorted(
                    usage_map[r["model"]].items(),
                    key=lambda item: item[1]["cost"],
                    reverse=True,
                )
            )

        text = "<b>Estadísticas de uso de tokens:</b>\n"
        text += f"<i>Desde {datetime.utcfromtimestamp(usage[-1]['datetime']).strftime('%Y-%m-%d')}</i>\n"
        totals = {"input": 0, "output": 0, "cost": 0}
        for model, users in usage_map.items():
            text += f"\n✨ Modelo: <i>{model}</i> ✨\n"
            for user_id, usage in users.items():
                text += (
                    f"👤 {users_map[user_id]}:\n"
                    + f"Input: {usage['input']}; Output: {usage['output']}\n"
                    + f"Gasto: ${round(usage['cost'], 5)} USD\n"
                )
            text += "\n"
            model_total_input = sum([u["input"] for u in users.values()])
            model_total_output = sum([u["output"] for u in users.values()])
            model_total_cost = sum([u["cost"] for u in users.values()])
            totals["input"] += model_total_input
            totals["output"] += model_total_output
            totals["cost"] += model_total_cost
            text += (
                "Total modelo\n"
                + f"Input: {model_total_input}; Output: {model_total_output}\n"
                + f"Gasto: ${round(model_total_cost, 5)} USD\n"
                + "----------"
            )
        text += (
            "\n📊<b>Estadísticas totales:</b>\n"
            + f"Input: {totals['input']}; Output: {totals['output']}\n"
            + f"Gasto: ${round(totals['cost'], 5)} USD"
        )

        send_long_message(
            context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=text,
            reply_to_message_id=update.message.message_id,
        )

    except Exception as e:
        try_msg(
            context.bot,
            chat_id=update.message.chat_id,
            text=f"Hubo un error al obtener las estadísticas: {e}",
            reply_to_message_id=update.message.message_id,
        )
        raise e


@member_exclusive
def stats(update: Update, context: CallbackContext) -> None:
    """
    Sends a message with the ranking of users by total expenses.
    """
    log_command(update)
    try:
        usage = data.AIRequests.get()

        usage_map = {}
        users_map = {}
        for r in usage:
            if r["user_id"] not in usage_map:
                usage_map[r["user_id"]] = 0
            users_map[r["user_id"]] = r["username"]
            usage_map[r["user_id"]] += r["cost"]
            usage_map = dict(
                sorted(
                    usage_map.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
            )

        text = "<b>Ranking de gastos totales:</b>\n"
        text += f"<i>Desde {datetime.utcfromtimestamp(usage[-1]['datetime']).strftime('%Y-%m-%d')}</i>\n\n"
        i = 1
        emoji = ["🥇", "🥈", "🥉"]
        for user_id, usage in usage_map.items():
            prefix = emoji[i - 1] if i <= 3 else f"#{i}. "
            text += f"<b>{prefix}{users_map[user_id]}</b>:\n" + f"${round(usage, 5)} USD\n"
            i += 1
        text += "----------"
        text += "\n💸<b>Gasto total:</b>\n"
        text += f"${round(sum(usage_map.values()), 5)} USD"

        send_long_message(
            context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=text,
            reply_to_message_id=update.message.message_id,
        )
    except Exception as e:
        try_msg(
            context.bot,
            chat_id=update.message.chat_id,
            text=f"Hubo un error al obtener las estadísticas: {e}",
            reply_to_message_id=update.message.message_id,
        )
        raise e
