# bot.py
import telebot
from telebot import types
from pdf_utils import get_pdf_data, compare_pdf_data
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Привет! Я бот для проверки оригинальности чеков Сбербанка и Т-Банка. "
                                        "Нажмите 'Проверить чек', чтобы начать.")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Проверить чек")
    markup.add(item1)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Проверить чек")
def check_receipt(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Сбербанк")
    item2 = types.KeyboardButton("Т-Банк")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Выберите банк:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Сбербанк", "Т-Банк"])
def receive_file(message):
    bank = message.text
    bot.send_message(message.chat.id, "Отправьте PDF файл чека:")
    bot.register_next_step_handler(message, handle_pdf_file, bank)

def handle_pdf_file(message, bank):
    if message.content_type == 'document':
        file_info = bot.get_file(message.document.file_id)
        file_path = bot.download_file(file_info.file_path)

        with open("received_receipt.pdf", 'wb') as f:
            f.write(file_path)

        pdf_data = get_pdf_data("received_receipt.pdf")
        result = compare_pdf_data(bank, pdf_data)
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте именно PDF файл.")

if __name__ == '__main__':
    bot.polling(none_stop=True)
