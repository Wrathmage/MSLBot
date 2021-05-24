from io import BytesIO
from PIL import Image
from logger import logger
from filetools import im_path
from imagetools import save_img
from ppadb.device import Device


class MSL:
    """
    Standard Class for all Players and Functions regarding them
    """
    ADB_connected = False
    Level = None
    HP = None

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
            img_var = None
            area = area.lower()
            if area == 'rank':
                area = [607, 133, 791, 398]
            elif area == 'level':
                area = [15, 450, 80, 470]
                img_var = 'Level'
            elif area == 'health':
                area = [17, 472, 610, 540]
            elif area == 'hp':
                area = [69, 525, 162, 534]
                img_var = 'HP'
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
                if type(output) is str:
                    if await save_img(img_crop, output) is True:
                        return True
                    else:
                        return False
                elif img_var is not False:
                    setattr(MSL, img_var, img_crop)
                    return True
            else:
                return False

    def __str__(self):
        """
        :return: all Items of the Player
        """
        return f'name:\t\t{self.name}\nport:\t\t{self.port}\nemu:\t\t{self.emu}\nfile:\t\t{self.file}\n' \
               f'bot:\t{self.bot}\ndevice:\t\t{self.device}\nscreen:\t\t{self.screen}\nlocation:\t{self.location}'
