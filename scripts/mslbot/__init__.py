import globals as g
from logger import async_log, log
from asyncio import sleep
from classes import MSL


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
                    g.AUTO_IT.ControlCommand(f'[HANDLE:{hwnd}]', '', f'[ClassNN:{i[2]}]', 'SelectString',
                                             f'Farm {i[3]}')
                else:
                    clicked = g.AUTO_IT.ControlClick(f'[HANDLE:{hwnd}]', '', f'[ClassNN:{i[2]}]', 'primary',
                                                     1, i[0], i[1])
                    if clicked == 0:
                        return False
                await sleep(0.05)
    handle.set_location('Bot')
    return True


@log
def find_bots():
    g.MAIN.set_bot(0)
    g.SMURF.set_bot(0)
    bots = g.AUTO_IT.WinList('MSL')
    i = 0
    for b in bots[0]:
        handle = None
        if type(b) is str:
            if '- smurf' in b:
                handle = g.SMURF
            elif '- main' in b:
                handle = g.MAIN
            if handle is not None:
                handle.set_bot(bots[1][i])
        i += 1
