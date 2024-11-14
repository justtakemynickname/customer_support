import telebot
import torch
import whisper
from transformers import pipeline
from io import BytesIO

# Телеграм токен бота
TOKEN = '7973043724:AAE_idq12mkSXqo6w3Hk_1ad2pemCMROfIs'
bot = telebot.TeleBot(TOKEN)

# Модель для анализа настроения текста
nlp_model = pipeline("sentiment-analysis")

# Модель Whisper для распознавания речи
whisper_model = whisper.load_model("base")  # Можно выбрать другие версии: "small", "medium", "large"

# Словарь для хранения данных пользователя
user_data = {}

# Функция для запроса ФИО
def request_fio(chat_id):
    bot.send_message(chat_id, "Пожалуйста, введите ваши ФИО для продолжения.")
    user_data[chat_id] = {"state": "waiting_for_fio"}

# Основное меню бота
def show_main_menu(chat_id, fio):
    reply = (
        f"Добро пожаловать, {fio}!\n"
        "Выберите одну из опций, отправив текст:\n"
        "1. Оформить кредит\n"
        "2. Пополнить счёт\n"
        "3. Перевод средств\n"
        "4. Оформить банковскую карту\n"
        "5. Изменить личные данные\n"
        "6. Информация о счетах\n"
        "7. Выйти"
    )
    bot.send_message(chat_id, reply)
    user_data[chat_id]["state"] = "main_menu"

# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    user_text = message.text.lower().strip()  # Приводим текст к нижнему регистру и удаляем пробелы
    print(f"Полученное сообщение от {chat_id}: {user_text}")  # Отладочное сообщение

    # Проверка состояния пользователя
    if chat_id not in user_data:
        # Если пользователь новый, запросить ФИО
        request_fio(chat_id)
        return

    # Получаем текущее состояние пользователя
    state = user_data[chat_id].get("state")

    # Обработка ФИО
    if state == "waiting_for_fio":
        # Сохраняем ФИО и показываем меню
        user_data[chat_id]["fio"] = message.text.strip().title()  # Сохраняем с заглавными буквами
        show_main_menu(chat_id, user_data[chat_id]["fio"])
        return

    # Основное меню
    if state == "main_menu":
        if "оформить кредит" in user_text or "кредит" in user_text:
            bot.send_message(chat_id, "Пожалуйста, введите желаемую сумму кредита.")
            user_data[chat_id]["state"] = "awaiting_credit_amount"
        elif "пополнить" in user_text or "внести деньги" in user_text:
            reply = (
                "Для пополнения счёта выберите метод:\n"
                "1. Банковская карта\n"
                "2. Перевод с другого счёта\n"
                "3. Пополнение через отделение\n"
                "Напишите нужный вариант."
            )
            bot.send_message(chat_id, reply)
            user_data[chat_id]["state"] = "awaiting_deposit_method"
        elif "перевод средств" in user_text or "перевод" in user_text:
            reply = (
                "Для перевода средств выберите опцию:\n"
                "1. На другой счёт в нашем банке\n"
                "2. На счёт в другом банке\n"
                "3. Мгновенный перевод по номеру телефона\n"
                "Напишите нужный вариант."
            )
            bot.send_message(chat_id, reply)
            user_data[chat_id]["state"] = "awaiting_transfer_method"
        elif "банковская карта" in user_text:
            bot.send_message(chat_id, "Отлично! Пожалуйста, выберите тип карты:\n1. Дебетовая\n2. Кредитная")
            user_data[chat_id]["state"] = "awaiting_card_type"
        elif "изменить данные" in user_text:
            reply = (
                "Для изменения личных данных выберите:\n"
                "1. ФИО\n"
                "2. Номер телефона\n"
                "3. Адрес\n"
                "Пожалуйста, напишите нужный вариант."
            )
            bot.send_message(chat_id, reply)
            user_data[chat_id]["state"] = "awaiting_personal_data_change"
        elif "счета" in user_text:
            fio = user_data[chat_id]["fio"]
            reply = f"Ваши текущие счета, {fio}:\n1. Основной счёт: 100,000 руб.\n2. Сберегательный счёт: 250,000 руб.\n3. Кредитный счёт: -50,000 руб."
            bot.send_message(chat_id, reply)
        else:
            bot.send_message(chat_id, "Пожалуйста, выберите команду из меню. Напишите 'меню' для возврата.")

    # Обработка суммы кредита
    elif state == "awaiting_credit_amount":
        try:
            amount = float(user_text)
            user_data[chat_id]["credit_amount"] = amount
            fio = user_data[chat_id]["fio"]
            bot.send_message(chat_id, f"{fio}, ваш запрос на кредит на сумму {amount} руб. успешно оформлен.")
            show_main_menu(chat_id, fio)
        except ValueError:
            bot.send_message(chat_id, "Пожалуйста, введите корректную сумму.")

    # Обработка метода пополнения
    elif state == "awaiting_deposit_method":
        methods = {"1": "Банковская карта", "2": "Перевод с другого счёта", "3": "Пополнение через отделение"}
        if user_text in methods:
            method = methods[user_text]
            fio = user_data[chat_id]["fio"]
            bot.send_message(chat_id, f"{fio}, пополнение через '{method}' успешно оформлено.")
            show_main_menu(chat_id, fio)
        else:
            bot.send_message(chat_id, "Пожалуйста, выберите один из предложенных вариантов.")

    # Обработка метода перевода
    elif state == "awaiting_transfer_method":
        transfer_methods = {"1": "На другой счёт в нашем банке", "2": "На счёт в другом банке", "3": "По номеру телефона"}
        if user_text in transfer_methods:
            method = transfer_methods[user_text]
            fio = user_data[chat_id]["fio"]
            bot.send_message(chat_id, f"{fio}, перевод '{method}' успешно оформлен.")
            show_main_menu(chat_id, fio)
        else:
            bot.send_message(chat_id, "Пожалуйста, выберите один из предложенных вариантов.")

    # Обработка типа карты
    elif state == "awaiting_card_type":
        card_types = {"1": "Дебетовая", "2": "Кредитная"}
        if user_text in card_types:
            card_type = card_types[user_text]
            fio = user_data[chat_id]["fio"]
            bot.send_message(chat_id, f"{fio}, ваша {card_type} карта успешно оформлена.")
            show_main_menu(chat_id, fio)
        else:
            bot.send_message(chat_id, "Пожалуйста, выберите один из предложенных вариантов.")

# Основной запуск бота
bot.polling()
