from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN
from cotizaciones import (
    obtener_mejor_compra_venta_usd,
    obtener_mejor_compra_venta_btc,
    obtener_mejor_compra_venta_usdt,
    obtener_mejor_compra_venta_eth,
)
import pytz
from datetime import time

USUARIO_CHAT_ID = None

FUNCIONES_COTIZACION = {
    "usd": obtener_mejor_compra_venta_usd,
    "btc": obtener_mejor_compra_venta_btc,
    "usdt": obtener_mejor_compra_venta_usdt,
    "eth": obtener_mejor_compra_venta_eth,
    "todos": None,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global USUARIO_CHAT_ID
    USUARIO_CHAT_ID = update.effective_chat.id

    nombre = update.effective_user.first_name or "amigo"
    saludo = f"Hola {nombre}! 👋\nSelecciona la moneda para ver el mejor precio:"
    
    keyboard = [
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
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(saludo, reply_markup=reply_markup)

async def enviar_mensaje_diario(context: ContextTypes.DEFAULT_TYPE):
    if USUARIO_CHAT_ID is None:
        return
    
    mensajes = []
    for key, func in FUNCIONES_COTIZACION.items():
        if func:
            try:
                mensajes.append(func())
            except Exception as e:
                mensajes.append(f"Error al obtener cotización {key.upper()}: {e}")
    mensaje_final = "\n\n".join(mensajes)

    await context.bot.send_message(chat_id=USUARIO_CHAT_ID, text=mensaje_final, parse_mode="Markdown", disable_web_page_preview=True)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == "todos":
        mensajes = []
        for key, func in FUNCIONES_COTIZACION.items():
            if func:
                try:
                    mensajes.append(func())
                except Exception as e:
                    mensajes.append(f"Error al obtener cotización {key.upper()}: {e}")
        respuesta = "\n\n".join(mensajes)
    else:
        func = FUNCIONES_COTIZACION.get(data)
        if func is None:
            respuesta = "Opción no válida."
        else:
            try:
                respuesta = func()
            except Exception as e:
                respuesta = f"Error al obtener cotización: {e}"

    keyboard = [
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
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=respuesta, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=reply_markup)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    tz_buenos_aires = pytz.timezone("America/Argentina/Buenos_Aires")
    hora_ejecucion = time(hour=8, minute=0, second=0, tzinfo=tz_buenos_aires)
    app.job_queue.run_daily(enviar_mensaje_diario, time=hora_ejecucion)

    print("Bot iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()
