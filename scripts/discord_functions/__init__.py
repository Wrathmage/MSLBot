import globals as g
from glob import glob
from logger import async_log
from asyncio import sleep
from discord import Game, Message, Intents, Status
from filetools import get_ping_list, save_ping_list
from discord.ext.commands import Bot as BotBase, CommandNotFound, MissingRequiredArgument, MissingPermissions

intents = Intents.default()
intents.members = True
COGS = [path.split('\\')[-1][:-3] for path in glob('./scripts/cogs/*.py')]


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f'{cog} cog ready')

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = g.DISCORD_CFG['BOT_PREFIX']
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        super().__init__(command_prefix=self.PREFIX, owner_id=g.DISCORD_CFG['USERID'], intents=intents)

    def run(self):
        self.setup()
        super().run(g.DISCORD_CFG['TOKEN'], reconnect=True)

    def setup(self):
        for cog in COGS:
            self.load_extension(f'scripts.cogs.{cog}')
            print(f'{cog} cog loaded')
        print('setup complete')

    @async_log
    async def on_command_error(self, context, exception):
        if isinstance(exception, CommandNotFound):
            await context.send('Command not found!')
        elif isinstance(exception, MissingRequiredArgument):
            await context.send('There is an argument missing!')
        elif isinstance(exception, MissingPermissions):
            await context.send('Missing Permissions!')
        elif hasattr(exception, 'original'):
            raise exception.original
        else:
            raise exception

    async def on_ready(self):
        await self.change_presence(activity=Game(name="Monster Super League"), status=Status.online)
        if not self.ready:
            self.guild = self.get_guild(271444150082207745)
            while not self.cogs_ready.all_ready():
                await sleep(0.5)
            self.ready = True
            print(f'Logged in as {self.user.name}')

    async def on_message(self, message: Message):
        if message.author == self.user:
            return
        await self.process_commands(message)
        if message.content[:1] == '@':
            name_list = message.content[1:].split()
            k = int(g.TITAN_CFG['LEVEL']) + 1

            for arg1 in name_list:
                if len(arg1) < 4 and arg1.isdigit():
                    level = int(arg1)
                else:
                    arg1 = arg1.lower()
                    if arg1 == 'fire':
                        while k % 5 != 0:
                            k += 1
                    elif arg1 == 'dark':
                        while k % 5 != 1:
                            k += 1
                    elif arg1 == 'water':
                        while k % 5 != 2:
                            k += 1
                    elif arg1 == 'wood':
                        while k % 5 != 3:
                            k += 1
                    elif arg1 == 'light':
                        while k % 5 != 4:
                            k += 1
                    else:
                        return False
                    level = k

                if level > int(g.TITAN_CFG['LEVEL']):
                    ping_list = get_ping_list()
                    if type(ping_list) is str:
                        ping_list = {}
                    element = ''
                    for x in range(5):
                        elements = ['FIRE', 'DARK', 'WATER', 'WOOD', 'LIGHT']
                        if level % 5 == x:
                            element = elements[x]
                    await message.add_reaction(f'element_{element.lower}:{g.EMOJI[element]}')
                    if str(level) not in ping_list:
                        ping_list.update({f'{level}': [f'{message.author.mention}']})
                        await message.author.send(f'Alarm for Requested Titan added.\nLevel:\t\t{level}\n'
                                                  f'Element:\t{element.capitalize()}')
                    else:
                        if message.author.mention not in ping_list[str(level)]:
                            print(f'ping_list[{level}] = {ping_list[str(level)]}')
                            ping_list[str(level)].append(message.author.mention)
                            await message.author.send(f'Alarm for Requested Titan added.\nLevel:\t\t{level}\n'
                                                      f'Element:\t{element.capitalize()}')
                        else:
                            await message.author.send(f'You already have an Alarm for the Level {level} Titan.')
                    save_ping_list(ping_list)
                else:
                    await message.author.send(f'Level below current Titan Level.\nrequested Level:\t{level}\n'
                                              f'current Level:\t\t{g.TITAN_CFG["LEVEL"]}')


PEPE = Bot()
