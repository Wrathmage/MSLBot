from cv2 import COLOR_BGR2GRAY, COLOR_RGB2GRAY, cvtColor, imread, matchTemplate, minMaxLoc, TM_CCOEFF_NORMED
from PIL import Image, ImageFile
from numpy import array, ndarray
from logger import async_log
from filetools import im_path

ImageFile.LOAD_TRUNCATED_IMAGES = True


@async_log
async def save_img(img: Image.Image, output: str) -> bool:
    try:
        img.save(im_path(output), 'PNG')
    except IOError:
        return False
    else:
        return True


@async_log
async def compare_image(img: ndarray, tpl: str):
    """
    compares the two given Images and returns the points if the image is found
    :param img: image to compare
    :param tpl: template to compare against
    :return: Location of the Match, False on no Match or Error + Exception on Error
    """
    accuracy = 0.95
    image_gray = cvtColor(array(img), COLOR_RGB2GRAY)
    template = imread(im_path(tpl))
    th, tw, tc = template.shape
    template_gray = cvtColor(template, COLOR_BGR2GRAY)
    result = matchTemplate(image_gray, template_gray, TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = minMaxLoc(result)
    if max_val > accuracy:
        # returns the middle of the found Image if the Template is at least {accuracy}% accurate
        return [max_loc[0] + int(tw / 2), max_loc[1] + int(th / 2)]
    else:
        return False
