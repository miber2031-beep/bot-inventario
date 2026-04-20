import pandas as pd
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ================================
# 🔑 TOKEN (LOCAL + RAILWAY)
# ================================
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    TOKEN = "8671710771:AAFS7WdDTq3Wlx6cC80NGRLVLMdKzzeTW1M"  # 👈 reemplaza solo para pruebas locales


# ================================
# 🌐 GOOGLE SHEETS LINKS
# ================================
URL_AGOTADOS = "https://docs.google.com/spreadsheets/d/1xNOPwkbunW1-9_wDIb7PwbdBn6oLvDGZZKnWVnhJJO4/gviz/tq?tqx=out:csv&gid=0"

URL_PROXIMOS = "https://docs.google.com/spreadsheets/d/1xNOPwkbunW1-9_wDIb7PwbdBn6oLvDGZZKnWVnhJJO4/gviz/tq?tqx=out:csv&gid=462007210"
# ================================
# 🔴 AGOTADOS
# ================================
def obtener_agotados():
    try:
        df = pd.read_csv(URL_AGOTADOS)

        if df.empty:
            return ["No hay productos agotados"]

        mensajes = []
        bloque = ""

        for _, row in df.iterrows():
            codigo = str(row.iloc[0])
            material = str(row.iloc[1])
            estado = str(row.iloc[2])

            linea = f"🔴 {codigo}\n📦 {material}\n📌 {estado}\n────────────\n"

            if len(bloque + linea) > 4000:
                mensajes.append(bloque)
                bloque = linea
            else:
                bloque += linea

        if bloque:
            mensajes.append(bloque)

        return mensajes

    except Exception as e:
        return [f"Error AGOTADOS: {e}"]

# ================================
# 🟡 PROXIMOS
# ================================
def obtener_proximos():
    try:
        df = pd.read_csv(URL_PROXIMOS)

        if df.empty:
            return ["No hay productos próximos"]

        mensajes = []
        bloque = ""

        for _, row in df.iterrows():
            codigo = str(row.iloc[0])
            material = str(row.iloc[1])

            linea = f"{codigo} - {material}\n------\n"

            if len(bloque + linea) > 4000:
                mensajes.append(bloque)
                bloque = linea
            else:
                bloque += linea

        if bloque:
            mensajes.append(bloque)

        return mensajes

    except Exception as e:
        return [f"Error PROXIMOS: {e}"]


# ================================
# 📋 MENÚ INLINE
# ================================
def menu_inline():
    keyboard = [
        [InlineKeyboardButton("🔴 Agotados", callback_data="agotados")],
        [InlineKeyboardButton("🟡 Próximo a vencer", callback_data="vencimientos")],
        [InlineKeyboardButton("🟠 Bajo inventario", callback_data="bajo")],
        [InlineKeyboardButton("🔄 Actualizar datos", callback_data="recargar")],
        [InlineKeyboardButton("❌ Salir", callback_data="salir")]
    ]
    return InlineKeyboardMarkup(keyboard)


# ================================
# 🚀 START
# ================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Soy Marbell-Lee*\n"
        "🤖 Asistente Virtual Pozuelo\n\n"
        "Selecciona una opción:",
        reply_markup=menu_inline(),
        parse_mode="Markdown"
    )

# ================================
# 🔘 BOTONES
# ================================
async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # 🔴 AGOTADOS
    if data == "agotados":
        mensajes = obtener_agotados()
        await query.message.reply_text("🔴 Productos agotados:\n")

        for msg in mensajes:
            await query.message.reply_text(msg)

    # 🟡 PROXIMOS
    elif data == "vencimientos":
        mensajes = obtener_proximos()
        await query.message.reply_text("🟡 Próximo a vencerse:\n")

        for msg in mensajes:
            await query.message.reply_text(msg)

    # 🟠 BAJO INVENTARIO (EN CONSTRUCCIÓN)
    elif data == "bajo":
        await query.message.reply_text(
            "🟠 Módulo de bajo inventario en construcción 🚧\n\n"
            "Próximamente disponible."
        )

    # 🔄 RECARGAR
    elif data == "recargar":
        await query.message.reply_text("🔄 Datos actualizados desde Google Sheets")

    # ❌ SALIR
    elif data == "salir":
        await query.message.reply_text(
            "👋 Sesión finalizada.\nEscribe /start para volver."
        )
        return

    # 🔁 VOLVER AL MENÚ
    await query.message.reply_text(
        "¿Qué deseas hacer ahora?",
        reply_markup=menu_inline()
    )


# ================================
# ▶️ MAIN
# ================================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(botones))

    print("✅ Bot PRO con Google Sheets corriendo...")
    app.run_polling()
