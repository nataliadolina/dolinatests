import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to, text):
    login = "natashka_flask@mail.ru"
    password = "natashkaissendingyouemail"
    url = "smtp.mail.ru"
    msg = MIMEMultipart()
    msg['Subject'] = 'Сброс пароля'
    msg['From'] = 'natashka_flask@mail.ru'
    body = text
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP_SSL(url, 587)
        server.login(login, password)
        server.sendmail(login, to, msg.as_string())
        server.quit()

    except Exception:
        pass
