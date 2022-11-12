from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import datetime
import pytz

from configs import config

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

tz = pytz.timezone('Asia/Novosibirsk')


async def backuping():
    file = drive.CreateFile({
        'title': f"{datetime.datetime.now(tz).strftime('%d-%m-%Y %H:%M')} - {config.getAttr('db-name')}",
        'parents': [{'id': '1TdRsJAD3XQeQHk2hfJF70XEXk5v62sfi'}]
    })
    file.SetContentFile(config.getAttr("db-name"))
    file.Upload()
    file = None
