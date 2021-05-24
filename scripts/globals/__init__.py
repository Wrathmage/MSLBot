from classes import MSL
from configobj import ConfigObj
from filetools import cfg_path
from win32com.client import Dispatch

CFG = ConfigObj(cfg_path('config.ini'))
ADB_CFG = CFG['ADB']
NOX_CFG = CFG['NOX']
FILE_CFG = CFG['FILE']
PROFILES = CFG['BOTPROFILES']
TITAN_CFG = CFG['TITAN']
DISCORD_CFG = CFG['DISCORD'][CFG['CONFIG_MODE']]
EMOJI = DISCORD_CFG['EMOJI']
AUTO_IT = Dispatch("AutoItX3.Control")
MSL_PACK = 'com.ftt.msleague_gl'
DETACHED_PROCESS = 8

MAIN = MSL(NOX_CFG['MAIN'], ADB_CFG['MAIN_PORT'], NOX_CFG['EMU_MAIN'], FILE_CFG['MAIN_SCREEN'])
SMURF = MSL(NOX_CFG['SMURF'], ADB_CFG['SMURF_PORT'], NOX_CFG['EMU_SMURF'], FILE_CFG['SMURF_SCREEN'])
