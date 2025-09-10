import os
import datetime
import json
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
HORA_ENVIO = os.getenv("HORA_ENVIO", "08:00")
SUBS_FILE = "suscriptores.json"
def cargar_ids():
    try:
        with open(SUBS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_ids(ids):
    with open(SUBS_FILE, "w") as f:
        json.dump(ids, f)

def agregar_id(chat_id):
    ids = cargar_ids()
    if chat_id not in ids:
        ids.append(chat_id)
        guardar_ids(ids)

def eliminar_id(chat_id):
    ids = cargar_ids()
    if chat_id in ids:
        ids.remove(chat_id)
        guardar_ids(ids)


FUNCIONES_COTIZACION = {
    "usd": obtener_mejor_compra_venta_usd,
    "btc": obtener_mejor_compra_venta_btc,
    "usdt": obtener_mejor_compra_venta_usdt,
    "eth": obtener_mejor_compra_venta_eth,
}

def crear_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("USD 💵", callback_data="usd"),
         InlineKeyboardButton("BTC ₿", callback_data="btc")],
        [InlineKeyboardButton("USDT 💲", callback_data="usdt"),
         InlineKeyboardButton("ETH Ξ", callback_data="eth")],
        [InlineKeyboardButton("Todos 📊", callback_data="todos")],
    ])

def obtener_mensajes_cotizacion():
    mensajes = []
    for key, func in FUNCIONES_COTIZACION.items():
        try:
            mensajes.append(func())
        except Exception as e:
            mensajes.append(f"⚠️ Error al obtener {key.upper()}: {e}")
    return "\n\n".join(mensajes)


SALUDOS = {"hola", "buenas", "hey", "holi", "buen día", "buenas tardes", "buenas noches"}
DESPEDIDAS = {"gracias", "chau", "nos vemos", "hasta luego", "adiós", "bye"}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.effective_user.first_name or "amigo"
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Sí, quiero suscribirme", callback_data="suscribir"),
            InlineKeyboardButton("❌ No, gracias", callback_data="rechazar"),
        ]
    ])
    await update.message.reply_text(
        f"¡Hola {nombre}! 👋\n\n"
        "Soy tu asistente de cotizaciones y puedo enviarte las mejores ofertas de USD, BTC, USDT y ETH todos los días.\n\n"
        "¿Querés recibir notificaciones diarias?",
        reply_markup=keyboard
    )

async def suscribir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    agregar_id(chat_id)
    await update.message.reply_text(
        "🎉 ¡Genial! Te suscribiste correctamente a las notificaciones diarias.\n\n"
        "Cada día recibirás las mejores cotizaciones a primera hora. 🌅\n"
        "Si en algún momento querés dejar de recibirlas, usá el comando /desuscribir."
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text="¿Querés ver el mejor precio de alguna moneda ahora?",
        reply_markup=crear_keyboard()
    )

async def desuscribir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    eliminar_id(chat_id)
    await update.message.reply_text(
        "😔 Has dejado de recibir notificaciones diarias.\n"
        "Si cambias de opinión, podés volver a suscribirte con /suscribir."
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text="De todas formas, podés consultar el mejor precio de alguna moneda ahora:",
        reply_markup=crear_keyboard()
    )

async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "📌 *Lista de comandos disponibles:*\n\n"
        "/start - Inicia la conversación con el bot\n"
        "/suscribir - Suscribirte a las notificaciones diarias.\n"
        "/desuscribir - Darse de baja de las notificaciones diarias.\n"
        "/comandos - Mostrar esta lista de comandos disponibles.\n\n"
        "También podés interactuar con los botones que aparecen después de suscribirte o en el menú de monedas."
    )
    await update.message.reply_text(mensaje, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    if data == "suscribir":
        agregar_id(chat_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text="🎉 ¡Te suscribiste a las notificaciones diarias! 🌟"
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text="¿Querés ver el mejor precio de alguna moneda ahora?",
            reply_markup=crear_keyboard()
        )
        return

    if data == "rechazar":
        await context.bot.send_message(
            chat_id=chat_id,
            text="👍 Entendido, no te suscribiré. Si cambias de opinión, usá /suscribir."
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text="De todas formas, podés consultar el mejor precio de alguna moneda ahora:",
            reply_markup=crear_keyboard()
        )
        return

    if data == "todos":
        respuesta = obtener_mensajes_cotizacion()
    else:
        func = FUNCIONES_COTIZACION.get(data)
        respuesta = func() if func else "⚠️ Opción no válida."

    await context.bot.send_message(
        chat_id=chat_id,
        text=respuesta,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=crear_keyboard()
    )

async def responder_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.lower()
    nombre = update.effective_user.first_name or "amigo"

    if any(saludo in mensaje for saludo in SALUDOS):
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Sí, quiero suscribirme", callback_data="suscribir"),
                InlineKeyboardButton("❌ No, gracias", callback_data="rechazar"),
            ]
        ])
        await update.message.reply_text(
            f"¡Hola {nombre}! 👋\n\n"
            "Si querés recibir notificaciones diarias con las mejores cotizaciones, podés suscribirte acá:",
            reply_markup=keyboard
        )
        return

    if any(despedida in mensaje for despedida in DESPEDIDAS):
        await update.message.reply_text(
            f"¡De nada, {nombre}! 😊 Si querés recibir más cotizaciones, podés suscribirte con /suscribir."
        )
        return

async def enviar_mensaje_diario(context: ContextTypes.DEFAULT_TYPE):
    ids = cargar_ids()
    for chat_id in ids:
        try:
            user = await context.bot.get_chat(chat_id)
            nombre = user.first_name or "amigo"

            mensaje_cotizaciones = obtener_mensajes_cotizacion()
            mensaje_final = (
                f"👋 Hola {nombre}! Soy *usdzhinbot*.\n\n"
                "Estos son los mejores precios de hoy:\n\n"
                f"{mensaje_cotizaciones}\n\n"
                "¡Que tengas un excelente día! ☀️"
            )

            await context.bot.send_message(
                chat_id=chat_id,
                text=mensaje_final,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            print(f"✅ Mensaje diario enviado a {chat_id}")
        except Exception as e:
            print(f"❌ Error enviando a {chat_id}: {e}")

async def testjob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enviar_mensaje_diario(context)
    await update.message.reply_text("📨 Mensaje de prueba enviado.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("suscribir", suscribir))
    app.add_handler(CommandHandler("desuscribir", desuscribir))
    app.add_handler(CommandHandler("testjob", testjob))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("comandos", comandos))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))

    hora, minuto = map(int, HORA_ENVIO.split(":"))
    argentina_tz = ZoneInfo("America/Argentina/Buenos_Aires")
    hora_envio = datetime.time(hour=hora, minute=minuto, tzinfo=argentina_tz)
    app.job_queue.run_daily(enviar_mensaje_diario, time=hora_envio)

    print("Bot iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()
