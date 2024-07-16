import numpy as np
import os
from base64 import b64decode
from PIL import Image
from io import BytesIO
import browser

ORI_WIDTH = browser.CANVAS_ORI_WIDTH
ORI_HEIGHT = browser.CANVAS_ORI_HEIGHT
RATIO = browser.RATIO


def _screenshot_from_browser(crop_params=None):
  data = browser.screenshot_as_base64()
  png = b64decode(data)
  img = Image.open(BytesIO(png))
  img.save('./screenshot/last.png')  # debug
  ratio = RATIO
  if crop_params is None:
    return [img]

  for i in range(len(crop_params)):
    x1, y1, x2, y2 = crop_params[i]
    crop_params[i] = (x1 // ratio, y1 // ratio, x2 // ratio, y2 // ratio)
  imgs = [img.crop(param) for param in crop_params]
  imgs[0].save('./screenshot/last.crop.png')  # debug
  return imgs


def _proc(img, save_name=None, gray_scale=True):
  img = img.convert("L") if gray_scale else img  # better for ocr
  if save_name:
    fname = "./screenshot/{}.png".format(save_name)
    dname = fname.rsplit("/", 1)[0]
    if not os.path.exists(dname):
      os.mkdir(dname)
    img.save(fname)
  return np.array(img)


def fullscreen(save_name=None):
  img = _screenshot_from_browser()[0]
  return _proc(img, gray_scale=False, save_name=save_name)
# fullscreen(save_name="wave_0")


def chatbox(line=None):
  height = 160
  y1 = 855
  if line is not None:
    height //= 2
  if line == 2:
    y1 = 950
  img = _screenshot_from_browser(crop_params=[(0, y1, ORI_WIDTH, y1+height)])[0]
  return _proc(img, save_name="chatbox_{}".format(line))


def bottom_screen(save_name=None):
  y1 = 690
  img = _screenshot_from_browser(crop_params=[(0, y1, ORI_WIDTH, ORI_HEIGHT)])[0]
  return _proc(img, save_name=save_name)
# bottom_screen(save_name="0")


def rival_screen():
  img = _screenshot_from_browser(crop_params=[(25, 320, 600, 400)])[0]
  return _proc(img, gray_scale=False)


def wave_nos():
  x1 = 1840
  l1_y1, l2_y1 = 0, 100
  height = 55
  crop_params = [(x1, l1_y1, ORI_WIDTH-10, l1_y1+height),
                 (x1, l2_y1, ORI_WIDTH-10, l2_y1+height)]
  imgs = _screenshot_from_browser(crop_params=crop_params)

  return [_proc(img, save_name="wave_no_{}".format(idx))
          for idx, img in enumerate(imgs)]


def fight_moves():
  move1_x1, move1_y1 = 100, 860
  move2_x1, move2_y1 = 705, move1_y1
  move3_x1, move3_y1 = move1_x1, 950
  move4_x1, move4_y1 = move2_x1, move3_y1
  move_width = 500
  move_height = 80
  crop_params = [(move1_x1, move1_y1, move1_x1+move_width, move1_y1+move_height),
                 (move2_x1, move2_y1, move2_x1+move_width, move2_y1+move_height),
                 (move3_x1, move3_y1, move3_x1+move_width, move3_y1+move_height),
                 (move4_x1, move4_y1, move4_x1+move_width, move4_y1+move_height)]
  imgs = _screenshot_from_browser(crop_params=crop_params)
  return [_proc(img, save_name=f'{idx}') for idx, img in enumerate(imgs)]
# action_moves()


def learn_moves(save_prefix=None):
  x1, x2 = 870, 1400
  y1, y2 = 200, 572
  move_height = (y2-y1) // 4
  crop_params = [(x1, y1+move_height*i, x2, y1+move_height*(i+1)) for i in range(4)]
  imgs = _screenshot_from_browser(crop_params=crop_params)
  return [_proc(img, save_name="{}_{}".format(save_prefix, idx) if save_prefix else None)
          for idx, img in enumerate(imgs)]
# learn_moves(save_prefix="0")


def pokemons(double=None, debug=True):
  width, height = 320, 70
  l_x1, r_x1 = 190, 970
  if double is True:
    p1_y1 = 210
    p2_y1 = 600
    p3_y1 = 120
    y_span = 215
    crop_params = [(l_x1, p1_y1, l_x1 + width, p1_y1 + height),
                   (l_x1, p2_y1, l_x1 + width, p2_y1 + height)]
    crop_params.extend([(r_x1, p3_y1 + i*y_span,
                         r_x1 + width, p3_y1 + i*y_span + height) for i in range(4)])
  else:
    l_y1, r_y2 = 256, 256
    y_span = 165
    crop_params = [(l_x1, l_y1, l_x1 + width, l_y1 + height)]
    crop_params.extend([(r_x1, r_y2 + i*y_span,
                         r_x1+width, r_y2 + i*y_span + height)
                        for i in range(-1, 4)])
  imgs = _screenshot_from_browser(crop_params=crop_params)
  return [_proc(img,
                save_name="pokemon/{}".format(idx) if debug else None)
          for idx, img in enumerate(imgs)]


def ball_cursor():
  x1, y1 = 1250, 155
  x2, y2 = 1320, 755
  img = _screenshot_from_browser(crop_params=[(x1, y1, x2, y2)])[0]
  return _proc(img)


def rewards(cnt=3, debug=True):
  y1, y2 = 470, 515
  width = ORI_WIDTH // (cnt+2)
  crop_params = [(i * width, y1, (i+1) * width, y2) for i in range(1, cnt+1)]

  imgs = _screenshot_from_browser(crop_params=crop_params)

  return [_proc(img, save_name="reward/{}".format(index) if debug else None)
          for index, img in enumerate(imgs)]


def pokemons_sidebar(x1=1430, y1=50, debug=True):
  last_y2 = 1050
  height = 100
  if y1 % 50 > 0:
    y1 = y1 // 50 * 50
  crop_params = [(x1, y, ORI_WIDTH, y+height) for y in range(y1, last_y2, height)]
  imgs = _screenshot_from_browser(crop_params=crop_params)

  return [_proc(img, save_name="sidebar/{}".format(idx) if debug else None)
          for idx, img in enumerate(imgs)]
