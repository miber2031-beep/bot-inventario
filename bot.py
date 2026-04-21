from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# =========================
# 🔹 CONFIGURACIÓN
# =========================

TOKEN = "TU_TOKEN_AQUI"
ITEMS_PER_PAGE = 10

# 🔹 DATOS (REEMPLAZA POR TU FUENTE REAL)
agotados = [f"Producto AGOTADO {i}" for i in range(1, 53)]
proximos = [f"Producto VENCER {i}" for i in range(1, 37)]


# =========================
# 🔹 MENÚ PRINCIPAL
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔴 Agotados", callback_data="menu_agotados")],
        [InlineKeyboardButton("🟡 Próximo a vencer", callback_data="menu_proximos")],
        [InlineKeyboardButton("❌ Cerrar", callback_data="close")]
    ]

    await update.message.reply_text(
        "📊 *Panel de Inventario*\n\nSelecciona una opción:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# =========================
# 🔹 PAGINADOR GENÉRICO
# =========================

def build_page(data_list, page, title, prefix):
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    items = data_list[start:end]

    text = f"{title} ({len(data_list)} productos)\n"
    text += f"📄 Página {page+1}\n\n"

    for i, item in enumerate(items, start=1):
        text += f"{start + i}. {item}\n"

    buttons = []

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton("⏮️", callback_data=f"{prefix}_{page-1}")
        )
    if end < len(data_list):
        nav_buttons.append(
            InlineKeyboardButton("⏭️", callback_data=f"{prefix}_{page+1}")
        )

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([
        InlineKeyboardButton("🔙 Menú", callback_data="menu"),
        InlineKeyboardButton("❌ Cerrar", callback_data="close")
    ])

    return text, InlineKeyboardMarkup(buttons)


# =========================
# 🔹 HANDLERS MENÚ
# =========================

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔴 Agotados", callback_data="menu_agotados")],
        [InlineKeyboardButton("🟡 Próximo a vencer", callback_data="menu_proximos")],
        [InlineKeyboardButton("❌ Cerrar", callback_data="close")]
    ]

    await query.edit_message_text(
        "📊 *Panel de Inventario*\n\nSelecciona una opción:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def agotados_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    page = 0
    text, keyboard = build_page(agotados, page, "🔴 AGOTADOS", "agotados")

    await query.edit_message_text(text, reply_markup=keyboard)


async def proximos_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    page = 0
    text, keyboard = build_page(proximos, page, "🟡 PRÓXIMOS A VENCER", "proximos")

    await query.edit_message_text(text, reply_markup=keyboard)


# =========================
# 🔹 PAGINACIÓN
# =========================

async def pagination_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("agotados_"):
        page = int(data.split("_")[1])
        text, keyboard = build_page(agotados, page, "🔴 AGOTADOS", "agotados")

    elif data.startswith("proximos_"):
        page = int(data.split("_")[1])
        text, keyboard = build_page(proximos, page, "🟡 PRÓXIMOS A VENCER", "proximos")

    else:
        return

    await query.edit_message_text(text, reply_markup=keyboard)


# =========================
# 🔹 CERRAR
# =========================

async def close_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("✅ Sesión finalizada")


# =========================
# 🔹 APP
# =========================

def main():
    app = Application.builder().token(TOKEN).build()

    # comandos
    app.add_handler(CommandHandler("start", start))

    # menú
    app.add_handler(CallbackQueryHandler(menu_handler, pattern="^menu$"))
    app.add_handler(CallbackQueryHandler(agotados_handler, pattern="^menu_agotados$"))
    app.add_handler(CallbackQueryHandler(proximos_handler, pattern="^menu_proximos$"))

    # paginación
    app.add_handler(CallbackQueryHandler(pagination_handler, pattern="^(agotados|proximos)_"))

    # cerrar
    app.add_handler(CallbackQueryHandler(close_handler, pattern="^close$"))

    app.run_polling()


if __name__ == "__main__":
    main()
