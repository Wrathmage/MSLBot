import globals as g
from titan import titan_level, titan_max_hp, titan_time, titan_hp
from mslbot import command_bot, find_bots
from psutil import NoSuchProcess
from asyncio import sleep
from discord import Colour, Embed, File
from adbtools import adb_touch, get_pid_by_cmd, navigate
from datetime import datetime
from filetools import get_ping_list, im_path, update_titan_cfg
from imagetools import compare_image, save_img
from subprocess import Popen
from discord.ext.tasks import loop
from discord.ext.commands import Cog, command
from discord_functions import PEPE

LOOPS = ['check_nox', 'check_titan']


class Tasks(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('tasks')
            print('Starting Loops...')
            for l in LOOPS:
                await self.start_loop(l)
                print(f'{l} Loop started')

    @command(name='loops_start',
             brief='Starts the Loops to check for Titans and Nox',
             description='Starts the Loops to check for Titans and Nox',
             aliases=['start_loops'],
             pass_context=True,
             hidden=True)
    async def start_loops(self, context):
        for l in LOOPS:
            if await self.start_loop(l) is True:
                await context.send(f'{l} Loop started.')
            else:
                await context.send(f'{l} Loop already running.')
        await context.send('Starting of Loops completed.')

    @command(name='loops_stop',
             brief='Stops the Loops to check for Titans and Nox',
             description='Stops the Loops to check for Titans and Nox',
             aliases=['stop_loops'],
             pass_context=True,
             hidden=True)
    async def stop_loops(self, context):
        for l in LOOPS:
            if await self.stop_loop(l) is True:
                await context.send(f'{l} Loop stopped.')
            else:
                await context.send(f'{l} Loop is not running.')
        await context.send('Stopping of Loops completed.')

    @command(name='loops_restart',
             brief='Restarts the Loops to check for Titans and Nox',
             description='Restarts the Loops to check for Titans and Nox',
             aliases=['restart_loops'],
             pass_context=True,
             hidden=True)
    async def restart_loops(self, context):
        for l in LOOPS:
            if await self.stop_loop(l) is True:
                await context.send(f'{l} Loop stopped.')
            else:
                await context.send(f'{l} Loop is not running.')
            await sleep(2)
            if await self.start_loop(l) is True:
                await context.send(f'{l} Loop started.')
            else:
                await context.send(f'{l} Loop already running.')
        await context.send('Stopping of Loops completed.')

    async def start_loop(self, loop_to_start):
        print(f'Starting Loop {loop_to_start}...')
        lts = getattr(self, loop_to_start)
        if not lts.is_running():
            lts.start()
            return True
        else:
            return False

    async def stop_loop(self, loop_to_stop):
        print(f'Starting Loop {loop_to_stop}...')
        lts = getattr(self, loop_to_stop)
        if lts.is_running():
            lts.stop()
            return True
        else:
            return False

    @loop(seconds=int(g.TITAN_CFG['FREQ']))
    async def check_titan(self):
        """
        Screenshots the Smurf Device and checks if a new Titan is up, this Function is looped
        :return: none
        """
        channel = PEPE.get_channel(int(g.DISCORD_CFG['CHANNEL']))
        if g.TITAN_CFG['UPDATES'] == 'ON':
            await g.SMURF.screenshot()
            compare = await compare_image(g.SMURF.screen, g.FILE_CFG['BUFF'])
            if titan_time() is True:
                if compare is not False:
                    curr_hp = await titan_hp()
                    max_hp = await titan_max_hp(int(g.TITAN_CFG['LEVEL']))
                    last_update = int(g.TITAN_CFG['LAST_UPDATE'])
                    if curr_hp is not False:
                        percent = round(curr_hp / max_hp * 100)
                    else:
                        percent = 0
                    level, element = await titan_level()
                    if percent > 5 and level > int(g.TITAN_CFG['LEVEL']) or last_update > percent > 5:
                        new_update = False
                        next_update = False
                        if 75 > percent > 50:
                            next_update = 50
                            new_update = 75
                        elif 50 > percent > 25:
                            next_update = 25
                            new_update = 50
                        elif 25 > percent > 10:
                            next_update = 10
                            new_update = 25
                        elif 10 > percent > 5:
                            next_update = 5
                            new_update = 10
                        if next_update is not False:
                            update_titan_cfg(LAST_UPDATE=str(next_update))
                        await sleep(2)
                        level = str(level)
                        ping_list = get_ping_list()
                        ping_me = ''
                        if type(ping_list) is dict and level in ping_list:
                            ping_me = '\t'.join(ping_list[level])
                        if next_update is False:
                            message = f'{element.capitalize()} Titan is up now!\t**Lv. {level}**'
                            update_titan_cfg(NEXT_UPDATE=str(75))
                        else:
                            message = f'{element.capitalize()} Titan fell below {new_update}% HP!\t**Lv. {level}**'
                        update_titan_cfg(LEVEL=level, ELEMENT=element)
                        async for msg in channel.history(limit=20):
                            if msg.author == PEPE.user:
                                await msg.delete()
                        await g.SMURF.screenshot()
                        await g.SMURF.crop_screen('titan', g.FILE_CFG['TITAN'])
                        if element == 'fire':
                            colour = Colour.red()
                        elif element == 'light':
                            colour = Colour.gold()
                        elif element == 'water':
                            colour = Colour.blue()
                        elif element == 'wood':
                            colour = Colour.green()
                        else:
                            colour = Colour.dark_grey()
                        if curr_hp is not False:
                            hp_str = '{:,}'.format(curr_hp)
                        else:
                            hp_str = 'Error: can\'t get the current HP'
                        max_hp = await titan_max_hp(int(level))
                        embed = Embed(title=message, colour=colour, timestamp=datetime.utcnow())
                        embed.set_thumbnail(url='attachment://element.webp')
                        embed.add_field(name='Current HP:', value=hp_str, inline=True)
                        embed.add_field(name='Max HP:', value='{:,}'.format(max_hp), inline=True)
                        if ping_me != '':
                            embed.add_field(name='Requested Pings', value=ping_me, inline=False)
                        files = [File(im_path(g.FILE_CFG['TITAN']), filename='image.png'),
                                 File(im_path(f'Element_{element.capitalize()}.webp'), filename='element.webp')]
                        embed.set_image(url='attachment://image.png')
                        embed.set_footer(text='\u200b')
                        await channel.send(embed=embed, files=files, content=ping_me)
                elif compare is False and g.SMURF.location not in ['Atk', 'Test']:
                    await command_bot(['log', 'stop'], g.SMURF)
                    await navigate()
            elif compare is not False:
                await g.SMURF.screenshot()
                await save_img(g.SMURF.screen, g.FILE_CFG['LAST_TITAN'])
                compare_back = await compare_image(g.SMURF.screen, g.FILE_CFG['BACK'])
                if compare_back is not False:
                    await adb_touch(g.SMURF, compare_back[0], compare_back[1])
                    await command_bot(['script', 'select', 'rare', 'start'], g.SMURF)

    @loop(seconds=60)
    async def check_nox(self):
        """
        checks if the Nox Emulators are running and starts them if they are not

        :return: None
        """
        user = PEPE.get_user(int(g.DISCORD_CFG['USERID']))
        if g.MAIN.bot is None or g.SMURF.bot is None\
            or g.AUTO_IT.WinExists(f'[HANDLE:{g.MAIN.bot}]') == 0\
                or g.AUTO_IT.WinExists(f'[HANDLE:{g.SMURF.bot}]') == 0:
                    find_bots()
        pid = dict()
        emulators = [g.NOX_CFG['EMU_MAIN'], g.NOX_CFG['EMU_SMURF']]
        for emu in emulators:
            i = 0
            msl_find_str = f'-clone:{emu}'
            while i < 5:
                try:
                    pid[emu] = get_pid_by_cmd(msl_find_str)
                    if pid[emu] is not False:
                        break
                    else:
                        i += 1
                        await sleep(10)
                except (ProcessLookupError, NoSuchProcess):
                    print(f'Exception occured')
                    pid[emu] = False
                    break
            if pid[emu] is False:
                print(f'Trying to start Process for {emu}')
                Popen([f'{g.NOX_CFG["PATH"]}', f'{msl_find_str}', f'-package:{g.MSL_PACK}', f'-lang:en'],
                      creationflags=g.DETACHED_PROCESS, close_fds=True)
                if type(user) != 'NoneType':
                    await user.send(f'No PID found for {emu}, restarting Emulator')

    @loop(seconds=int(g.TITAN_CFG['FREQ']))
    async def check_hp(self):
        await titan_hp()
        pass

    @check_hp.before_loop
    @check_nox.before_loop
    @check_titan.before_loop
    async def check_loops_before(self):
        await PEPE.wait_until_ready()

    @check_hp.after_loop
    async def check_hp_after(self):
        if self.check_hp.is_being_cancelled():
            await self.start_loop('check_hp')

    @check_nox.after_loop
    async def check_loops_after(self):
        if self.check_nox.is_being_cancelled():
            await self.start_loop('check_nox')

    @check_titan.after_loop
    async def check_titan_after(self):
        if self.check_titan.is_being_cancelled():
            await self.start_loop('check_titan')


def setup(bot):
    bot.add_cog(Tasks(bot))
