
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
import random
import string
import os

PREFIXO, TAMANHO, QUANTIDADE = range(3)

def gerar_codiguin(prefixo, tamanho_total):
    sufixo_len = tamanho_total - len(prefixo)
    sufixo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=sufixo_len))
    return prefixo + sufixo

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [[InlineKeyboardButton("Iniciar Geração", callback_data="start_gerar")]]
    await update.message.reply_text("Use o menu para selecionar uma opção.", reply_markup=InlineKeyboardMarkup(teclado))

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("👋 Envie o prefixo para os codiguins (ex: DSZNX, CNDMD):")
    return PREFIXO

async def receber_prefixo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prefixo = update.message.text.strip().upper()
    if len(prefixo) < 3 or len(prefixo) > 6:
        await update.message.reply_text("❌ Prefixo deve ter entre 3 e 6 caracteres. Tente novamente:")
        return PREFIXO
    context.user_data['prefixo'] = prefixo

    teclado = [
        [InlineKeyboardButton("12 caracteres", callback_data="12")],
        [InlineKeyboardButton("16 caracteres", callback_data="16")],
    ]
    await update.message.reply_text("Escolha o tamanho total do código:", reply_markup=InlineKeyboardMarkup(teclado))
    return TAMANHO

async def receber_tamanho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tamanho = int(query.data)
    context.user_data['tamanho'] = tamanho

    teclado = [
        [InlineKeyboardButton("5 códigos", callback_data="5"),
         InlineKeyboardButton("10 códigos", callback_data="10"),
         InlineKeyboardButton("20 códigos", callback_data="20")]
    ]
    await query.message.reply_text("Escolha a quantidade de codiguins:", reply_markup=InlineKeyboardMarkup(teclado))
    return QUANTIDADE

async def receber_quantidade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    quantidade = int(query.data)

    prefixo = context.user_data['prefixo']
    tamanho = context.user_data['tamanho']

    codigos = [gerar_codiguin(prefixo, tamanho) for _ in range(quantidade)]
    resposta = "\n".join(codigos)

    await query.message.reply_text(f"🎉 Aqui estão seus codiguins:\n\n{resposta}")
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operação cancelada.")
    return ConversationHandler.END

if __name__ == "__main__":
    TOKEN = os.environ.get("7740021136:AAG4rvpPULOHacxeICGDoflrHFidiE_SZB0")
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CallbackQueryHandler(menu, pattern="^start_gerar$")],
        states={
            PREFIXO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_prefixo)],
            TAMANHO: [CallbackQueryHandler(receber_tamanho, pattern="^(12|16)$")],
            QUANTIDADE: [CallbackQueryHandler(receber_quantidade, pattern="^(5|10|20)$")],
        },
        fallbacks=[CommandHandler("cancel", cancelar)],
    )

    app.add_handler(conv_handler)
    print("🤖 Bot rodando...")
    app.run_polling()
