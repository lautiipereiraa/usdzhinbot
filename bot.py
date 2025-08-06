import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler, 
    filters
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from cotizaciones import (
    obtener_mejor_compra_venta_usd,
    obtener_mejor_compra_venta_btc,
    obtener_mejor_compra_venta_usdt,
    obtener_mejor_compra_venta_eth,
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

FUNCIONES_COTIZACION = {
    "usd": obtener_mejor_compra_venta_usd,
    "btc": obtener_mejor_compra_venta_btc,
    "usdt": obtener_mejor_compra_venta_usdt,
    "eth": obtener_mejor_compra_venta_eth,
}

SALUDOS = {"hola", "buenas", "hey", "holi", "buen día", "buenas tardes", "buenas noches"}

def crear_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("USD", callback_data="usd"),
            InlineKeyboardButton("BTC", callback_data="btc"),
        ],
        [
            InlineKeyboardButton("USDT", callback_data="usdt"),
            InlineKeyboardButton("ETH", callback_data="eth"),
        ],
        [
            InlineKeyboardButton("Todos", callback_data="todos"),
        ],
    ])

def obtener_mensajes_cotizacion():
    mensajes = []
    for key, func in FUNCIONES_COTIZACION.items():
        try:
            mensajes.append(func())
        except Exception as e:
            mensajes.append(f"Error al obtener cotización {key.upper()}: {e}")
    return "\n\n".join(mensajes)

async def responder_a_saludos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.lower()

    if any(saludo in mensaje for saludo in SALUDOS):
        nombre = update.effective_user.first_name or "amigo"
        saludo = f"Hola {nombre}! 👋\nSelecciona la moneda para ver el mejor precio:"
        await update.message.reply_text(saludo, reply_markup=crear_keyboard())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.bot_data["usuario_chat_id"] = chat_id

    nombre = update.effective_user.first_name or "amigo"
    saludo = f"Hola {nombre}! 👋\nSelecciona la moneda para ver el mejor precio:"

    await update.message.reply_text(saludo, reply_markup=crear_keyboard())

async def enviar_mensaje_diario(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.bot_data.get("usuario_chat_id")
    if not chat_id:
        return

    mensaje = obtener_mensajes_cotizacion()
    await context.bot.send_message(
        chat_id=chat_id,
        text=mensaje,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "todos":
        respuesta = obtener_mensajes_cotizacion()
    else:
        func = FUNCIONES_COTIZACION.get(data)
        if not func:
            respuesta = "Opción no válida."
        else:
            try:
                respuesta = func()
            except Exception as e:
                respuesta = f"Error al obtener cotización: {e}"

    await query.edit_message_text(
        text=respuesta,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=crear_keyboard(),
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_a_saludos))

    print("Bot iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()
