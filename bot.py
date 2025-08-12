import os
import datetime
from zoneinfo import ZoneInfo  
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
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

def cargar_config():
    chat_ids_env = os.getenv("CHAT_IDS", "")
    chat_ids = [int(cid.strip()) for cid in chat_ids_env.split(",") if cid.strip().isdigit()]

    hora_envio_str = os.getenv("HORA_ENVIO", "16:00")
    try:
        hora, minuto = map(int, hora_envio_str.split(":"))
    except ValueError:
        print(f"⚠️ Formato de HORA_ENVIO inválido: '{hora_envio_str}', usando 16:00 por defecto.")
        hora, minuto = 16, 0

    return chat_ids, hora, minuto

CHAT_IDS, hora, minuto = cargar_config()

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

async def enviar_saludo(update: Update):
    nombre = update.effective_user.first_name or "amigo"
    saludo = f"Hola {nombre}! 👋\nSelecciona la moneda para ver el mejor precio:"
    await update.message.reply_text(saludo, reply_markup=crear_keyboard())

async def responder_a_saludos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.lower()
    if any(saludo in mensaje for saludo in SALUDOS):
        await enviar_saludo(update)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enviar_saludo(update)

async def enviar_mensaje_diario(context: ContextTypes.DEFAULT_TYPE):
    mensaje = obtener_mensajes_cotizacion()
    for chat_id in CHAT_IDS:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=mensaje,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
            print(f"✅ Mensaje enviado a {chat_id}")
        except Exception as e:
            print(f"❌ Error enviando a {chat_id}: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "todos":
        respuesta = obtener_mensajes_cotizacion()
    else:
        func = FUNCIONES_COTIZACION.get(data)
        respuesta = func() if func else "Opción no válida."

    await query.edit_message_text(
        text=respuesta,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=crear_keyboard(),
    )

async def testjob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enviar_mensaje_diario(context)
    await update.message.reply_text("✅ Mensaje enviado (test).")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("testjob", testjob))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_a_saludos))

    argentina_tz = ZoneInfo("America/Argentina/Buenos_Aires")
    hora_envio = datetime.time(hour=hora, minute=minuto, tzinfo=argentina_tz)
    app.job_queue.run_daily(enviar_mensaje_diario, time=hora_envio)

    print("🤖 Bot iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()
