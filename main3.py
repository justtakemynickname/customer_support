import telebot
from transformers import pipeline
import whisper
from PIL import Image
import torch
import easyocr
from io import BytesIO

# Telegram bot token
TOKEN = '7627248525:AAGd-xuC9mfvic-gARxV8cNUUKi6VpKeXO4'
bot = telebot.TeleBot(TOKEN)

# Models initialization
nlp_model = pipeline("sentiment-analysis")  # Text sentiment analysis
whisper_model = whisper.load_model("base")  # Speech-to-text model
yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)  # Object detection
ocr_reader = easyocr.Reader(['en', 'ru'])  # OCR for English and Russian

# User data dictionary
user_data = {}


# Function to request user's full name (FIO)
def request_fio(chat_id):
    bot.send_message(chat_id, "Пожалуйста, введите ваши ФИО для продолжения.")
    user_data[chat_id] = {"state": "waiting_for_fio"}


# Function to display the main menu
def show_main_menu(chat_id, fio):
    reply = (
        f"Добро пожаловать, {fio}!\n"
        "Выберите одну из опций:\n"
        "1. Оформить кредит\n"
        "2. Пополнить счёт\n"
        "3. Перевод средств\n"
        "4. Оформить банковскую карту\n"
        "5. Изменить личные данные\n"
        "6. Информация о счетах\n"
        "7. Распознавание документов\n"
        "8. Выйти"
    )
    bot.send_message(chat_id, reply)
    user_data[chat_id]["state"] = "main_menu"


# Handle text messages
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    user_text = message.text.strip().lower()

    # Ensure user data is initialized
    if chat_id not in user_data:
        request_fio(chat_id)
        return

    state = user_data[chat_id].get("state")

    # Handle user FIO input
    if state == "waiting_for_fio":
        user_data[chat_id]["fio"] = message.text.strip().title()
        show_main_menu(chat_id, user_data[chat_id]["fio"])
        return

    # Main menu options
    if state == "main_menu":
        process_main_menu(chat_id, user_text)
        return

    # Handle specific states
    handlers = {
        "awaiting_credit_amount": process_credit,
        "awaiting_deposit_method": process_deposit_method,
        "awaiting_transfer_method": process_transfer_method,
        "awaiting_account_number": process_account_number,
        "awaiting_phone_number": process_phone_number,
        "awaiting_transfer_amount": process_transfer_amount,
        "awaiting_card_type": process_card_type,
    }

    if state in handlers:
        handlers[state](chat_id, user_text)
    else:
        bot.send_message(chat_id, "Произошла ошибка. Пожалуйста, начните с команды 'меню'.")


# Handle main menu options
def process_main_menu(chat_id, user_text):
    fio = user_data[chat_id]["fio"]
    options = {
        "1": ("Пожалуйста, введите желаемую сумму кредита.", "awaiting_credit_amount"),
        "2": ("Для пополнения счёта выберите метод:\n1. Банковская карта\n2. Перевод с другого счёта\n3. Пополнение через отделение", "awaiting_deposit_method"),
        "3": ("Для перевода средств выберите опцию:\n1. На другой счёт в нашем банке\n2. На счёт в другом банке\n3. Мгновенный перевод по номеру телефона", "awaiting_transfer_method"),
        "4": ("Отлично! Пожалуйста, выберите тип карты:\n1. Дебетовая\n2. Кредитная", "awaiting_card_type"),
        "5": ("Для изменения личных данных выберите:\n1. ФИО\n2. Номер телефона\n3. Адрес", "awaiting_personal_data_change"),
        "6": (f"Ваши текущие счета, {fio}:\n1. Основной счёт: 100,000 руб.\n2. Сберегательный счёт: 250,000 руб.\n3. Кредитный счёт: -50,000 руб.", None),
        "7": ("Пожалуйста, отправьте документ для распознавания.", "awaiting_document_upload"),
        "8": ("Спасибо, что воспользовались нашим ботом! До свидания.", None),
    }

    if user_text in options:
        response, next_state = options[user_text]
        bot.send_message(chat_id, response)

        if next_state:
            user_data[chat_id]["state"] = next_state
        elif user_text == "7":
            bot.send_message(chat_id, "Пожалуйста, загрузите изображение документа для распознавания.")
            user_data[chat_id]["state"] = "awaiting_document_upload"

        elif user_text == "8":
            del user_data[chat_id]

    else:
        bot.send_message(chat_id, "Пожалуйста, выберите действительный номер из меню.")


# Process credit requests
def process_credit(chat_id, user_text):
    try:
        amount = float(user_text)
        fio = user_data[chat_id]["fio"]
        bot.send_message(chat_id, f"{fio}, ваш запрос на кредит на сумму {amount} руб. успешно оформлен.")
        show_main_menu(chat_id, fio)
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите корректную сумму.")


# Handle deposit method
def process_deposit_method(chat_id, user_text):
    methods = {"1": "Банковская карта", "2": "Перевод с другого счёта", "3": "Пополнение через отделение"}
    if user_text in methods:
        fio = user_data[chat_id]["fio"]
        bot.send_message(chat_id, f"{fio}, пополнение через '{methods[user_text]}' успешно выполнено.")
        show_main_menu(chat_id, fio)
    else:
        bot.send_message(chat_id, "Пожалуйста, выберите действительный метод пополнения.")


# Handle transfer options
def process_transfer_method(chat_id, user_text):
    methods = {"1": "На другой счёт в нашем банке", "2": "На счёт в другом банке", "3": "Мгновенный перевод по номеру телефона"}
    if user_text in methods:
        user_data[chat_id]["transfer_method"] = methods[user_text]
        next_prompt = "Введите номер телефона для перевода." if user_text == "3" else "Введите номер счёта для перевода."
        bot.send_message(chat_id, next_prompt)
        user_data[chat_id]["state"] = "awaiting_phone_number" if user_text == "3" else "awaiting_account_number"
    else:
        bot.send_message(chat_id, "Пожалуйста, выберите допустимую опцию перевода.")


# Handle account number input
def process_account_number(chat_id, user_text):
    user_data[chat_id]["account_number"] = user_text
    bot.send_message(chat_id, "Введите сумму для перевода.")
    user_data[chat_id]["state"] = "awaiting_transfer_amount"


# Handle phone number input
def process_phone_number(chat_id, user_text):
    user_data[chat_id]["phone_number"] = user_text
    bot.send_message(chat_id, "Введите сумму для перевода.")
    user_data[chat_id]["state"] = "awaiting_transfer_amount"


# Handle transfer amount
def process_transfer_amount(chat_id, user_text):
    try:
        amount = float(user_text)
        fio = user_data[chat_id]["fio"]
        target = user_data[chat_id].get("phone_number") or user_data[chat_id].get("account_number")
        transfer_type = "номер телефона" if "phone_number" in user_data[chat_id] else "счёт"
        bot.send_message(chat_id, f"{fio}, перевод на сумму {amount} руб. на {transfer_type} {target} успешно выполнен.")
        show_main_menu(chat_id, fio)
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите корректную сумму.")


# Process card type selection
def process_card_type(chat_id, user_text):
    card_types = {"1": "Дебетовая", "2": "Кредитная"}
    if user_text in card_types:
        fio = user_data[chat_id]["fio"]
        bot.send_message(chat_id, f"{fio}, ваша заявка на оформление {card_types[user_text]} карты успешно принята.")
        show_main_menu(chat_id, fio)
    else:
        bot.send_message(chat_id, "Пожалуйста, выберите допустимый тип карты.")

# Handle document (photo) uploads
@bot.message_handler(content_types=['photo'])
def handle_document_upload(message):
    chat_id = message.chat.id
    if chat_id not in user_data or user_data[chat_id].get("state") != "awaiting_document_upload":
        bot.send_message(chat_id, "Пожалуйста, выберите опцию распознавания документов в меню, чтобы загрузить файл.")
        return

    bot.send_message(chat_id, "Документ получен, обработка началась...")

    # Get the highest-resolution photo file
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    try:
        # Load the image into memory
        image = Image.open(BytesIO(downloaded_file))

        # Perform text recognition with EasyOCR
        text_results = ocr_reader.readtext(image, detail=0)

        # Perform object detection with YOLOv5
        yolo_results = yolo_model(image)

        # Generate response
        text_response = "Распознанный текст:\n" + "\n".join(text_results) if text_results else "Текст не найден."
        yolo_response = "Обнаруженные объекты:\n" + "\n".join([f"{x['name']} ({x['confidence']:.2%})" for x in yolo_results.pandas().xyxy[0].to_dict('records')]) if not yolo_results.pandas().xyxy[0].empty else "Объекты не найдены."

        # Send responses to the user
        bot.send_message(chat_id, text_response)
        bot.send_message(chat_id, yolo_response)

    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка при обработке документа: {str(e)}")
    finally:
        # Return to main menu after processing
        show_main_menu(chat_id, user_data[chat_id]["fio"])

# Run the bot
bot.polling(none_stop=True)
