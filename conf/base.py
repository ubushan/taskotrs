import sqlite3
from os import path
from conf import config

DATABASE = config.properties.PATH + "conf/users.db"
PATH = config.properties.PATH
MAIL = config.properties.OTRS_MAIL

# Проверка вводимых данных при добавлении UserID
def check_data(data):
    a = data
    if type(data) == int:
        return data
    if a.isdigit():
        return int(data)
    else:
        return False

# Создание Базы Данных
def createdb():
    if path.isfile(PATH + DATABASE):
        return 'Database already exist'
    else:
        con = sqlite3.connect(DATABASE)
        c = con.cursor()
        c.execute("CREATE TABLE users (user_id INTEGER,"
                  "user_type TEXT NOT NULL,"
                  "email TEXT)")
        con.commit()
        c.close()
        return 'Database create successfully'

# Проверка на существование пользователя в БД
def find(user_id):
    con = sqlite3.connect(DATABASE)
    c = con.cursor()
    user_id = (user_id,)
    c.execute("SELECT * FROM users WHERE user_id=?", user_id)
    out = c.fetchone()
    c.close()
    return bool(out)

# Найти UID
def findUid(user_id):
    con = sqlite3.connect(DATABASE)
    c = con.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id = '%s'" % user_id)
    out = c.fetchone()
    c.close()
    if out == None:
        return 0
    else:
        return out[0]

# Узнать user_type пользователя
def userType(user_id):
    con = sqlite3.connect(DATABASE)
    c = con.cursor()
    c.execute("SELECT user_type FROM users WHERE user_id = '%s'" % user_id)
    out = c.fetchone()
    c.close()
    if out == None:
        return None
    else:
        return out[0]

# Добавить пользователя
def addUser(user_id, role):
    utype = userType(user_id)
    if utype == role:
        return "ℹ️ Пользователь с `USER_ID %d` уже является %s'ом!" % (user_id, str.upper(role))
    else:
        if role == 'admin':
            if utype == 'user':
                con = sqlite3.connect(DATABASE)
                c = con.cursor()
                c.execute("UPDATE users SET user_type = '%s' WHERE user_id = '%s'" % ('admin', user_id))
                con.commit()
                c.close()
                return "✅ Пользователь с `USER_ID %d` переведен в ряды администраторов!" % user_id
            else:
                con = sqlite3.connect(DATABASE)
                c = con.cursor()
                c.execute("INSERT INTO users (user_id, user_type, email)"
                          "VALUES ('%s', '%s', '%s')" % (user_id, 'admin', MAIL))
                con.commit()
                c.close()
                return "✅ Администратор с `USER_ID %d` добавлен!" % user_id

        else:
            if utype == 'admin':
                con = sqlite3.connect(DATABASE)
                c = con.cursor()
                c.execute("UPDATE users SET user_type = '%s' WHERE user_id = '%s'" % ('user', user_id))
                con.commit()
                c.close()
                return "✅ Администратор с `USER_ID %d` переведен в ряды пользователей!" % user_id
            else:
                con = sqlite3.connect(DATABASE)
                c = con.cursor()
                c.execute("INSERT INTO users (user_id, user_type, email)"
                          "VALUES ('%s', '%s', '%s')" % (user_id, 'user', MAIL))
                con.commit()
                c.close()
                return "✅ Пользователь с `USER_ID %d` добавлен!" % user_id

# Удалить пользователя
def delUser(user_id):
    if find(user_id) == False:
        return "ℹ️ Пользователь с `USER_ID %d` не найден!" % user_id
    else:
        if userType(user_id) == 'user':
            con = sqlite3.connect(DATABASE)
            c = con.cursor()
            c.execute("DELETE FROM users WHERE user_id = '%s'" % user_id)
            con.commit()
            c.close()
            return "✅ Пользователь с `USER_ID %d` удален!" % user_id
        else:
            return "❌ Вы не можете удалить *администратора*"

# Обновить почтовый ящик отправителя для конкретного пользователя
def updateMail(user_id, mail):
    con = sqlite3.connect(DATABASE)
    c = con.cursor()
    user_id = (user_id,)
    c.execute("SELECT * FROM users WHERE user_id=?", user_id)
    out = c.fetchone()
    c.close()
    if out[2] == mail:
        return "❌ Введенный адрес `%s` уже используется!" % mail
    else:
        con = sqlite3.connect(DATABASE)
        c = con.cursor()
        c.execute("UPDATE users SET email = '%s' WHERE user_id = '%s'" % (mail, user_id[0]))
        con.commit()
        c.close()
        return "✅ Адрес получателя изменен на `%s`" % mail

# Узнать почтовый ящик отправителя для конкретного пользователя
def userMail(user_id):
    con = sqlite3.connect(DATABASE)
    c = con.cursor()
    user_id = (user_id,)
    c.execute("SELECT * FROM users WHERE user_id=?", user_id)
    out = c.fetchone()
    c.close()
    return out[2]


    # createdb()
    # adduser(123, 'Shelock', 'admin')
    # print(adduser(2211, 'John', 'user', MAIL))
    # print(adduser(221, 'Sherlock', 'user', MAIL))
    # print(addUser(6581704, 'admin'))
    # print(addUser(121135999, 'admin'))
    # print(deluser(6581704))
    # print(createdb())


    # print(update(6581704, "ubushaev08@yandex.ru"))
    # print(userMail(6581704))
