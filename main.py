import json
import os
import smtplib
import models as db
from sqlalchemy import create_engine, exists
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

engine = create_engine("sqlite:///logdb.db", echo=False)
db.Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db.Base.metadata.create_all(engine)
session_db = DBSession()


def send_mail(sender, address_book, subject, body, mail_server):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ','.join(address_book)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()
    s = smtplib.SMTP(mail_server)
    s.sendmail(sender, address_book, text)
    s.quit()


def read_error_file(file_name, path_):
    with open(path_ + file_name, 'r') as file_data:
        error_data = file_data.read().replace('\n', '')
        return error_data


def add_file_log(order_id, file_type, mail_date):
    log = db.Orders(order_id=order_id, file_type=file_type, mail_date=mail_date)
    session_db.merge(log)
    session_db.commit()


def check_ex(order_id, file_type):
    return session_db.query(
        exists().where(db.Orders.order_id == order_id and db.Orders.file_type == file_type)).scalar()


jsonfile = open("settings.json", )
data = json.load(jsonfile)
path = data["path"]
mail_server = data["mail_server"]
sender = data["sender"]
address_book = []

for address in data["address_book"]:
    address_book.append(address)

for root, dirs, files in os.walk(path):
    now = datetime.now()
    dt_string = now.strftime("%d.%m.%Y %H:%M:%S")
    for file in files:
        if file.endswith(".err") and check_ex(file[3:-4], "err") == False:
            error_msg = read_error_file(file, path)
            error_subj = "Система маркировки: Ошибка в заказе: " + file[3:-4]
            error_body = ("При обработке заказа: {}, обнаружена следующая ошибка: {}".format(file[3:-4], error_msg))
            send_mail(sender, address_book, error_subj, error_body, mail_server)
            add_file_log(file[3:-4], "err", dt_string)

        if file.endswith(".out") and check_ex(file[3:-4], "out") == False:
            ok_subj = "Система маркировки: Заказ {} успешно обработан".format(file[3:-4])
            ok_body = "Заказ {} успешно обработан".format(file[3:-4])
            send_mail(sender, address_book, ok_subj, ok_body, mail_server)
            add_file_log(file[3:-4], "out", dt_string)
