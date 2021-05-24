import globals as g
from json import load, dump
from pathlib import Path


def cfg_path(ini: str):
    """
    appends the Image directory to the :param img
    :return: the completed path to the Image
    """
    return str(Path(__file__).parent.parent.parent.joinpath('config/', ini))


def im_path(img: str):
    """
    appends the Image directory to the :param img
    :return: the completed path to the Image
    """
    return str(Path(__file__).parent.parent.parent.joinpath(g.FILE_CFG['IMAGE_PATH'], img))


def get_hp_from_ini() -> dict:
    with open(cfg_path(g.FILE_CFG['TITAN_HP']), mode='r') as f:
        return load(f)


def get_ping_list() -> dict:
    with open(cfg_path(g.FILE_CFG['PING_LIST']), mode='r') as f:
        return load(f)


def save_ping_list(ping_list: dict):
    with open(cfg_path(g.FILE_CFG['PING_LIST']), mode='w') as f:
        dump(ping_list, f, sort_keys=True, indent=4)


def update_titan_cfg(**kwargs: str):
    """
    updates the Titan Section in the configfile with the given keyword arguments
    :param kwargs:
    :return:
    """
    for arg in kwargs:
        g.TITAN_CFG[arg] = kwargs[arg]
    g.CFG.write()
