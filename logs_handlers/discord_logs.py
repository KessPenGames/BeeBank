import disnake

from configs import config

logs = [
    "**sender** получил **dataАР** от игрока **receiver**. С комментарием **data**",
    "**sender** перевёл **dataАР** игроку **receiver**. С комментарием **data**",
    "Банкир **sender** создал счёт **receiver**",
    "Банкир **sender** создал карту **receiver** с номером **data**",
    "Игрок **sender** переоткрыл карту **data**"
]

notifications = [
    "Вы получили **dataАР** от игрока **sender**. Комментарий: **data**",
    "С вашей карты **sender** снято **dataАР**."
]


async def sendLog(guild: disnake.Guild, log_type: int, sender, receiver, datas: str):
    guild_id = config.getAttr("guild-id")
    channel_id = config.getAttr("logs-channel-id")

    if guild.id == guild_id:
        channel = guild.get_channel(channel_id)
        datas = datas.split("|")
        log = logs[log_type - 1].replace("sender", sender)\
            .replace("receiver", receiver)
        for data in datas:
            log = log.replace("data", data, 1)
        await channel.send(log)


async def sendNotification(user: disnake.Member, not_type: int, sender, datas: str):
    datas = datas.split("|")
    notification = notifications[not_type - 1].replace("sender", sender)
    for data in datas:
        notification = notification.replace("data", data, 1)
    await user.send(notification)
