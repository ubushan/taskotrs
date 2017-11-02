#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sendgrid
from sendgrid.helpers.mail import *
from conf import base, config


def send(user_id, subject, message):
    try:
        sg = sendgrid.SendGridAPIClient(apikey=config.properties.SENDGRID_API_TOKEN)
        from_email = Email(email=config.properties.FROM, name=config.properties.FROM_NAME)
        to_email = Email(base.userMail(user_id))
        subject = config.properties.SUBJECT + subject
        content = Content("text/plain", message)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())

        if response.status_code == 202:
            return "✅ Письмо успешно отправлено на %s\n\n" \
                   "ℹ️ Для смены адреса получателя используй команду в формате:\n`/change <e-mail address>`" % base.userMail(user_id)
        else:
            return "Что-то пошло не так :( Попробуй ещё раз!"
    except:
        return "Could not connect to server :("
