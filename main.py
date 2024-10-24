import telebot
from telebot import types
import os
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
import calendar
import glob

bot = telebot.TeleBot('7407683443:AAHQ_CS5zWBB-iznJLT-ylPmZK4RTF2zPY0')

latest=''

try:
    for backup in glob.glob('/run/media/onkolog/SSD/backup/backup*'):
        latest=backup[37:-4]
        print(latest)
except:
    latest=''

@bot.message_handler(commands=['start'])

def start(message): #Создание клавиатуры с кнопками
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    now = types.KeyboardButton("Сделать бэкап")
    date = types.KeyboardButton("Дата последнего бэкапа")
    gdrive = types.KeyboardButton("Загрузить всё в облако")
    send = types.KeyboardButton("Отправить последний сюда")
    list = types.KeyboardButton("Удалить все бэкапы с диска")
    markup.add(now,date,gdrive,send,list)
    bot.send_message(message.chat.id, text="Бот запущен".format(message.from_user), reply_markup=markup)


SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
PARENT_FOLDER_ID = "1ZygcmuCBgCU10dXdDl1lE5c_-qe2OlRc"
def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def upload_tar(path,dtu): #загрузка пачки бэкапов на гугл диск
    os.system('cp /run/media/onkolog/SSD/backup/*backup* /run/media/onkolog/SSD/backup/old_backs')
    command = 'cd /run/media/onkolog/SSD/backup; tar -zcvf /run/media/onkolog/SSD/backup/backup_all-'+dtu+'.tar /run/media/onkolog/SSD/backup/old_backs'
    os.system(command)
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name' : "backup_all-"+dtu,
        'parents' : [PARENT_FOLDER_ID]
    }

    file = service.files().create(
        body=file_metadata,
        media_body=path
    ).execute()
    os.system('cd /run/media/onkolog/SSD/backup; rm *backup_all*')
    os.system('rm /run/media/onkolog/SSD/backup/old_backs/*')


def dobackup(dt): #создание бэкапа
    global latest
    tarname = "backup-"+dt+".tar"
    cmdmv = 'cd /run/media/onkolog/SSD/backup/;mv *backup* old_backs/'
    cmdtar = 'tar -zcvf /run/media/onkolog/SSD/backup/backup-'+dt+'.tar /home/onkolog/Documents'
    os.system(cmdmv)
    os.system(cmdtar)

@bot.message_handler(content_types=['text'])

def func(message): #действия кнопок
    if(message.text == "Сделать бэкап"):      
        nw = datetime.now()
        dt = nw.strftime("%d-%m-%Y_%H:%M:%S")
        global latest
        if latest == 'Ещё не создано ни одного бэкапа':
            latest = dt
        dobackup(dt)
        latest = dt
        bot.send_message(message.chat.id,'Бэкап создан');
    
    elif(message.text == "Дата последнего бэкапа"):
        if latest!='':
            data = "Дата:"+' '+latest[:2]+' '+calendar.month_name[int(latest[3:5])]+' '+latest[6:10]+' '
            vremya = "Время: "+latest[11:19]
            bot.send_message(message.chat.id,data+vremya)
        else:
            bot.send_message(message.chat.id,"Бэкапов нет")

    elif(message.text == "Загрузить всё в облако"):
        nwu = datetime.now()
        dtu = nwu.strftime("%d-%m-%Y_%H:%M:%S")
        path='/run/media/onkolog/SSD/backup/backup_all-'+dtu+'.tar'
        upload_tar(path,dtu)
        bot.send_message(message.chat.id,'Файлы загружены. Ссылка на них: https://drive.google.com/drive/folders/1ZygcmuCBgCU10dXdDl1lE5c_-qe2OlRc?usp=sharing')

    elif(message.text == "Отправить последний сюда"):
        try:
            bot.send_document(message.chat.id, document=open('/run/media/onkolog/SSD/backup/backup-'+latest+'.tar', 'rb'))
        except:
            bot.send_message(message.chat.id,"Бэкапов нет")

    elif(message.text == "Удалить все бэкапы с диска"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        yes = types.KeyboardButton("Да⠀")
        no = types.KeyboardButton("Нет⠀")
        markup.add(yes,no)
        bot.send_message(message.chat.id, text="Вы уверены?", reply_markup=markup)

    elif(message.text == "Да⠀"):
        os.system('rm /run/media/onkolog/SSD/backup/*backup*;rm /run/media/onkolog/SSD/backup/old_backs/*')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        now = types.KeyboardButton("Сделать бэкап")
        date = types.KeyboardButton("Дата последнего бэкапа")
        gdrive = types.KeyboardButton("Загрузить всё в облако")
        send = types.KeyboardButton("Отправить последний сюда")
        list = types.KeyboardButton("Удалить все бэкапы с диска")
        markup.add(now,date,gdrive,send,list)
        bot.send_message(message.chat.id, text="Директория очищена".format(message.from_user), reply_markup=markup)

    elif(message.text == "Нет⠀"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        now = types.KeyboardButton("Сделать бэкап")
        date = types.KeyboardButton("Дата последнего бэкапа")
        gdrive = types.KeyboardButton("Загрузить всё в облако")
        send = types.KeyboardButton("Отправить последний сюда")
        list = types.KeyboardButton("Удалить все бэкапы с диска")
        markup.add(now,date,gdrive,send,list)
        bot.send_message(message.chat.id, text="Вы вернулись в главное меню".format(message.from_user), reply_markup=markup)

    else:
        bot.send_message(message.chat.id,"Управление возможно только кнопками")

bot.polling(none_stop=True, interval=0)