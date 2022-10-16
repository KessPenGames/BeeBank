import re

from configs import config


def isMain(var):
    return var == "__main__"


def isAuthor(ctx):
    return ctx.author.id == config.getAttr("admin-id")


def isHex(hexColor: str):
    match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hexColor)
    return True if match else False
