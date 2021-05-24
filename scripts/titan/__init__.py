import globals as g
from cv2 import COLOR_BGR2RGB, COLOR_BGR2HSV, cvtColor, imread, inRange, matchTemplate, minMaxLoc, threshold,\
    THRESH_TOZERO, TM_CCOEFF_NORMED
from numpy import array, uint8, zeros_like
from calendar import day_name
from datetime import datetime, date
from classes import MSL
from logger import async_log, log
from filetools import get_hp_from_ini, im_path, save_ping_list, update_titan_cfg


@async_log
async def titan_level():
    """
    checks the Level of the Titan in the last Screenshot
    :return: Level and Element of the titan if Successful, Error + Exception on Error
    """
    await g.SMURF.screenshot()
    await g.SMURF.crop_screen(area='level')
    img = cvtColor(array(MSL.Level), COLOR_BGR2RGB)
    hsv = cvtColor(img, COLOR_BGR2HSV)
    mask = inRange(hsv, (0, 250, 0), (200, 255, 255))
    i_mask = mask > 0
    red = zeros_like(img, uint8)
    red[i_mask] = img[i_mask]
    ret, red = threshold(red, 150, 255, THRESH_TOZERO)
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
                tmp = imread(im_path(f'd_{step}.png'))
                result = matchTemplate(crop_red, tmp, TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = minMaxLoc(result)
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


@log
def titan_time() -> bool:
    """
    Checks if it's time for Titan Battles
    :return: True if it's time, otherwise False
    """
    base_battle_time = g.TITAN_CFG['BASE_BATTLE_TIME']
    offset = 0
    own_zone = int(g.TITAN_CFG['OWN_TIMEZONE'])
    clan_zone = int(g.TITAN_CFG['CLAN_TIMEZONE'])
    if g.TITAN_CFG['DST'] == 'True':
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
    weekday = day_name[date.today().weekday()]
    time = int(datetime.now().strftime('%H'))
    rel_time = time - offset
    if rel_time < 0:
        rel_time += 24
    elif rel_time > 24:
        rel_time -= 24
    today = datetime.now().strftime('%m/%d/%Y')

    if weekday == 'Monday' and g.TITAN_CFG['LAST_RESET'] != today:
        update_titan_cfg(LEVEL='1', ELEMENT='DARK', LAST_RESET=today)
        save_ping_list({})

    if start_first <= rel_time < end_first:
        if offset > 0 and weekday != 'Sunday' or offset < 0 and weekday != 'Saturday':
            return True
    elif start_second <= rel_time < end_second:
        if offset > 0 and weekday != 'Monday' or offset < 0 and weekday != 'Sunday':
            return True
    return False


@async_log
async def titan_max_hp(level: int) -> int:
    """
    Gets the max HP for the given Titan from the ini File
    :param level: (int) Level of the titan to check for
    :return: (int) max HP of that Titan
    """
    hp_dict = get_hp_from_ini()
    if level % 5 == 0:
        level_key = level - 4
    else:
        level_key = level - (level % 5 - 1)
    return int(float(hp_dict[str(level_key)])*1_000_000)


@async_log
async def titan_hp():
    """
    checks the HP of the Titan in the last Screenshot
    :return: (int) HP of the titan if Successful, False on Error
    """
    await g.SMURF.screenshot()
    await g.SMURF.crop_screen(area='hp')
    img = cvtColor(array(MSL.HP), COLOR_BGR2RGB)
    hsv = cvtColor(img, COLOR_BGR2HSV)
    mask = inRange(hsv, (0, 250, 0), (200, 255, 255))
    i_mask = mask > 0
    red = zeros_like(img, uint8)
    red[i_mask] = img[i_mask]
    ret, red = threshold(red, 150, 255, THRESH_TOZERO)
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
    if len(c_loc) > 2:
        x = 0
        for i in c_loc[2:]:
            x += 1
            crop_red = red[:, i[0]:i[1]]
            for step in digit_list:
                tmp = imread(im_path(f'h_{step}.png'))
                result = matchTemplate(crop_red, tmp, TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = minMaxLoc(result)
                if max_val > 0.85:
                    digit_str = digit_str + step
                    match += 1
    if match == len(c_loc) - 2:
        if digit_str.isdigit() is True:
            hp = int(digit_str)
        else:
            hp = False
    else:
        hp = False
    return hp
