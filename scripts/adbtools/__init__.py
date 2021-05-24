import globals as g
from os import kill
from re import compile
from signal import SIGINT
from logger import async_log, log
from psutil import AccessDenied, process_iter
from asyncio import sleep
from classes import MSL
from filetools import im_path
from imagetools import compare_image
from subprocess import Popen
from ppadb.client import Client as AdbClient


@log
def adb_connect() -> bool:
    """
    connects the Script to the NOX ADB Server
    :return: True or False, depending on Success
    """
    try:
        adb_host = AdbClient(host=g.ADB_CFG['HOST'], port=int(g.ADB_CFG['ADB_PORT']))
    except Exception as e:
        print(e)
        MSL.ADB_connected = False
    else:
        MSL.ADB_connected = True
        devices = adb_host.devices()
        for device in devices:
            for emu in [g.MAIN, g.SMURF]:
                if device.serial == f'{g.ADB_CFG["HOST"]}:{emu.port}':
                    emu.set_device(AdbClient.device(adb_host, device.serial))
    return MSL.ADB_connected


@async_log
async def adb_touch(handle, x: int, y: int) -> bool:
    """
    issues Touch Commands to the Device
    :param handle: Device where the Command is issued
    :param x: X-Location
    :param y: Y-Location
    :return: True or False, depending on Success
    """
    if MSL.ADB_connected is False:
        adb_connect()

    if MSL.ADB_connected is True:
        try:
            handle.device.shell(f'input tap {x} {y}')
        except Exception as e:
            print(e)
            return False
        else:
            return True


@async_log
async def msl_restart(handle: MSL, force=False) -> bool:
    """
    restarts the MSL Game or Emulator on :param handle, :param force bypasses Game restart and restarts Nox immediately
    :return: True on Success, Error + Exception on Error
    """
    if MSL.ADB_connected is False:
        adb_connect()

    if MSL.ADB_connected is True and force is False:
        try:
            handle.device.shell(f'am force-stop {g.MSL_PACK}')
            handle.device.shell(f'monkey -p {g.MSL_PACK} -c android.intent.category.LAUNCHER 1')
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
                kill(int(msl_pid), SIGINT)
            except Exception as e:
                print(e)
                return False
            else:
                success = True
            finally:
                Popen([f'{g.NOX_CFG["PATH"]}', f'{msl_find_str}', f'-package:{g.MSL_PACK}', f'-lang:en'],
                      creationflags=g.DETACHED_PROCESS, close_fds=True)
                await sleep(10)
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
        for process in process_iter():
            try:
                cmd_lines[process.pid] = process.cmdline()
            except AccessDenied:
                cmd_lines[process.pid] = None
        return cmd_lines

    def to_regex(regex):
        if not hasattr(regex, "search"):
            regex = compile(regex)
        return regex

    regex_cmd = to_regex(cmd_line)
    for pid, cmdline in process_cmd_lines().items():
        if cmdline is not None:
            for part in cmdline:
                if regex_cmd.search(part):
                    return pid
    return False


@async_log
async def navigate(handle: MSL=g.SMURF) -> bool:
    buff = False
    i = 0
    handle.set_location('Nav')
    while buff is False:
        await handle.screenshot()
        for image in ['tap-to-start', 'tap-to-start2', 'tap-to-start-sonic', 'tap-to-start-sonic2', 'start-up-x',
                      'play', 'play2', 'skip', 'tap', 'tap2', 'tap3', 'tap4', 'tap5', 'give_up2', 'give_up', 'pause',
                      'map', 'region_defense', 'view_clan', 'clan_plaza', 'get_reward', 'x', 'roll_call']:
            image = im_path(f'{image}.png')
            compare = await compare_image(handle.screen, image)
            if compare is not False:
                x = compare[0]
                y = compare[1]
                adb = await adb_touch(handle, x, y)
                if adb is True:
                    break
        await sleep(0.5)
        buff = await compare_image(handle.screen, g.FILE_CFG['BUFF'])
        i += 1
        if i > 100:
            return False
    return True


@async_log
async def startup(handle: MSL=g.SMURF) -> bool:
    play = False
    i = 0

    if MSL.ADB_connected is False:
        adb_connect()

    if MSL.ADB_connected is True:
        try:
            pid = handle.device.shell(f'pidof -s {g.MSL_PACK}')
            print(f'pid: {pid}')
            if pid == '':
                handle.device.shell(f'monkey -p {g.MSL_PACK} 1')
                await sleep(30)
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
        await sleep(0.5)
        play = compare_image(handle.screen, g.FILE_CFG['PLAY'])
        i += 1
        if i > 100:
            return False
    return True
