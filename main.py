# TELEBOT IMPORT
import telebot
from telebot import types
import database
from database import *
import threading
import string
import random

#API TOKEN
API_TOKEN = 'API_TOKEN_HERE'

bot = telebot.TeleBot(API_TOKEN)

def database_worker():
    global conn
    conn = database.create_connection()

db_thread = threading.Thread(target=database_worker)
db_thread.start()
db_thread.join()

# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_settings = database.UserSettings(message.from_user.id)
    insert_user(conn, message.from_user.id, user_settings.user_length, user_settings.use_letters, user_settings.use_digits, user_settings.use_punctuation)
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Генерировать пароль")
    item2=types.KeyboardButton("Настройки генерации")
    markup.add(item1)
    markup.add(item2)
    bot.reply_to(message, "Привет, я - бот генератор сложных паролей.", reply_markup=markup)

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Это бот для генерации сложных паролей. Используйте команду /start для начала работы.")

@bot.message_handler(content_types='text')
def message_reply(message):
    global user_settings, use_letters, use_digits, use_punctuation, password_length_to_int

    user_settings = database.UserSettings(message.from_user.id)
    use_letters = user_settings.use_letters
    use_digits = user_settings.use_digits
    use_punctuation = user_settings.use_punctuation
    password_length_to_int = user_settings.user_length

    if message.text=="Генерировать пароль":
        try:
            bot.send_message(message.chat.id, "Сгенерирован пароль: " + generate_password(user_settings))
        except Exception as e:
            print(e)
    elif message.text=="Настройки генерации":
        create_settings_keyboard(message, user_settings)
        bot.reply_to(message, "Нажмите для изменения настройки", reply_markup=settings_markup)
        bot.send_message(message.chat.id, f"""Длина пароля: {password_length_to_int}
Использование букв: {'✅' if use_letters else '❌'}
Использование цифр: {'✅' if use_digits else '❌'}
Использование спец. символов: {'✅' if use_punctuation else '❌'}""")

    elif message.text=="Изменить длину пароля":
        bot.send_message(message.chat.id, "Введите длину пароля")
        bot.register_next_step_handler(message, length_change)
    elif message.text == f"Использование букв: {'✅' if user_settings.use_letters else '❌'} -> {'❌' if user_settings.use_letters else '✅'}":
        change_use_letters(message)
    elif message.text == f"Использование цифр: {'✅' if user_settings.use_digits else '❌'} -> {'❌' if user_settings.use_digits else '✅'}":
        change_use_digits(message)
    elif message.text == f"Использование спец. символов: {'✅' if user_settings.use_punctuation else '❌'} -> {'❌' if user_settings.use_punctuation else '✅'}":
        change_use_punctuation(message)
    elif message.text == "get_all_users":
        rows = f"{get_all_users(conn)}"
        bot.send_message(message.chat.id, rows)
    elif message.text=="Главное меню":
        home_keyboard(message)

def length_change(message):
    password_length = message.text
    try:
        password_length_to_int = int(password_length)
        print(f"LOG | {message.from_user.id}/{message.from_user.first_name} {message.from_user.last_name} | Set password_length: {password_length_to_int}.")
        bot.send_message(message.chat.id, "Длина пароля установлена: " + password_length)
        user_settings = database.UserSettings(message.from_user.id)
        user_settings.use_length = password_length_to_int
        # Обновляем запись в базе данных
        update_user_settings(conn, message.from_user.id, password_length_to_int, use_letters=use_letters, use_digits=use_digits, use_punctuation=use_punctuation)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Длина пароля может быть только целым числом! Вы ввели: " + str(type(password_length)))
        bot.register_next_step_handler(message, length_change)

def change_use_letters(message):
    user_settings = database.UserSettings(message.from_user.id)
    user_settings.use_letters = not user_settings.use_letters  # Изменяем значение на противоположное
    update_user_settings(conn, message.from_user.id, user_settings.user_length, use_letters=user_settings.use_letters, use_digits=user_settings.use_digits, use_punctuation=user_settings.use_punctuation)
    create_settings_keyboard(message, user_settings)  # Передаем объект user_settings в функцию create_settings_keyboard

    bot.send_message(message.chat.id, f"Использование цифр: {'✅' if user_settings.use_letters else '❌'}", reply_markup=settings_markup)
    print(f"LOG | {message.from_user.id}/{message.from_user.first_name} {message.from_user.last_name} | Letters turn {'on' if user_settings.use_letters else 'off'}.")

def change_use_punctuation(message):
    user_settings = database.UserSettings(message.from_user.id)
    user_settings.use_punctuation = 1 if user_settings.use_punctuation == 0 else 0
    update_user_settings(conn, message.from_user.id, user_settings.user_length, use_letters=user_settings.use_letters, use_digits=user_settings.use_digits, use_punctuation=user_settings.use_punctuation)
    create_settings_keyboard(message, user_settings)  # Передаем объект user_settings в функцию create_settings_keyboard

    bot.send_message(message.chat.id, f"Использование спец. символов: {'✅' if user_settings.use_punctuation else '❌'}", reply_markup=settings_markup)
    print(f"LOG | {message.from_user.id}/{message.from_user.first_name} {message.from_user.last_name} | Punctuation turn {'on' if user_settings.use_punctuation else 'off'}.")

def change_use_digits(message):
    user_settings = database.UserSettings(message.from_user.id)
    user_settings.use_digits = not user_settings.use_digits  # Изменяем значение на противоположное
    update_user_settings(conn, message.from_user.id, user_settings.user_length, use_letters=user_settings.use_letters, use_digits=user_settings.use_digits, use_punctuation=user_settings.use_punctuation)
    create_settings_keyboard(message, user_settings)  # Передаем объект user_settings в функцию create_settings_keyboard

    bot.send_message(message.chat.id, f"Использование цифр: {'✅' if user_settings.use_digits else '❌'}", reply_markup=settings_markup)
    print(f"LOG | {message.from_user.id}/{message.from_user.first_name} {message.from_user.last_name} | digits turn {'on' if user_settings.use_digits else 'off'}.")

def home_keyboard(message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Генерировать пароль")
    item2=types.KeyboardButton("Настройки генерации")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(message.chat.id, "Главное меню", reply_markup=markup)

def create_settings_keyboard(message, user_settings):
    global settings_markup, settings_item1, settings_item2, settings_item3, settings_item4, settings_home

    settings_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    settings_item1 = types.KeyboardButton("Изменить длину пароля")
    settings_markup.add(settings_item1)
    
    # Использование букв
    settings_item2_text = f"Использование букв: {'✅' if user_settings.use_letters else '❌'} -> {'✅' if not user_settings.use_letters else '❌'}"
    settings_item2 = types.KeyboardButton(settings_item2_text)
    settings_markup.add(settings_item2)
    
    # Использование цифр
    settings_item3_text = f"Использование цифр: {'✅' if user_settings.use_digits else '❌'} -> {'❌' if user_settings.use_digits else '✅'}"
    settings_item3 = types.KeyboardButton(settings_item3_text)
    settings_markup.add(settings_item3)
    
    # Использование спец. символов
    settings_item4_text = f"Использование спец. символов: {'✅' if user_settings.use_punctuation else '❌'} -> {'❌' if user_settings.use_punctuation else '✅'}"
    settings_item4 = types.KeyboardButton(settings_item4_text)
    settings_markup.add(settings_item4)
    
    # Кнопка для возврата в главное меню
    settings_home = types.KeyboardButton("Главное меню")
    settings_markup.add(settings_home)



def generate_password(user_settings):
    length = user_settings.user_length

    characters = ''
    if user_settings.use_letters:
        characters += string.ascii_letters
    if user_settings.use_digits:
        characters += string.digits
    if user_settings.use_punctuation:
        characters += string.punctuation

    if not characters:
        raise ValueError("Невозможно создать пароль: отсутствуют символы для генерации")

    password = ''.join(random.choice(characters) for _ in range(length))
    return password



bot.infinity_polling()
