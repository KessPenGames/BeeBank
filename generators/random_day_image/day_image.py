import datetime
import glob
import random

import disnake


async def random_img(bot_avatar):
    images = glob.glob("./generators/random_day_image/pictures/*.jpg")
    random_image = random.choice(images)
    embed = disnake.Embed(title="Картина дня:", color=3092790, timestamp=datetime.datetime.utcnow())
    embed.set_image(file=disnake.File(random_image))
    embed.set_footer(text="Пчело-Банк", icon_url=bot_avatar)
    return embed
