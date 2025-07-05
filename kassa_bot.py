import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

WEIGHT, RATE, EXCHANGE, DUTY = range(4)

VAT_PERCENT = 12
FIXED_FEE = 23592

def start(update, context):
    update.message.reply_text("Введите вес товара (в кг):")
    return WEIGHT

def weight_input(update, context):
    context.user_data['weight'] = float(update.message.text.replace(',', '.'))
    update.message.reply_text("Введите ставку (цена за 1 кг в долларах):")
    return RATE

def rate_input(update, context):
    context.user_data['rate'] = float(update.message.text.replace(',', '.'))
    update.message.reply_text("Введите текущий курс доллара (в тенге):")
    return EXCHANGE

def exchange_input(update, context):
    context.user_data['exchange'] = float(update.message.text.replace(',', '.'))
    update.message.reply_text("Введите процент пошлины (например, 5):")
    return DUTY

def duty_input(update, context):
    weight = context.user_data['weight']
    rate = context.user_data['rate']
    exchange = context.user_data['exchange']
    duty_percent = float(update.message.text.replace(',', '.'))

    price_usd = weight * rate
    price_kzt = price_usd * exchange

    vat = price_kzt * (VAT_PERCENT / 100)
    duty = price_kzt * (duty_percent / 100)

    total_price = vat + duty + FIXED_FEE  # Без стоимости товара

    update.message.reply_text(
        f"Расчёт завершён ✅\n\n"
        f"НДС (12%): {vat:.2f} тг\n"
        f"Пошлина ({duty_percent}%): {duty:.2f} тг\n"
        f"Сбор: {FIXED_FEE} тг\n\n"
        f"Итоговая стоимость: {total_price:.2f} тг"
    )

    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text('Операция отменена.')
    return ConversationHandler.END

def main():
    updater = Updater(os.getenv("BOT_TOKEN"), use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WEIGHT: [MessageHandler(Filters.text & ~Filters.command, weight_input)],
            RATE: [MessageHandler(Filters.text & ~Filters.command, rate_input)],
            EXCHANGE: [MessageHandler(Filters.text & ~Filters.command, exchange_input)],
            DUTY: [MessageHandler(Filters.text & ~Filters.command, duty_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    
if __name__ == '__main__':
    main()

