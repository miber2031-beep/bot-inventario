import pandas as pd
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ================================
# 🔑 TOKEN (VARIABLE DE ENTORNO)
# ================================
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ TOKEN no configurado en Railway")

# ================================
# 🌐 GOOGLE SHEETS
# ================================
URL_AGOTADOS = "https://docs.google.com/spreadsheets/d/1xNOPwkbunW1-9_wDIb7PwbdBn6oLvDGZZKnWVnhJJO4/gviz/tq?tqx=out:csv&gid=0"
URL_PROXIMOS = "https://docs.google.com/spreadsheets/d/1xNOPwkbunW1-9_wDIb7PwbdBn6oLvDGZZKnWVnhJJO4/gviz/tq?tqx=out:csv&gid=462007210"

# ================================
# 🔴 AGOTADOS
# ================================
def obtener_agotados():
    try:
        print("🔄 Consultando AGOTADOS...")
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
        print("❌ Error AGOTADOS:", e)
        return ["❌ Error consultando productos agotados"]

# ================================
# 🟡 PRÓXIMOS
# ================================
def obtener_proximos():
    try:
        print("🔄 Consultando PROXIMOS...")
        df = pd.read_csv(URL_PROXIMOS)

        if df.empty:
            return ["No hay productos próximos a vencer"]

        mensajes = []
        bloque = ""

        for _, row in df.iterrows():
            codigo = str(row.iloc[0])
            material = str(row.iloc[1])

            linea = f"🟡 {codigo}\n📦 {material}\n⏳ Próximo a vencer\n────────────\n"

            if len(bloque + linea) > 4000:
                mensajes.append(bloque)
                bloque = linea
            else:
                bloque += linea

        if bloque:
            mensajes.append(bloque)

        return mensajes

    except Exception as e:
        print("❌ Error PROXIMOS:", e)
        return ["❌ Error consultando productos próximos"]

# ================================
# 📋 MENÚ
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
        "👋 *Hola ... soy MARBELL-LEE*\n"
        "🤖 Tu Asistente Virtual Pozuelo\n\n"
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

    try:
        if data == "agotados":
            mensajes = obtener_agotados()
            await query.message.reply_text("🔴 *PRODUCTOS AGOTADOS*\n", parse_mode="Markdown")

            for msg in mensajes:
                await query.message.reply_text(msg)

        elif data == "vencimientos":
            mensajes = obtener_proximos()
            await query.message.reply_text("🟡 *PRÓXIMOS A VENCER*\n", parse_mode="Markdown")

            for msg in mensajes:
                await query.message.reply_text(msg)

        elif data == "bajo":
            await query.message.reply_text(
                "🟠 Módulo de bajo inventario en construcción 🚧"
            )

        elif data == "recargar":
            await query.message.reply_text("🔄 Datos actualizados correctamente")

        elif data == "salir":
            await query.message.reply_text(
                "👋 Sesión finalizada.\nEscribe /start para volver."
            )
            return

        await query.message.reply_text(
            "¿Qué deseas hacer ahora?",
            reply_markup=menu_inline()
        )

    except Exception as e:
        print("💥 Error en botones:", e)
        await query.message.reply_text("❌ Ocurrió un error interno.")

# ================================
# ▶️ MAIN
# ================================
if __name__ == "__main__":
    try:
        print("🚀 Iniciando bot...")

        app = ApplicationBuilder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(botones))

        print("✅ Bot corriendo en Railway...")
        app.run_polling()

    except Exception as e:
        print("💥 ERROR CRÍTICO:", e)
