#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  Python Bot for Discord-rewrite Branch, working with Python 3.6.7
import re
import cv2
import numpy as np
import psutil
import signal
import asyncio
import discord
import logging
import calendar
from io import BytesIO
from os import kill
from PIL import Image, ImageFile
from json import dump, load
from time import sleep
from psutil import NoSuchProcess
from discord import Colour, Embed, Game
from os.path import dirname, join as os_join
from datetime import date, datetime
from functools import wraps
from configobj import ConfigObj
from subprocess import Popen
from ppadb.device import Device
from ppadb.client import Client as AdbClient
from discord.file import File
from win32com.client import Dispatch
from discord.ext.commands import Bot

ImageFile.LOAD_TRUNCATED_IMAGES = True
logging.basicConfig(filename='log.ini', level=logging.ERROR, format='%(levelname)s %(asctime)s - %(message)s')
logger = logging.getLogger()


class MSL:
    """
    Standard Class for all Players and Functions regarding them
    """
    ADB_connected = False
    Level = None

    def __init__(self, name: str, port: str, emu: str, file: str):
        """
        sets the default Values for the Player and Emulator
        :param name: Name of the Nox Emulator
        :param port: Port of the Nox Emulator
        :param file: File for the Screenshot
        """
        logger.debug(f'Initializing with name: {name}, port: {port}, emu: {emu} and file: {file}')
        self.name = name
        self.port = port
        self.emu = emu
        self.file = file
        self.bot = None
        self.device = None
        self.screen = None
        self.location = 'unknown'

    def set_bot(self, bot: int):
        """
        sets the Bot handle of the Player
        :param bot: hwnd
        :return:
        """
        logger.debug(f'Changing bot from {self.bot} to {bot} on {self.name}')
        self.bot = bot

    def set_device(self, device: Device):
        """
        sets the Device handle of the Player
        :param device: ppadb Device type
        :return:
        """
        logger.debug(f'Changing device from {self.device} to {device} on {self.name}')
        self.device = device

    def set_location(self, location: str):
        """
        sets the Location of the Player
        :param location: String containing the Location of the Player
        :return:
        """
        logger.debug(f'Changing location from {self.location} to {location} on {self.name}')
        self.location = location

    async def screenshot(self) -> bool:
        """
        takes a Screenshot of the Nox Emulator of the Player
        :return: True or False, depending on Success
        """
        logger.debug(f'Changing screen on {self.name}')
        if self.device is not None:
            try:
                self.screen = Image.open(BytesIO(self.device.screencap()))
            except EnvironmentError:
                return False
            else:
                return True
        else:
            return False

    async def show_screen(self) -> bool:
        """
        shows the Screenshot of the Player
        :return: True or False, depending on Success
        """
        if self.screen is not None:
            logger.debug(f'Showing Screenshot on {self.name}')
            self.screen.show()
            return True
        else:
            return False

    async def crop_screen(self, area: str, output: str=None, diff: str=None) -> bool:
        """
        crops the Screenshot of the Player with the given Area and saves it to the Output if given
        :param area: Area to be cropped to
        :param output: File to be saved to
        :param diff: Different File to be cropped from instead to fresh Screenshot
        :return: True or False, depending on Success
        """
        if type(area) is str:
            file = True
            area = area.lower()
            if area == 'rank':
                area = [607, 133, 791, 398]
            elif area == 'level':
                area = [15, 450, 80, 470]
                file = False
            elif area == 'health':
                area = [17, 472, 610, 540]
            elif area == 'hp':
                area = [69, 520, 165, 538]
            elif area == 'buff':
                area = [539, 189, 600, 230]
            elif area == 'titan':
                area = [0, 340, 610, 552]
            else:
                area = ''
            if area != '':
                if diff is None:
                    img_crop = self.screen.crop(area)
                else:
                    img_crop = Image.open(im_path(diff))
                if type(output) is str and file is True:
                    if await save_img(img_crop, output) is True:
                        return True
                    else:
                        return False
                elif file is False:
                    MSL.Level = img_crop
                    return True
            else:
                return False

    def __str__(self):
        """
        :return: all Items of the Player
        """
        return f'name:\t{self.name}\nport:\t{self.port}\nbot:\t{self.bot}\ndevice:\t{self.device}\n' \
               f'location:\t{self.location}\nfile: {self.file}\nscreen:{self.screen}'


# IMPORT FROM CONFIG
CFG = ConfigObj('config.ini')
TITAN_HP = ConfigObj('titanhp.ini')
ADB_CFG = CFG['ADB']
NOX_CFG = CFG['NOX']
FILE_CFG = CFG['FILE']
TITAN_CFG = CFG['TITAN']
DISCORD_CFG = CFG['DISCORD'][CFG['CONFIG_MODE']]
EMOJI = DISCORD_CFG['EMOJI']
PROFILES = CFG['BOTPROFILES']
DETACHED_PROCESS = 8
MAIN = MSL(NOX_CFG['MAIN'], ADB_CFG['MAIN_PORT'], NOX_CFG['EMU_MAIN'], FILE_CFG['MAIN_SCREEN'])
SMURF = MSL(NOX_CFG['SMURF'], ADB_CFG['SMURF_PORT'], NOX_CFG['EMU_SMURF'], FILE_CFG['SMURF_SCREEN'])
MSL_PACK = 'com.ftt.msleague_gl'
# DISCORD INTENTS, needed since Discord API 1.5
intents = discord.Intents.default()
intents.members = True
PEPE = Bot(command_prefix=DISCORD_CFG['BOT_PREFIX'], intents=intents, owner_id=DISCORD_CFG['USERID'])
AUTO_IT = Dispatch("AutoItX3.Control")
# END OF CONFIG


def log(func):
    """
    basic logging decorator
    :param func: decorated function
    :return: the return of the decorated function
    """
    @wraps(func)
    def call(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f'\n+', '-'*17, '+', '-'*81,
              f'\n|\tTime:\t\t\t|\t{datetime.now().strftime("%H:%M:%S")}\n'
              f'|\tSync:\t\t\t|\tTrue\n'
              f'|\tFunction:\t\t|\t{func.__name__}\n'
              f'|\targs:\t\t\t|\t{args}\n'
              f'|\tkwargs:\t\t\t|\t{kwargs}\n'
              f'|\tResult:\t\t\t|\t{result}',
              f'\n+', '-' * 17, '+', '-' * 81)
        if type(result) is str:
            if result.startswith('Error: ') is True:
                logger.error(f'Function: {func.__name__}, args: {args}, kwargs {kwargs}, Result: {result[7:]}')
        return result
    return call


def async_log(func):
    """
    basic logging decorator for asynchronous Functions
    :param func: decorated function
    :return: the return of the decorated function
    """
    @wraps(func)
    async def call(*args, **kwargs):
        result = await func(*args, **kwargs)
        print(f'\n+', '-'*17, '+', '-'*81,
              f'\n|\tTime:\t\t\t|\t{datetime.now().strftime("%H:%M:%S")}\n'
              f'|\tSync:\t\t\t|\tFalse\n'
              f'|\tFunction:\t\t|\t{func.__name__}\n'
              f'|\targs:\t\t\t|\t{args}\n'
              f'|\tkwargs:\t\t\t|\t{kwargs}\n'
              f'|\tResult:\t\t\t|\t{result}',
              f'\n+', '-' * 17, '+', '-' * 81)
        if type(result) is str:
            if result.startswith('Error: ') is True:
                logger.error(f'Function: {func.__name__}, args: {args}, kwargs {kwargs}, Result: {result[7:]}')
        return result
    return call


def im_path(img: str):
    """
    appends the Image directory to the :param img
    :return: the completed path to the Image
    """
    return os_join(dirname(__file__), FILE_CFG['IMAGE_PATH'], img)


@PEPE.event
async def on_ready():
    await PEPE.change_presence(activity=Game(name="Monster Super League"), status=discord.Status.online)
    print(f'Logged in as {PEPE.user.name}')
    # check_nox.start()
    # check_titan.start()
    # ping_list = get_ping_list()
    # print(ping_list['29'])
    # print(PEPE.emojis)


@async_log
@PEPE.event
async def on_message(message: discord.Message):
    if not message.author.bot:
        await PEPE.process_commands(message)
    if message.author == PEPE.user:
        return
    if message.content[:1] == '@':
        name_list = message.content[1:].split()
        k = int(TITAN_CFG['LEVEL']) + 1

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

            if level > int(TITAN_CFG['LEVEL']):
                ping_list = get_ping_list()
                if type(ping_list) is str:
                    ping_list = {}
                element = ''
                for x in range(5):
                    elements = ['FIRE', 'DARK', 'WATER', 'WOOD', 'LIGHT']
                    if level % 5 == x:
                        element = elements[x]
                await message.add_reaction(f'element_{element.lower}:{EMOJI[element]}')
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
                        await message.author.send(f'You already have an Alarm for the requested Level {level} Titan.')
                save_ping_list(ping_list)
            else:
                await message.author.send(f'Level below current Titan Level.\nrequested Level:\t{level}\n'
                                          f'current Level:\t\t{TITAN_CFG["LEVEL"]}')


@async_log
@PEPE.command(name='restart',
              brief='Restarts the Game and/or the Emulator',
              description='Restarts the Game and/or the Emulator',
              aliases=['kill'],
              pass_context=True)
async def restart(context, handle: str='smurf', force: str=False):
    """
    Discord Function to restart the Game and/or the Emulator
    :param context: passed from discord
    :param handle: additional Arguments, restricted use
    :param force: trigger if Game restart should be bypassed and Nox should be restarted immediately, restricted use
    :return: none
    """
    handle = handle.lower()
    if handle == 'main' or force is not False:
        if str(context.author) == DISCORD_CFG['USER']:
            if handle == 'main':
                handle = MAIN
            else:
                handle = SMURF
            if force is not False:
                force = True
        else:
            await context.send('Missing permissions!')
            await context.message.add_reaction(f'missing_permissions:{EMOJI["MISSING_PERMISSIONS"]}')
            return False
    else:
        handle = SMURF
    await context.send('Restarting Emulator, please stand by...')
    rst = await msl_restart(handle, force)
    if rst is True:
        await context.send('Restart complete.')
    else:
        await context.send('Restart failed.')


@async_log
@PEPE.command(name='startup',
              brief='Starts the Game and enters the Main Screen',
              description='Restarts the Game and/or the Emulator',
              aliases=['start'],
              pass_context=True)
async def startup_handler(context, handle: str='smurf'):
    """
    Discord Function to restart the Game and/or the Emulator
    :param context: passed from discord
    :param handle: additional Arguments, restricted use
    :return: none
    """
    handle = handle.lower()
    if handle == 'main':
        if str(context.author) == DISCORD_CFG['USER']:
            handle = MAIN
        else:
            await context.send('Missing permissions!')
            await context.message.add_reaction(f'missing_permissions:{EMOJI["MISSING_PERMISSIONS"]}')
    else:
        handle = SMURF
    await context.send('Starting, please stand by...')
    start = await startup(handle)
    if start is True:
        await context.send('Startup complete')
    else:
        await context.send('Startup failed')


@async_log
@PEPE.command(name='ss',
              brief='Takes a Screenshot',
              description='Takes a Screenshot',
              aliases=['screenshot', 'SS', 'Screen', 'screen'],
              pass_context=True)
async def ss(context, *args: str):
    """
    Discord Function for taking a Screenshot, calls screen() and sends an Image to the Channel or User
    :param context: passed from Discord
    :param args: additional Arguments, restricted use
    :return: none
    """
    handle = SMURF
    image = False
    async with context.typing():
        main_flag = False
        bot_flag = False
        if str(context.author) == DISCORD_CFG['USER']:
            for arg in args:
                arg = arg.lower()
                if arg == 'main':
                    main_flag = True
                elif arg == 'bot':
                    bot_flag = True

        if bot_flag is False:
            if main_flag is True:
                handle = MAIN
            await handle.screenshot()
            image = await save_img(handle.screen, handle.file)
        if image is not False:
            await context.send(content=context.author.mention, file=File(im_path(handle.file)))
        else:
            await context.send('An Error occurred')


@async_log
@PEPE.command(name='Command',
              brief='Commands the Bots',
              description='Commands the Bots',
              aliases=['cmd', 'CMD', 'command'],
              pass_context=True,
              hidden=True)
async def cmd(context, *args: str):
    """
    Discord Function to command the Bots
    :param context: passed from Discord
    :param args: additional Arguments, restricted use
    :return: True if successful, False / Error on Error
    """
    async with context.typing():
        main_flag = False
        command = False
        if str(context.author) == DISCORD_CFG['USER']:
            for arg in args:
                arg = arg.lower()
                if arg == 'main':
                    main_flag = True
                elif arg in ['gem', 'slime']:
                    command = 'astrogem'
                elif arg in ['astromon', 'mon']:
                    command = 'astrochip'
                elif arg in ['pvp', 'league']:
                    command = 'league'
                elif arg in ['golem', 'forever', 'rare', 'dragon', 'starstone', 'start', 'stop', 'pause']:
                    command = arg
            if command is not False:
                if command in ['stop', 'pause']:
                    cmd_list = [command]
                else:
                    cmd_list = ['stop', command, 'start']
                if main_flag is True:
                    handle = MAIN
                else:
                    handle = SMURF
                if handle.bot is not False:
                    success = await command_bot(cmd_list, handle)
                    if success is True:
                        await context.message.add_reaction(f'{command}:{EMOJI[command.upper()]}')
                        await context.send(f'Executed Command:\t{command}\nmain_flag:\t{main_flag}')
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
            await context.message.add_reaction(f'missing_permissions:{EMOJI["MISSING_PERMISSIONS"]}')
            await context.send('Missing Permissions!')
            return False


@async_log
@PEPE.command(name='Goto',
              brief='Moves the Player to the Titan Screen',
              description='Moves the Player to the Titan Screen',
              aliases=['goto', 'titan', 'move'],
              pass_context=True,
              hidden=True)
async def goto(context, *args: str):
    """
    Discord Function to move the selected Player to the Titan Screen
    :param context: passed from Discord
    :param args: additional Arguments, restricted use
    :return: True if successful, False / Error on Error
    """
    async with context.typing():
        main_flag = False
        if str(context.author) == DISCORD_CFG['USER']:
            for arg in args:
                arg = arg.lower()
                if arg == 'main':
                    main_flag = True
            if main_flag is True:
                handle = MAIN
            else:
                handle = SMURF
        else:
            handle = SMURF
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


@async_log
@PEPE.command(name='Rank',
              brief='Shows the current Ranking',
              description='Shows the current Ranking',
              aliases=['rank', 'ranking', 'top5'],
              pass_context=True)
async def rank(context):
    """
    Discord Function for Ranking Screenshot, calls screen() and sends an Image to the Channel or User
    :param context: passed from Discord
    :return: none
    """
    async with context.typing():
        if titan_time() is True:
            image = await SMURF.crop_screen('rank', FILE_CFG['RANK'])
        else:
            image = await SMURF.crop_screen('rank', FILE_CFG['RANK'], FILE_CFG['LAST_TITAN'])
        if image is True:
            await context.send(content=context.author.mention, file=File(im_path(FILE_CFG['RANK'])))
        else:
            await context.send('An Error occurred.')


@async_log
@PEPE.command(name='Health',
              brief='Shows the current Titans Health',
              description='Shows the current Titans Health',
              aliases=['health'],
              pass_context=True)
async def hp(context):
    """
    Discord Function for Ranking Screenshot, calls screen() and sends an Image to the Channel or User
    :param context: passed from Discord
    :return: none
    """
    async with context.typing():
        if titan_time() is True:
            image = await SMURF.crop_screen('health', FILE_CFG['HEALTH'])
        else:
            image = await SMURF.crop_screen('health', FILE_CFG['HEALTH'], FILE_CFG['LAST_TITAN'])
        if image is True:
            await context.send(content=context.author.mention, file=File(im_path(FILE_CFG['HEALTH'])))
        else:
            await context.send('An Error occurred.')


@async_log
@PEPE.command(name='Level',
              brief='Shows the current Level and Element of the Titan',
              description='Shows the current Level and Element of the Titan',
              aliases=['level', 'element', 'Element', 'ele', 'lvl'],
              pass_context=True)
async def lvl(context):
    """
    Discord Function for Titan Level and Element
    :param context: passed from Discord
    :return: none
    """
    async with context.typing():
        await context.send(content=f'The current Titan is Level {TITAN_CFG["LEVEL"]}, '
                                   f'Element <:element_{TITAN_CFG["ELEMENT"].lower()}:{EMOJI[TITAN_CFG["ELEMENT"]]}>')


@log
def connect_adb() -> bool:
    """
    connects the Script to the NOX ADB Server
    :return: True or False, depending on Success
    """
    try:
        adb_host = AdbClient(host=ADB_CFG['HOST'], port=int(ADB_CFG['ADB_PORT']))
    except Exception as e:
        print(e)
        MSL.ADB_connected = False
    else:
        MSL.ADB_connected = True
        devices = adb_host.devices()
        for device in devices:
            for emu in [MAIN, SMURF]:
                if device.serial == f'{ADB_CFG["HOST"]}:{emu.port}':
                    emu.set_device(AdbClient.device(adb_host, device.serial))
    return MSL.ADB_connected


@async_log
async def adb_touch(handle: MSL, x: int, y: int) -> bool:
    """
    issues Touch Commands to the Device
    :param handle: Device where the Command is issued
    :param x: X-Location
    :param y: Y-Location
    :return: True or False, depending on Success
    """
    if MSL.ADB_connected is False:
        connect_adb()

    if MSL.ADB_connected is True:
        try:
            handle.device.shell(f'input tap {x} {y}')
        except Exception as e:
            print(e)
            return False
        else:
            return True


@async_log
async def command_bot(bot_cmd: list, handle: MSL) -> bool:
    button_list = list()
    button_list.append([25, 11, 'Button2', 'stop'])
    button_list.append([25, 11, 'Button3', 'pause'])
    button_list.append([25, 11, 'Button1', 'start'])
    button_list.append([75, 106, 'ComboBox1', 'league'])
    button_list.append([75, 119, 'ComboBox1', 'toc'])
    button_list.append([75, 132, 'ComboBox1', 'forever'])
    button_list.append([75, 145, 'ComboBox1', 'rare'])
    button_list.append([75, 158, 'ComboBox1', 'golem'])
    button_list.append([75, 171, 'ComboBox1', 'astrogem'])
    button_list.append([75, 184, 'ComboBox1', 'astrochip'])
    button_list.append([75, 197, 'ComboBox1', 'guardian'])
    button_list.append([75, 210, 'ComboBox1', 'starstone'])
    button_list.append([75, 223, 'ComboBox1', 'dragon'])
    hwnd = handle.bot

    for c in bot_cmd:
        c = c.lower()
        for i in button_list:
            if c in i:
                if i[2] in 'ComboBox1':
                    if i[3] == 'league':
                        i[3] = 'pvp'
                    elif i[3] == 'astrochip':
                        i[3] = 'astromon'
                    elif i[3] == 'astrogem':
                        i[3] = 'gem'
                    AUTO_IT.ControlCommand(f'[HANDLE:{hwnd}]', '', f'[ClassNN:{i[2]}]', 'SelectString',
                                           f'Farm {i[3]}')
                else:
                    clicked = AUTO_IT.ControlClick(f'[HANDLE:{hwnd}]', '', f'[ClassNN:{i[2]}]', 'primary',
                                                   1, i[0], i[1])
                    if clicked == 0:
                        return False
                sleep(0.05)
    handle.set_location('Bot')
    return True


@async_log
async def msl_restart(handle: MSL, force=False) -> bool:
    """
    restarts the MSL Game or Emulator on :param handle, :param force bypasses Game restart and restarts Nox immediately
    :return: True on Success, Error + Exception on Error
    """
    if MSL.ADB_connected is False:
        connect_adb()

    if MSL.ADB_connected is True and force is False:
        try:
            stop = handle.device.shell(f'am force-stop {MSL_PACK}')
            start = handle.device.shell(f'monkey -p {MSL_PACK} -c android.intent.category.LAUNCHER 1')
            print(f'Executing adb commands, results --> stop:{stop} start: {start}')
            logger.debug(f'Executing adb commands, results --> stop:{stop} start: {start}')
        except Exception as e:
            force = True
            print(e)
        else:
            return True
    if force is True:
        if handle.emu != '':
            success = False
            msl_find_str = f'-clone:{handle.emu}'
            try:
                msl_pid = get_pid_by_cmd(msl_find_str)
                kill(int(msl_pid), signal.SIGINT)
            except Exception as e:
                print(e)
                return False
            else:
                success = True
            finally:
                Popen([f'{NOX_CFG["PATH"]}', f'{msl_find_str}', f'-package:{MSL_PACK}', f'-lang:en'],
                      creationflags=DETACHED_PROCESS, close_fds=True)
                await asyncio.sleep(10)
                await startup(handle)
                return success
        else:
            return False


@log
def get_pid_by_cmd(cmd_line: str):
    """
    returns the PID for the commandline in :param handle
    :return: the PID
    """
    def process_cmd_lines():
        cmd_lines = {}
        for process in psutil.process_iter():
            try:
                cmd_lines[process.pid] = process.cmdline()
            except psutil.AccessDenied:
                cmd_lines[process.pid] = None
        return cmd_lines

    def to_regex(regex):
        if not hasattr(regex, "search"):
            regex = re.compile(regex)
        return regex

    regex_cmd = to_regex(cmd_line)
    for pid, cmdline in process_cmd_lines().items():
        if cmdline is not None:
            for part in cmdline:
                if regex_cmd.search(part):
                    return pid
    return False


# @tasks.loop(seconds=int(TITAN_CFG['FREQ']))
@async_log
async def check_titan():
    """
    Screenshots the Smurf Device and checks if a new Titan is up, this Function is looped
    :return: none
    """
    await PEPE.wait_until_ready()
    channel = PEPE.get_channel(int(DISCORD_CFG['CHANNEL']))
    while not PEPE.is_closed():
        if TITAN_CFG['UPDATES'] == 'ON':
            await SMURF.screenshot()
            compare = await compare_image(SMURF.screen, FILE_CFG['BUFF'])
            if titan_time() is True:
                if compare is not False:
                    level, element = await titan_level()
                    if level > int(TITAN_CFG['LEVEL']) and level is not False:
                        level = str(level)
                        ping_list = get_ping_list()
                        ping_me = ''
                        if type(ping_list) is dict and level in ping_list:
                            ping_me = '\t'.join(ping_list[level])
                        # message ='<:element_{3}:{0}>\t\t{1} Titan is up now!\t**Lv. {2}**\t\t<:element_{3}:{0}>\n{4}'\
                        #    .format(EMOJI[element], element.capitalize(), level, element.lower(), ping_me)
                        message = '<:element_{3}:{0}>\t{1} Titan is up now!\t**Lv. {2}**\t<:element_{3}:{0}>'\
                            .format(EMOJI[element], element.capitalize(), level, element.lower())
                        update_titan_cfg(LEVEL=level, ELEMENT=element)
                        async for msg in channel.history(limit=20):
                            if msg.author == PEPE.user:
                                await msg.delete()
                        await asyncio.sleep(2)
                        await SMURF.screenshot()
                        await SMURF.crop_screen('titan', FILE_CFG['TITAN'])
                        # await save_img(SMURF.screen, SMURF.file)
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
                        # TODO: get current HP from ini

                        embed = Embed(title=message, colour=colour, timestamp=datetime.utcnow())
                        embed.set_thumbnail(url='attachment://element.webp')
                        embed.add_field(name='Current HP:', value='*~WIP~*', inline=True)
                        embed.add_field(name='Max HP:', value='*~WIP~*', inline=True)
                        if ping_me != '':
                            embed.add_field(name='Requested Pings', value=ping_me, inline=False)
                        files = [File(im_path(FILE_CFG['TITAN']), filename='image.png'),
                                 File(im_path(f'Element_{element.capitalize()}.webp'), filename='element.webp')]
                        embed.set_image(url='attachment://image.png')
                        embed.set_footer(text='\u200b', icon_url='attachment://element.webp')
                        # await channel.send(content=message, file=File(im_path(SMURF.file)))
                        await channel.send(embed=embed, files=files, content=ping_me)
                elif compare is False and SMURF.location not in ['Atk', 'Test']:
                    await command_bot(['log', 'stop'], SMURF)
                    await navigate()
            elif compare is not False:
                await SMURF.screenshot()
                await save_img(SMURF.screen, FILE_CFG['LAST_TITAN'])
                compare_back = await compare_image(SMURF.screen, FILE_CFG['BACK'])
                if compare_back is not False:
                    await adb_touch(SMURF, compare_back[0], compare_back[1])
                    await command_bot(['script', 'select', 'rare', 'start'], SMURF)
        await asyncio.sleep(int(TITAN_CFG['FREQ']))


@async_log
async def attack(handle: MSL, element: str=False, team: int=False):
    # todo: create Function to Attack Titans from Titans screen
    while True:
        await handle.screenshot()
        handle.set_location('Atk')
        print(f'element: {element}\nteam:{team}')
        for image in ['battle', 'battle2']:
            image = im_path(f'{image}.png')
            compare = await compare_image(handle.screen, image)
            if compare is not False:
                x = compare[0]
                y = compare[1]
                await adb_touch(handle, x, y)


# @tasks.loop(seconds=60)
@async_log
async def check_nox():
    """
    checks if the Nox Emulators are running and starts them if they are not

    :return: None
    """
    await PEPE.wait_until_ready()
    user = PEPE.get_user(int(DISCORD_CFG['USERID']))
    while not PEPE.is_closed():
        if MAIN.bot is None or SMURF.bot is None or \
                AUTO_IT.WinExists(f'[HANDLE:{MAIN.bot}]') == 0 or AUTO_IT.WinExists(f'[HANDLE:{SMURF.bot}]') == 0:
            find_bots()
        pid = dict()
        emulators = [NOX_CFG['EMU_MAIN'], NOX_CFG['EMU_SMURF']]
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
                        await asyncio.sleep(10)
                except (ProcessLookupError, NoSuchProcess):
                    print(f'Exception occured')
                    pid[emu] = False
                    break
            if pid[emu] is False:
                print(f'Trying to start Process for {emu}')
                Popen([f'{NOX_CFG["PATH"]}', f'{msl_find_str}', f'-package:{MSL_PACK}', f'-lang:en'],
                      creationflags=DETACHED_PROCESS, close_fds=True)
                logger.critical(f'Restarting Nox - {emu}')
                if type(user) != 'NoneType':
                    await user.send(f'No PID found for {emu}, restarting Emulator')
        await asyncio.sleep(60)


@async_log
async def navigate(handle: MSL=SMURF) -> bool:
    buff = False
    i = 0
    handle.set_location('Nav')
    while buff is False:
        await handle.screenshot()
        for image in ['tap-to-start', 'tap-to-start2', 'tap-to-start-sonic', 'tap-to-start-sonic2', 'start-up-x',
                      'play', 'skip', 'tap', 'tap2', 'tap3', 'pause', 'give_up', 'give_up2', 'map', 'region_defense',
                      'clan_plaza', 'region_defense', 'view_clan', 'get_reward', 'roll_call', 'x']:
            image = im_path(f'{image}.png')
            compare = await compare_image(handle.screen, image)
            if compare is not False:
                x = compare[0]
                y = compare[1]
                adb = await adb_touch(handle, x, y)
                if adb is True:
                    break
        await asyncio.sleep(0.5)
        buff = await compare_image(handle.screen, FILE_CFG['BUFF'])
        i += 1
        if i > 100:
            return False
    return True


@async_log
async def startup(handle: MSL=SMURF) -> bool:
    play = False
    i = 0

    if MSL.ADB_connected is False:
        connect_adb()

    if MSL.ADB_connected is True:
        try:
            pid = handle.device.shell(f'pidof -s {MSL_PACK}')
            print(f'pid: {pid}')
            if pid == '':
                handle.device.shell(f'monkey -p {MSL_PACK} 1')
                await asyncio.sleep(30)
        except Exception as e:
            print(e)
            return False
    else:
        return False

    while play is False:
        play_ss = handle.screenshot()
        if play_ss is not False:
            for image in ['tap-to-start', 'tap-to-start2', 'tap-to-start-sonic', 'tap-to-start-sonic2', 'start-up-x']:
                image = im_path(f'{image}.png')
                compare = await compare_image(handle.screen, image)
                if compare is not False:
                    x = compare[0]
                    y = compare[1]
                    adb = await adb_touch(handle, x, y)
                    if adb is True:
                        break
        else:
            await msl_restart(handle, True)
        await asyncio.sleep(0.5)
        play = compare_image(handle.screen, FILE_CFG['PLAY'])
        i += 1
        if i > 100:
            return False
    return True


@log
def find_bots():
    MAIN.set_bot(0)
    SMURF.set_bot(0)
    bots = AUTO_IT.WinList('MSL')
    i = 0
    for b in bots[0]:
        handle = None
        if type(b) is str:
            if '- smurf' in b:
                handle = SMURF
            elif '- main' in b:
                handle = MAIN
            if handle is not None:
                handle.set_bot(bots[1][i])
        i += 1


@async_log
async def compare_image(img: np.ndarray, tpl: str):
    """
    compares the two given Images and returns the points if the image is found
    :param img: image to compare
    :param tpl: template to compare against
    :return: Location of the Match, False on no Match or Error + Exception on Error
    """
    accuracy = 0.95
    image_gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    template = cv2.imread(im_path(tpl))
    th, tw, tc = template.shape
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val > accuracy:
        # returns the middle of the found Image if the Template is at least {accuracy}% accurate
        return [max_loc[0] + int(tw / 2), max_loc[1] + int(th / 2)]
    else:
        return False


@log
def get_ping_list() -> dict:
    with open(FILE_CFG['PING_LIST'], mode='r') as f:
        return load(f)


@log
def save_ping_list(ping_list: dict):
    with open(FILE_CFG['PING_LIST'], mode='w') as f:
        dump(ping_list, f, sort_keys=True, indent=4)


@async_log
async def save_img(img: Image.Image, output: str) -> bool:
    try:
        img.save(im_path(output), 'PNG')
    except IOError:
        return False
    else:
        return True


@async_log
async def titan_level():
    """
    checks the Level of the Titan in the last Screenshot
    :return: Level and Element of the titan if Successful, Error + Exception on Error
    """
    await SMURF.screenshot()
    await SMURF.crop_screen(area='level')
    img = cv2.cvtColor(np.array(MSL.Level), cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0, 250, 0), (200, 255, 255))
    i_mask = mask > 0
    red = np.zeros_like(img, np.uint8)
    red[i_mask] = img[i_mask]
    ret, red = cv2.threshold(red, 150, 255, cv2.THRESH_TOZERO)
    loc = 0
    b_col = []
    for i in range(len(red[0])):
        if sum(sum(red.transpose(1, 0, 2)[i].transpose())) < 100:
            b_col.append(loc)
        loc += 1
    c_loc = []
    for i in range(len(b_col) - 1):
        gap = b_col[i + 1] - b_col[i]
        if gap > 1:
            c_loc.append([b_col[i], b_col[i + 1]])
    digit_str = ''
    digit_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    match = 0
    if len(c_loc) > 3:
        for i in c_loc[3:]:
            crop_red = red[:, i[0]:i[1]]
            for step in digit_list:
                tmp = cv2.imread(im_path(f'd_{step}.png'))
                result = cv2.matchTemplate(crop_red, tmp, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                if max_val > 0.98:
                    digit_str = digit_str + step
                    match += 1
    if match == len(c_loc) - 3:
        if digit_str.isdigit() is True:
            level = int(digit_str)
            if level % 5 == 1:
                element = 'DARK'
            elif level % 5 == 2:
                element = 'WATER'
            elif level % 5 == 3:
                element = 'WOOD'
            elif level % 5 == 4:
                element = 'LIGHT'
            elif level % 5 == 0:
                element = 'FIRE'
            else:
                element = False
        else:
            level = False
            element = False
    else:
        level = False
        element = False
    return level, element


@async_log
async def titan_hp():
    pass


@log
def titan_time() -> bool:
    """
    Checks if it's time for Titan Battles
    :return: True if it's time, otherwise False
    """
    base_battle_time = TITAN_CFG['BASE_BATTLE_TIME']
    offset = 0
    own_zone = int(TITAN_CFG['OWN_TIMEZONE'])
    clan_zone = int(TITAN_CFG['CLAN_TIMEZONE'])
    if TITAN_CFG['DST'] == 'True':
        dst = 1
    else:
        dst = 0
    if own_zone != clan_zone:
        if clan_zone >= 0 > own_zone or clan_zone < 0 <= own_zone:
            offset = own_zone - clan_zone
        elif own_zone > clan_zone >= 0 or own_zone < clan_zone <= 0:
            offset = own_zone - clan_zone
        elif clan_zone > own_zone >= 0 or clan_zone < own_zone <= 0:
            offset = -clan_zone + own_zone
    offset += dst
    first_battle = base_battle_time[0]
    second_battle = base_battle_time[1]
    start_first = int(first_battle.split('-')[0].split(':')[0])
    end_first = int(first_battle.split('-')[1].split(':')[0])
    start_second = int(second_battle.split('-')[0].split(':')[0])
    end_second = int(second_battle.split('-')[1].split(':')[0])
    # 0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, 4 = Friday, 5 = Saturday, 6 = Sunday
    weekday = calendar.day_name[date.today().weekday()]
    time = int(datetime.now().strftime('%H'))
    rel_time = time - offset
    if rel_time < 0:
        rel_time += 24
    elif rel_time > 24:
        rel_time -= 24
    today = datetime.now().strftime('%m/%d/%Y')

    if weekday == 'Monday' and TITAN_CFG['LAST_RESET'] != today:
        update_titan_cfg(LEVEL='1', ELEMENT='DARK', LAST_RESET=today)
        save_ping_list({})

    if start_first <= rel_time < end_first:
        if offset > 0 and weekday != 'Sunday' or offset < 0 and weekday != 'Saturday':
            return True
    elif start_second <= rel_time < end_second:
        if offset > 0 and weekday != 'Monday' or offset < 0 and weekday != 'Sunday':
            return True
    return False


@log
def update_titan_cfg(**kwargs: str):
    """
    updates the Titan Section in the configfile with the given keyword arguments
    :param kwargs:
    :return:
    """
    for arg in kwargs:
        TITAN_CFG[arg] = kwargs[arg]
    CFG.write()


if __name__ == '__main__':
    connect_adb()
    PEPE.loop.create_task(check_nox())
    PEPE.loop.create_task(check_titan())
    PEPE.run(DISCORD_CFG['TOKEN'])
