import globals as g
from titan import titan_time, titan_hp, titan_max_hp
from logger import async_log
from mslbot import command_bot
from discord import File
from adbtools import msl_restart, navigate, startup
from filetools import im_path
from imagetools import save_img
from discord.ext.commands import Cog, command


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('commands')

    @command(name='restart',
             brief='Restarts the Game and/or the Emulator',
             description='Restarts the Game and/or the Emulator',
             aliases=['kill'],
             pass_context=True)
    @async_log
    async def restart(self, context, handle: str = 'smurf', force: str = False):
        """
        Discord Function to restart the Game and/or the Emulator
        :param context: passed from discord
        :param handle: additional Arguments, restricted use
        :param force: trigger if Game restart should be bypassed and Nox should be restarted immediately, restricted use
        :return: none
        """
        handle = handle.lower()
        if handle == 'main' or force is not False:
            if str(context.author) == g.DISCORD_CFG['USER']:
                if handle == 'main':
                    handle = g.MAIN
                else:
                    handle = g.SMURF
                if force is not False:
                    force = True
            else:
                await context.send('Missing permissions!')
                await context.message.add_reaction(f'missing_permissions:{g.EMOJI["MISSING_PERMISSIONS"]}')
                return False
        else:
            handle = g.SMURF
        await context.send('Restarting Emulator, please stand by...')
        rst = await msl_restart(handle, force)
        if rst is True:
            await context.send('Restart complete.')
        else:
            await context.send('Restart failed.')

    @command(name='startup',
             brief='Starts the Game and enters the Main Screen',
             description='Restarts the Game and/or the Emulator',
             aliases=['start'],
             pass_context=True)
    @async_log
    async def startup_handler(self, context, handle: str = 'smurf'):
        """
        Discord Function to restart the Game and/or the Emulator
        :param context: passed from discord
        :param handle: additional Arguments, restricted use
        :return: none
        """
        handle = handle.lower()
        if handle == 'main':
            if str(context.author) == g.DISCORD_CFG['USER']:
                handle = g.MAIN
            else:
                await context.send('Missing permissions!')
                await context.message.add_reaction(f'missing_permissions:{g.EMOJI["MISSING_PERMISSIONS"]}')
        else:
            handle = g.SMURF
        await context.send('Starting, please stand by...')
        start = await startup(handle)
        if start is True:
            await context.send('Startup complete')
        else:
            await context.send('Startup failed')

    @command(name='ss',
             brief='Takes a Screenshot',
             description='Takes a Screenshot',
             aliases=['screenshot', 'SS', 'Screen', 'screen'],
             pass_context=True)
    @async_log
    async def ss(self, context, *args: str):
        """
        Discord Function for taking a Screenshot, calls screen() and sends an Image to the Channel or User
        :param context: passed from Discord
        :param args: additional Arguments, restricted use
        :return: none
        """
        handle = g.SMURF
        image = False
        async with context.typing():
            main_flag = False
            bot_flag = False
            if str(context.author) == g.DISCORD_CFG['USER']:
                for arg in args:
                    arg = arg.lower()
                    if arg == 'main':
                        main_flag = True
                    elif arg == 'bot':
                        bot_flag = True

            if bot_flag is False:
                if main_flag is True:
                    handle = g.MAIN
                await handle.screenshot()
                image = await save_img(handle.screen, handle.file)
            if image is not False:
                await context.send(content=context.author.mention, file=File(im_path(handle.file)))
            else:
                await context.send('An Error occurred')

    @command(name='Command',
             brief='Commands the Bots',
             description='Commands the Bots',
             aliases=['cmd', 'CMD', 'command'],
             pass_context=True,
             hidden=True)
    @async_log
    async def cmd(self, context, *args: str):
        """
        Discord Function to command the Bots
        :param context: passed from Discord
        :param args: additional Arguments, restricted use
        :return: True if successful, False / Error on Error
        """
        async with context.typing():
            main_flag = False
            cmd_name = False
            if str(context.author) == g.DISCORD_CFG['USER']:
                for arg in args:
                    arg = arg.lower()
                    if arg == 'main':
                        main_flag = True
                    elif arg in ['gem', 'slime']:
                        cmd_name = 'astrogem'
                    elif arg in ['astromon', 'mon']:
                        cmd_name = 'astrochip'
                    elif arg in ['pvp', 'league']:
                        cmd_name = 'league'
                    elif arg in ['golem', 'forever', 'rare', 'dragon', 'starstone', 'start', 'stop', 'pause']:
                        cmd_name = arg
                if cmd_name is not False:
                    if cmd_name in ['stop', 'pause']:
                        cmd_list = [cmd_name]
                    else:
                        cmd_list = ['stop', cmd_name, 'start']
                    if main_flag is True:
                        handle = g.MAIN
                    else:
                        handle = g.SMURF
                    if handle.bot is not False:
                        success = await command_bot(cmd_list, handle)
                        if success is True:
                            await context.message.add_reaction(f'{cmd_name}:{g.EMOJI[cmd_name.upper()]}')
                            await context.send(f'Executed Command:\t{cmd_name}\nmain_flag:\t{main_flag}')
                            return True
                        else:
                            await context.send(f'Unable to Execute Command\n{success}')
                            return f'Error: {success}'
                    else:
                        await context.send('Unable to Execute Command\nBot not found!')
                        return 'Error: Bot not Found!'
                else:
                    await context.send(f'No such Command found, Arguments given: {args}')
                    return False
            else:
                await context.message.add_reaction(f'missing_permissions:{g.EMOJI["MISSING_PERMISSIONS"]}')
                await context.send('Missing Permissions!')
                return False

    @command(name='Goto',
             brief='Moves the Player to the Titan Screen',
             description='Moves the Player to the Titan Screen',
             aliases=['goto', 'titan', 'move'],
             pass_context=True,
             hidden=True)
    @async_log
    async def goto(self, context, *args: str):
        """
        Discord Function to move the selected Player to the Titan Screen
        :param context: passed from Discord
        :param args: additional Arguments, restricted use
        :return: True if successful, False / Error on Error
        """
        async with context.typing():
            main_flag = False
            if str(context.author) == g.DISCORD_CFG['USER']:
                for arg in args:
                    arg = arg.lower()
                    if arg == 'main':
                        main_flag = True
                if main_flag is True:
                    handle = g.MAIN
                else:
                    handle = g.SMURF
            else:
                handle = g.SMURF
            if handle.device is not False:
                await command_bot(['log', 'stop'], handle)
                await context.send('Moving to Titan Screen, please stand by...')
                going = await navigate(handle)
                if going is True:
                    await context.send('Successfully moved to the Titan Screen.')
                else:
                    await context.send('An Error occured while moving to the Titan Screen, please try again later.')
            else:
                await context.send('Unable to move to the Titan Screen, Nox not running :-(')

    @command(name='Rank',
             brief='Shows the current Ranking',
             description='Shows the current Ranking',
             aliases=['rank', 'ranking', 'top5'],
             pass_context=True)
    @async_log
    async def rank(self, context):
        """
        Discord Function for Ranking Screenshot, calls screen() and sends an Image to the Channel or User
        :param context: passed from Discord
        :return: none
        """
        async with context.typing():
            if titan_time() is True:
                image = await g.SMURF.crop_screen('rank', g.FILE_CFG['RANK'])
            else:
                image = await g.SMURF.crop_screen('rank', g.FILE_CFG['RANK'], g.FILE_CFG['LAST_TITAN'])
            if image is True:
                await context.send(content=context.author.mention, file=File(im_path(g.FILE_CFG['RANK'])))
            else:
                await context.send('An Error occurred.')

    @command(name='Health',
             brief='Shows the current Titans Health',
             description='Shows the current Titans Health',
             aliases=['health', 'HP', 'Hp', 'hp'],
             pass_context=True)
    @async_log
    async def hp(self, context):
        """
        Discord Function for Ranking Screenshot, calls screen() and sends an Image to the Channel or User
        :param context: passed from Discord
        :return: none
        """
        async with context.typing():
            if titan_time() is True:
                image = await g.SMURF.crop_screen('health', g.FILE_CFG['HEALTH'])
            else:
                image = await g.SMURF.crop_screen('health', g.FILE_CFG['HEALTH'], g.FILE_CFG['LAST_TITAN'])
            if image is True:
                curr_hp = await titan_hp()
                if curr_hp is not False:
                    max_hp = await titan_max_hp(int(g.TITAN_CFG['LEVEL']))
                    hp_str = 'Current HP: {:,}\t(~{}%)'.format(curr_hp, round(curr_hp/max_hp*100))
                else:
                    hp_str = 'Error getting the current HP'
                await context.send(content=f'{hp_str}\n{context.author.mention}', file=File(im_path(g.FILE_CFG['HEALTH'])))
            else:
                await context.send('An Error occurred.')

    @command(name='Level',
             brief='Shows the current Level and Element of the Titan',
             description='Shows the current Level and Element of the Titan',
             aliases=['level', 'element', 'Element', 'ele', 'lvl'],
             pass_context=True)
    @async_log
    async def lvl(self, context):
        """
        Discord Function for Titan Level and Element
        :param context: passed from Discord
        :return: none
        """
        async with context.typing():
            await context.send(content=f'The current Titan is Level {g.TITAN_CFG["LEVEL"]}, '
                                       f'Element <:element_{g.TITAN_CFG["ELEMENT"].lower()}:'
                                       f'{g.EMOJI[g.TITAN_CFG["ELEMENT"]]}>')


def setup(bot):
    bot.add_cog(Commands(bot))
