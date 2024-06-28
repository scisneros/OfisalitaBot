import data
import json
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import CallbackContext

from ai.provider import ai_client
from ai.base import GenAIMessage
import ai.pricing as prc
from commands.decorators import command
from commands.base import Command
from utils import (
    num_tokens_from_string,
    get_alias_dict_from_string,
    get_alias_dict_from_messages_list,
    anonymize,
    deanonymize,
)

try:
    from config.auth import openai_key
except ImportError:
    openai_key = None

DEFAULT_MODEL = "claude-3-sonnet-20240229"
MAX_MESSAGES_TO_SUMMARIZE = 1000

PROMPT_SYSTEM_MESSAGE_SINGLE = (
    "Eres un bot para resumir mensajes de un chat. "
    + "Te daré un mensaje y debes resumirlo de forma concisa. No incluyas nada más que el resumen en tu mensaje. "
    + "Utiliza HTML para los formatos de <b>negritas</b> e <i>itálicas</i>, NO uses otras etiquetas aparte de <b> y <i>. NO uses Markdown."
)

PROMPT_SYSTEM_MESSAGE_MULTIPLE = (
    "Eres un bot para resumir mensajes de un chat. "
    + "Te daré una lista de mensajes en el siguiente formato:\n"
    + "(message_id, username, message, reply_to)\n"
    + "\n"
    + "Donde:\n"
    + "message_id: Identificador único del mensaje.\n"
    + "reply_to: Identificador único del mensaje al que se responde.\n"
    + "username: Nombre de usuario de quien envió el mensaje.\n"
    + "message: El contenido del mensaje.\n"
    + "\n"
    + "Usa esta información para entregar un resumen de lo que se conversó en el chat."
    + "La conversación es informal, en español chileno, puede contener errores gramaticales y ortográficos, utilizar anglicismos y conceptos inventados."
    + "El campo 'reply_to' indica respuestas en la conversación, pero no siempre se utiliza, y los mensajes podrían estar relacionados sin un reply_to explícito."
    + "Al resumir, hazlo como una lista de sucesos relevantes por cada tema de conversación. Usa un lenguaje muy conciso, tipo lista con bullet-points. Cada ítem en la lista es un tema de conversación, con sub-ítemes con algunas conclusiones y resúmenes de las ideas expresadas. Usa los nombres de los usuarios. Utiliza HTML para los formatos de negritas (<b>) e itálicas (<i>).\n"
    + "\n"
    + "Ejemplo\n"
    + "INPUT:\n"
    + "[(123, 34924, 'usuario1', 'ola, hoy vi a Baloian', None),"
    + "(124, 24587, 'usuario2', 'de vdd? qué bacan! lo amoooo, y como estaba?', 123),"
    + "(125, 34924, 'usuario1', 'se veía piola, estaba tomando pap', None),"
    + "(126, 24587, 'usuario2', 'ogh que paja, me carga la pap', None),"
    + "(127, 87562, 'usuario3', 'wena cabros descubrí un framework de js se llama TupJS', None),"
    + "(128, 24587, 'usuario2', 'uuu si lo cacho, apaña caleta pero me gusta más BebJS', 127),"
    + "(129, 34924, 'usuario1', 'que chucha están hablando', None)]"
    + "OUTPUT:\n"
    + "<b>Baloian estaba tomando pap</b>\n"
    + "- usuario1 lo vio.\n"
    + "- usuario2 ama a Baloian pero odia la pap.\n"
    + "<b>Conversación sobre frameworks de JS</b>\n"
    + "- usuario3 descubre TupJS.\n"
    + "- usuario2 prefiere BebJS.\n"
    + "- usuario1 no entiende del tema.\n"
)


@command(group_exclusive=True)
def resumir(update: Update, context: CallbackContext, command: Command) -> None:
    """
    Summarizes multiples messages from the database.
    """
    cmd = command
    msg = update.message

    ai_model = cmd.opts.get("m") or cmd.opts.get("model") or DEFAULT_MODEL

    client = ai_client(
        model=ai_model, user_id=msg.from_user.id, username=msg.from_user.username
    )
    # Summarize a specific single replied message
    if not cmd.arg and msg.reply_to_message:
        alias_dict = get_alias_dict_from_string(msg.reply_to_message.text)
        prompt_text = anonymize([msg.reply_to_message.text], alias_dict)[0]
        response = client.generate(
            system=PROMPT_SYSTEM_MESSAGE_SINGLE,
            conversation=[GenAIMessage("user", prompt_text)],
        )
        result = deanonymize(response.message, alias_dict)
        message_link = f"https://t.me/c/{str(msg.chat_id).replace('-100','')}/{msg.reply_to_message.message_id}"
        try:
            msg.reply_html(
                f'Resumen del <a href="{message_link}">mensaje</a>:\n\n{result}'
            )
        except Exception:
            msg.reply_markdown_v2(f"Resumen del [mensaje]({message_link}):\n\n{result}")
        return

    # Summarize N messages
    n = None
    try:
        n = int(cmd.arg)
    except ValueError:
        msg.reply_text(
            "Debes indicar la cantidad de mensajes hacia atrás que quieres resumir."
        )

    if n and n > MAX_MESSAGES_TO_SUMMARIZE:
        msg.reply_text(
            f"El máximo de mensajes a resumir es de {MAX_MESSAGES_TO_SUMMARIZE}."
        )
        return

    summarize_from = msg.message_id - 1
    if msg.reply_to_message:
        summarize_from = msg.reply_to_message.message_id

    raw_messages = data.Messages.get_n(n, from_id=summarize_from)
    input_messages = [
        {
            "message_id": m["message_id"],
            "username": m["username"],
            "message": m["message"],
            "reply_to": m["reply_to"],
        }
        for m in raw_messages
    ]

    if not input_messages:
        msg.text(
            "No hay mensajes para resumir. Es posible que lo que intentas resumir no haya sido registrado en la base de datos."
        )
        return

    prompt_messages = [
        PROMPT_SYSTEM_MESSAGE_MULTIPLE,
        {
            "role": "user",
            "content": [{"type": "text", "text": str(input_messages)}],
        },
    ]

    input_tokens = num_tokens_from_string(str(prompt_messages), DEFAULT_MODEL)
    # TODO: Calculate this based on the input messages
    expected_output_tokens = 300

    msg.reply_html(
        f"El resumen de {len(input_messages)} mensajes con <i>{client.model}</i> costará aproximadamente <b>${round(prc.get_total_cost(DEFAULT_MODEL, input_tokens, expected_output_tokens), 3)} USD</b>\n"
        + (f"\nOPTS: {json.dumps(cmd.opts)}" if cmd.opts else ""),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Resumir",
                        callback_data=json.dumps(
                            ["confirm_summary", n, summarize_from]
                        ),
                    ),
                    InlineKeyboardButton(
                        "Cancelar", callback_data=json.dumps(["cancel_summary"])
                    ),
                ],
            ]
        ),
        quote=True,
    )


def _do_resumir(query: CallbackQuery, context: CallbackContext) -> None:
    msg = query.message
    try:
        opts = re.search(r"OPTS: (\{.*\})", msg.text)
        ai_model = DEFAULT_MODEL
        if opts:
            opts = json.loads(opts.group(1))
            ai_model = opts.get("m") or opts.get("model") or ai_model
        client = ai_client(
            model=ai_model,
            user_id=msg.reply_to_message.from_user.id,
            username=msg.reply_to_message.from_user.username,
        )
        query_data = json.loads(query.data)
        n = query_data[1]
        summarize_from = query_data[2]
        if not summarize_from:
            summarize_from = msg.reply_to_message.message_id

        raw_messages = data.Messages.get_n(n, from_id=summarize_from)
        input_messages = [
            {
                "message_id": m["message_id"],
                "username": m["username"],
                "message": m["message"],
                "reply_to": m["reply_to"],
            }
            for m in raw_messages
        ]
        alias_dict = get_alias_dict_from_messages_list(input_messages)
        input_messages = anonymize(input_messages, alias_dict)

        input_tokens = num_tokens_from_string(str(input_messages), DEFAULT_MODEL)

        response = client.generate(
            system=PROMPT_SYSTEM_MESSAGE_MULTIPLE,
            conversation=[GenAIMessage("user", str(input_messages))],
        )

        result = deanonymize(response.message, alias_dict)

        start_message_link = f"https://t.me/c/{str(msg.chat_id).replace('-100','')}/{input_messages[0]['message_id']}"
        end_message_link = f"https://t.me/c/{str(msg.chat_id).replace('-100','')}/{input_messages[-1]['message_id']}"
        final_message = (
            f'Resumen de {len(input_messages)} mensajes [<a href="{start_message_link}">Inicio</a> - <a href="{end_message_link}">Fin</a>]:\n'
            + f"<i>Costo: ${round(response.cost, 5)} USD</i>\n"
            + f"<i>Tokens input: {input_tokens}, Tokens output: {response.usage['output']}, Ratio: {int(response.usage['output'])/input_tokens}</i>\n\n"
            + str(result)
        )
        try:
            msg.reply_html(
                f'Resumen de {len(input_messages)} mensajes [<a href="{start_message_link}">Inicio</a> - <a href="{end_message_link}">Fin</a>]:\n'
                + f"<i>Costo: ${round(response.cost, 5)} USD</i>\n"
                + f"<i>Tokens input: {input_tokens}, Tokens output: {response.usage['output']}, Ratio: {int(response.usage['output'])/input_tokens}</i>\n\n"
                + str(result),
                reply_to_message_id=msg.reply_to_message.message_id,
            )
        except Exception:
            msg.reply_markdown_v2(
                final_message,
                reply_to_message_id=msg.reply_to_message.message_id,
            )
    except Exception as e:
        msg.reply_text(f"Ocurrió un error al procesar el resumen:\n{e}")
        raise e


# TODO: Refactor. This receives all callback queries, not just the ones from the summary command.
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data = json.loads(query.data)
    # Only requesting user can answer
    if query.message.reply_to_message.from_user.id != query.from_user.id:
        query.answer("Solo quien solicitó el resumen puede confirmarlo.")
        return
    else:
        query.answer()
        if query_data[0] == "confirm_summary":
            query.edit_message_text(
                text=f"{query.message.text}\n\nResumen aceptado. Procesando..."
            )
            _do_resumir(query, context)
        elif query_data[0] == "cancel_summary":
            query.edit_message_text(text=f"{query.message.text}\n\nResumen cancelado.")
