import os
import logging
import pandas as pd

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ==============================
# CONFIGURACIÓN
# ==============================

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ TOKEN no configurado en Railway")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# URLs (ajusta si usas Google Sheets)
URL_AGOTADOS = "https://tu_url_aqui.xlsx"
URL_PROXIMOS = "https://tu_url_aqui.xlsx"

# ==============================
# FUNCIONES DE DATOS
# ==============================

def obtener_agotados():
    try:
        df = pd.read_excel(URL_AGOTADOS)
        lista = df.head(20).to_string(index=False)
        return [f"📦 {lista[i:i+3000]}" for i in range(0, len(lista), 3000)]
    except Exception as e:
        return [f"❌ Error obteniendo agotados: {e}"]


def obtener_proximos():
    try:
        df = pd.read_excel(URL_PROXIMOS)
        lista = df.head(20).to_string(index=False)
        return [f"⏳ {lista[i:i+3000]}" for i in range(0, len(lista), 3000)]
    except Exception as e:
        return [f"❌ Error obteniendo próximos: {e}"]

# ==============================
# MENÚ
# ==============================

def menu_inline():
    keyboard = [
        [InlineKeyboardButton("📦 Agotados", callback_data="agotados")],
        [InlineKeyboardButton("⏳ Próximos a vencer", callback_data="proximos")],
        [InlineKeyboardButton("🔄 Recargar", callback_data="recargar")],
        [InlineKeyboardButton("❌ Salir", callback_data="salir")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==============================
# COMANDO /START
# ==============================

async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bienvenido al bot de inventario\n\nSelecciona una opción:",
        reply_markup=menu_inline()
    )

# ==============================
# BOTONES
# ==============================

async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # 📦 AGOTADOS
    if data == "agotados":
        mensajes = obtener_agotados()
        await query.message.reply_text("📦 *PRODUCTOS AGOTADOS*\n", parse_mode="Markdown")

        for msg in mensajes:
            await query.message.reply_text(msg)

    # ⏳ PRÓXIMOS
    elif data == "proximos":
        mensajes = obtener_proximos()
        await query.message.reply_text("⏳ *PRÓXIMOS A VENCER*\n", parse_mode="Markdown")

        for msg in mensajes:
            await query.message.reply_text(msg)

    # 🔄 RECARGAR
    elif data == "recargar":
        await query.message.reply_text("🔄 Datos actualizados correctamente")

    # ❌ SALIR
    elif data == "salir":
        await query.message.reply_text("👋 Sesión finalizada.\nEscribe /start para volver.")
        return

    # 🔁 VOLVER AL MENÚ
    await query.message.reply_text(
        "¿Qué deseas hacer ahora?",
        reply_markup=menu_inline()
    )

# ==============================
# MAIN
# ==============================

def main():
    print("🚀 INICIANDO BOT...")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", inicio))
    app.add_handler(CallbackQueryHandler(botones))

    print("✅ BOT CORRIENDO...")
    app.run_polling()

# ==============================
# EJECUCIÓN
# ==============================

if __name__ == "__main__":
    main()
