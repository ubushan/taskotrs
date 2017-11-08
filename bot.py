# -*- coding: utf-8 -*-
import telebot
from telebot import types
from datetime import datetime
from conf import base, mailsender, config
from flask import Flask, request
import os


bot = telebot.TeleBot(config.properties.TELEGRAM_BOT_TOKEN)
server = Flask(__name__)

# Chat ID
def getCID(message):
    return message.chat.id

# User ID
def getUID(message):
    return message.from_user.id


def log(message):
    date = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    if bool(message.from_user.last_name) and bool(message.from_user.first_name):
        string = (date + " NAME: " + message.from_user.first_name + ' '
          + message.from_user.last_name + " USER_ID: " + str(message.from_user.id) + " MESSAGE: " + message.text)
    else:
        string = (date + " NAME: " + message.from_user.first_name + " USER_ID: " + str(message.from_user.id)
          + " MESSAGE: " + message.text)
    f = open(config.properties.PATH + "log/bot.log", 'a')
    f.write(string + '\n')
    f.close()
    

@bot.message_handler(commands=['start', 'help', 'stop'])
def start(message):
    cid = getCID(message)
    check = base.findUid(message.from_user.id)
    if message.text == "/start":
        if message.from_user.id == check:
            text = "*Начать работу*\n\n" \
                   "ℹ️ Чтобы отправить письмо, используй команду /mail в формате:" \
                   "\n\n`/mail <ваш текст письма>`"
            log(message)
            bot.send_message(cid, text, parse_mode="Markdown")
        else:
            text = "*Прости, но я тебя не знаю.\n" \
                   "Я работаю только с доверенными пользователями!*\n\n" \
                   "ℹ️ Чтобы начать пользоваться ботом, отправь свой *UserID* администратору.\n\n" \
                   "Твой *UserID*: `" + str(message.from_user.id) + "`"
            log(message)
            bot.send_message(cid, text, parse_mode="Markdown")

    if message.text == "/help":
        text = "💡 *Помощь*\n\n" \
               "*MailSenderBot* отправитель писем в «Task OTRS».\n\n" \
               "ℹ️ Чтобы отправить письмо, используй команду /mail в формате:" \
               "\n\n`/mail <ваш текст письма>`\n\n" \
               "Если вдруг функционал бота тебе не доступен, узнай свой *UserID* используя команду " \
               "/whoami и передай его администратору для добавления в доверенные пользователи."
        log(message)
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

    if message.text == "/stop":
        text = "Уже уходишь? Ну пока :("
        log(message)
        bot.send_message(message.chat.id, text)


@bot.inline_handler(lambda query: len(query.query) > 0)
@bot.message_handler(commands=['mail'])
def subj(query):
    cid = getCID(query)
    msg = bot.send_message(cid, "🖌 Введите *тему* письма", parse_mode="Markdown")
    bot.register_next_step_handler(msg, body)

letter = {}


def body(message):
    cid = getCID(message)
    letter['subject'] = message.text
    msg = bot.send_message(cid, "📝 Введите *текст* письма", parse_mode="Markdown")
    bot.register_next_step_handler(msg, send)


@bot.inline_handler(lambda query: len(query.query) > 0)
def send(message):
    cid = getCID(message)
    letter['body'] = message.text
    subject = letter['subject']
    text = letter['body']
    check = base.findUid(message.from_user.id)
    if message.from_user.id == check:
        if bool(text) or bool(subject) == True:
            log(message)
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="📩 Отправить", callback_data='send')
            callback_button2 = types.InlineKeyboardButton(text="❌ Отмена", callback_data='cancel')
            keyboard.add(callback_button, callback_button2)
            bot.send_message(cid, "*Письмо сформированно!*\n\nТема: `%s`\nТекст: `%s`" % (subject, text),
                             parse_mode="Markdown", reply_markup=keyboard)
    else:
        text = "*Прости, но я тебя не знаю. Я работаю только с доверенными пользователями!*\n\n" \
               "ℹ️ Чтобы начать пользоваться ботом, отправь свой *UserID* администратору.\n\n" \
               "Твой *UserID:* `" + str(message.from_user.id) + "`"
        log(message)
        bot.send_message(cid, text, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "send":
            test = mailsender.send(getUID(call), letter['subject'], letter['body'])
            if test[0] == 1:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=test[1], parse_mode="Markdown")
            elif test[0] == 0:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=test[1], parse_mode="Markdown")
            elif test[0] == -1:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=test[1], parse_mode="Markdown")
            letter.clear()

        if call.data == "cancel":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="❌ *Отправка отменена!*\n\n"
                                           "ℹ Для смены адреса получателя используй команду в формате:\n"
                                           "`/change <e-mail address>`", parse_mode="Markdown")


@bot.message_handler(commands=['whoami'])
def whoami(message):
    cid = getCID(message)
    text = "Твой *UserID*: " + "`" + str(getUID(message)) + "`"
    log(message)
    bot.send_message(cid, text, parse_mode="Markdown")


@bot.message_handler(commands=['settings'])
def settings(message):
    cid = getCID(message)
    check = base.userType(message.from_user.id)
    if check == 'admin':
        text = "⚙ *Настройка бота*\n\n" \
               "Для настройки используйте команды:\n\n" \
               "/change `<user@host.ru>` - Сменить получателя\n" \
               "/adduser `<UserID>` - Добавить пользователя\n" \
               "/addadmin `<UserID>` - Добавить администратора\n" \
               "/deluser `<UserID>` - Удалить пользователя\n" \
               "/getlog - Получить свежий логфайл"
        log(message)
        bot.send_message(cid, text, parse_mode="Markdown")
    else:
        text = "⛔️ Настройки доступны только *администраторам*!"
        log(message)
        bot.send_message(cid, text, parse_mode="Markdown")


@bot.message_handler(commands=['adduser'])
def adduser(message):
    cid = getCID(message)
    check = base.userType(message.from_user.id)
    if check == 'admin':
        intext = base.check_data(message.text[9:])
        if bool(intext):
            log(message)
            bot.send_message(cid, base.addUser(intext, 'user'), parse_mode="Markdown")
        else:
            text = "*Добавление пользователя*\n\n" \
                   "ℹ️ Используй эту команду для добавления пользователя в доверенный лист, в формате:" \
                   "\n\n`/adduser <user_id>`"
            log(message)
            bot.send_message(cid, text, parse_mode="Markdown")
    else:
        text = "⛔️ Настройки доступны только *администраторам*!"
        log(message)
        bot.send_message(cid, text, parse_mode="Markdown")


@bot.message_handler(commands=['deluser'])
def adduser(message):
    cid = getCID(message)
    check = base.userType(message.from_user.id)
    if check == 'admin':
        intext = base.check_data(message.text[9:])
        if bool(intext):
            log(message)
            bot.send_message(cid, base.delUser(intext), parse_mode="Markdown")
        else:
            text = "*Удаление пользователя*\n\n" \
                   "ℹ️ Используй эту команду для удаления пользователя из доверенного листа, в формате:" \
                   "\n\n`/deluser <user_id>`"
            log(message)
            bot.send_message(cid, text, parse_mode="Markdown")
    else:
        text = "⛔️ Настройки доступны только *администраторам*!"
        log(message)
        bot.send_message(cid, text, parse_mode="Markdown")



@bot.message_handler(commands=['addadmin'])
def addadmin(message):
    cid = getCID(message)
    check = base.userType(message.from_user.id)
    if check == 'admin':
        intext = base.check_data(message.text[10:])
        if bool(intext):
            log(message)
            bot.send_message(cid, base.addUser(intext, 'admin'), parse_mode="Markdown")
        else:
            text = "*Добавление администратора*\n\n" \
                   "ℹ️ Используй эту команду для добавления администратора, в формате:" \
                   "\n\n`/adduser <user_id>`"
            log(message)
            bot.send_message(cid, text, parse_mode="Markdown")
    else:
        text = "⛔️ Настройки доступны только *администраторам*!"
        # log(message)
        bot.send_message(cid, text, parse_mode="Markdown")


@bot.message_handler(commands=['change'])
def change(message):
    cid = getCID(message)
    check = base.userType(message.from_user.id)
    if check == 'admin':
        intext = message.text[8:]
        if bool(intext):
            change = base.updateMail(message.from_user.id, str(intext))
            log(message)
            bot.send_message(cid, change, parse_mode="Markdown")
        else:
            text = "*Смена адреса получателя*\n\n" \
                   "ℹ️ Для смены адреса получателя используй команду в формате:\n\n`/change <e-mail address>`"
            log(message)
            bot.send_message(cid, text, parse_mode="Markdown")
    else:
        text = "⛔️ Настройки доступны только *администраторам*!"
        log(message)
        bot.send_message(cid, text, parse_mode="Markdown")


@bot.message_handler(commands=['getlog'])
def getlog(message):
    cid = getCID(message)
    check = base.userType(message.from_user.id)
    if check == 'admin':
        file = open(config.properties.PATH + "log/bot.log", 'rb')
        log(message)
        bot.send_document(cid, file)
    else:
        text = "⛔️ Настройки доступны только *администраторам*!"
        log(message)
        bot.send_message(cid, text, parse_mode="Markdown")


@server.route("/bot", methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=config.properties.APP_URL)
    return "OK!", 200

server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
server = Flask(__name__)