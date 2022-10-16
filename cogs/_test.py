from disnake.ext import commands

from utils.check import isHex


class TestCog(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx: commands.Context, hex: str):
        await ctx.send(str(isHex(hex)))


def setup(bot=commands.Bot):
    bot.add_cog(TestCog(bot))
    print(f"Cog {__name__} is loading!")
