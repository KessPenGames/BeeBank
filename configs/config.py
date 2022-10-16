import yaml
import os
import codecs

DUMP_STR = """
token: 'TOKEN'
bot-prefix: 'BeeBot'
bot-status: 'Bee Lines'
admin-id: 866553002172743701
guild-id: 765888901167972352
logs-channel-id: 847795886498512906
banker-role-id: 785727770394230835
bank-card-id: 000000
grant-card-id: 000000
db-name: 'database.db'
"""


def createIfNotExist():
    if not os.path.exists("config.yml"):
        with codecs.open('config.yml', 'w', 'utf-8') as file:
            config_dump = yaml.safe_load(DUMP_STR)
            yaml.dump(config_dump, file)


def getAttr(var: str):
    if os.path.exists("config.yml"):
        with codecs.open('config.yml', 'r', 'utf-8') as file:
            return yaml.safe_load(file)[var]
    return None
