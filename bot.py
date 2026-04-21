import pandas as pd
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN") or "8671710771:AAFS7WdDTq3Wlx6cC80NGRLVLMdKzzeTW1M"

URL_AGOTADOS = "https://docs.google.com/spreadsheets/d/1xNOPwkbunW1-9_wDIb7PwbdBn6oLvDGZZKnWVnhJJO4/gviz/tq?tqx=out:csv&gid=0"
URL_PROXIMOS = "https://docs.google.com/spreadsheets/d/1xNOPwkbunW1-9_wDIb7PwbdBn6oLvDGZZKnWVnhJJO4/gviz/tq?tqx=out:csv&gid=462007210"

ITEMS_PER_PAGE = 5

# ================================
# 🔹 CARGAR DATOS
# ================================
def cargar_agotados():
    df = pd.read_csv(URL_AGOTADOS)
    return df.fillna("").values.tolist()

def cargar_proximos():
    df = pd.read_csv(URL_PROXIMOS)
    return df.fillna("").values.tolist()

# ================================
# 🔹 PAGINADOR
# ================================
def construir_pagina(data, page, tipo):
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    items = data[start:end]

    titulo = "🔴 AGOTADOS" if tipo == "agotados" else "🟡 PRÓXIMOS A VENCER"

    texto = f"{titulo}\n📄 Página {page+1}\n\n"

    for i, row in enumerate(items, start=1):
        codigo = row[0]
        material = row[1]

        if tipo == "agotados":
            estado = row[2]
            texto += f"{start+i}. 🔴 {codigo}\n📦 {material}\n📌 {estado}\n──────────\n"
        else:
            texto += f"{start+i}. 🟡 {codigo}\n📦 {material}\n⏳ Próximo\n──────────\n"

    botones = []

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⏮️", callback_data=f"{tipo}_{page-1}"))
    if end < len(data):
        nav.append(InlineKeyboardButton("⏭️", callback_data=f"{tipo}_{page+1}"))

    if nav:
        botones.append(nav)

    botones.append([
        InlineKeyboardButton("🔙 Menú", callback_data="menu"),
        InlineKeyboardButton("❌ Salir", callback_data="salir")
    ])

    return texto, InlineKeyboardMarkup(botones)

# ================================
# 📋 MENÚ
# ================================
def menu_inline():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 Agotados", callback_data="menu_agotados")],
        [InlineKeyboardButton("🟡 Próximo a vencer", callback_data="menu_proximos")],
        [InlineKeyboardButton("🟠 Bajo inventario", callback_data="bajo")],
        [InlineKeyboardButton("🔄 Actualizar datos", callback_data="recargar")],
        [InlineKeyboardButton("❌ Salir", callback_data="salir")]
    ])

# ================================
# 🚀 START
# ================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Hola ... soy MARBELL-LEE!!!*\n🤖 Tu Asistente Virtual Pozuelo\n\nSelecciona una opción:",
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

    # MENÚ
    if data == "menu":
        await query.edit_message_text("📊 Panel de opciones:", reply_markup=menu_inline())
        return

    # 🔴 AGOTADOS
    if data == "menu_agotados":
        data_list = cargar_agotados()
        text, kb = construir_pagina(data_list, 0, "agotados")
        await query.edit_message_text(text, reply_markup=kb)
        return

    # 🟡 PROXIMOS
    if data == "menu_proximos":
        data_list = cargar_proximos()
        text, kb = construir_pagina(data_list, 0, "proximos")
        await query.edit_message_text(text, reply_markup=kb)
        return

    # 🔄 PAGINACIÓN
    if data.startswith("agotados_"):
        page = int(data.split("_")[1])
        data_list = cargar_agotados()
        text, kb = construir_pagina(data_list, page, "agotados")
        await query.edit_message_text(text, reply_markup=kb)
        return

    if data.startswith("proximos_"):
        page = int(data.split("_")[1])
        data_list = cargar_proximos()
        text, kb = construir_pagina(data_list, page, "proximos")
        await query.edit_message_text(text, reply_markup=kb)
        return

    # 🟠 BAJO
    if data == "bajo":
        await query.edit_message_text("🟠 Módulo en construcción 🚧")
        return

    # 🔄 RECARGAR
    if data == "recargar":
        await query.answer("Datos actualizados ✔", show_alert=True)
        return

    # ❌ SALIR
    if data == "salir":
        await query.edit_message_text("👋 Sesión finalizada")
        return


# ================================
# ▶️ MAIN
# ================================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(botones))

    print("✅ Bot PRO con paginación corriendo...")
    app.run_polling()
