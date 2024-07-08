import pyautogui
import numpy as np
import os

ScreenX1 = 30
ScreenX2 = 1122
ScreenY1 = 120
ScreenY2 = 725

BoxX1 = 50
BoxX2 = ScreenX2
BoxY1 = 590
BoxY2 = ScreenY2


def _proc(img, ratio=2, save_name=None, gray_scale=True):
  img = img.convert("L") if gray_scale else img  # better for ocr
  img = img.resize((img.size[0] // ratio, img.size[1] // ratio))
  if save_name:
    fname = "./screenshot/{}.png".format(save_name)
    dname = fname.rsplit("/", 1)[0]
    if not os.path.exists(dname):
      os.mkdir(dname)
    img.save(fname)
  return np.array(img)


def fullscreen(save_name=None):
  img = pyautogui.screenshot(region=(ScreenX1, ScreenY1, ScreenX2 - ScreenX1, ScreenY2 - ScreenY1))
  return _proc(img, ratio=1, gray_scale=False,
               save_name=save_name)
# fullscreen(save_name="wave_0")


def chatbox(line=None):
  y1 = BoxY1
  y_len = BoxY2 - BoxY1
  if line == 2:
    y1 = (BoxY1 + BoxY2) // 2
    y_len //= 2
  img = pyautogui.screenshot(region=(BoxX1, y1, BoxX2 - BoxX1, y_len))
  return _proc(img, save_name="chatbox_{}".format(line))


def bottom_screen(save_name=None):
  y1 = 510
  img = pyautogui.screenshot(region=(ScreenX1, y1, ScreenX2 - ScreenX1, ScreenY2 - y1))
  return _proc(img, ratio=1, save_name=save_name)
# bottom_screen(save_name="0")


def rival_screen():
  y1 = 200
  y2 = 415
  img = pyautogui.screenshot(region=(ScreenX1, y1, ScreenX2 - ScreenX1, y2 - y1))
  return _proc(img, ratio=1, gray_scale=False)


def wave_no(line=1):
  x1 = 1080
  y1 = ScreenY1
  if line == 2:
    y1 = 172
  y_len = 150 - ScreenY1

  img = pyautogui.screenshot(region=(x1, y1, ScreenX2 - x1, y_len)).convert("L")

  return _proc(img, ratio=1, save_name="wave_no_{}".format(line))


def action_moves():
  move1_x1 = BoxX1
  move1_y1 = BoxY1
  move4_x1 = (BoxX1 + BoxX2) // 3
  move4_y1 = (BoxY1 + BoxY2) // 2
  x_len = move4_x1 - move1_x1
  y_len = move4_y1 - move1_y1

  img = pyautogui.screenshot(region=(BoxX1, BoxY1, BoxX2 - BoxX1, BoxY2 - BoxY1))

  crop_params = [(0, 0, x_len, y_len),
                 (x_len, 0, x_len * 2, y_len),
                 (0, y_len, x_len, y_len * 2),
                 (x_len, y_len, x_len * 2, y_len * 2)]
  return [_proc(img.crop(param)) for param in crop_params]


def learn_moves(save_prefix=None):
  # TODO
  x1 = 515
  y1 = 233
  x2 = 760
  y2 = 442
  img = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))

  move_y_len = (y2-y1) // 4
  crop_params = [(0, move_y_len*i, x2-x1, move_y_len*(i+1)) for i in range(4)]
  return [_proc(img.crop(param), save_name="{}_{}".format(save_prefix, idx) if save_prefix else None) for idx, param in enumerate(crop_params)]
# learn_moves(save_prefix="0")


def pokemons(double=None, debug=True):
  img = pyautogui.screenshot()

  # TODO value
  x_len = 360
  y_len = 90

  x1 = 260
  x2 = 1160
  if double is True:
    y1 = 460
    y2 = 900
    y3 = 355
    y_span = 605 - 360
    crop_params = [(x1, y1, x1 + x_len, y1 + y_len),
                   (x1, y2, x1 + x_len, y2 + y_len)]
    crop_params.extend([(x2, y3 + i * y_span, x2 + x_len, y3 + i * y_span + y_len) for i in range(4)])
  else:
    y2 = 520
    y_span = 190
    crop_params = [(x1, y2, x1 + x_len, y2 + y_len)]
    crop_params.extend([(x2, y2 + i * y_span, x2 + x_len, y2 + i * y_span + y_len) for i in range(-1, 4)])

  return [_proc(img.crop(param),
                save_name="pokemon/{}".format(index) if debug else None)
          for index, param in enumerate(crop_params)]


def ball_cursor():
  # TODO
  x1 = 750
  y1 = 210
  x2 = 785
  y2 = 535
  img = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1)).convert("L")

  return _proc(img, ratio=1)


def rewards(cnt=3, debug=True):
  # TODO
  y1 = 385
  y2 = 415
  img = pyautogui.screenshot(region=(BoxX1, y1, BoxX2, y2 - y1))

  x_len = img.size[0] // (cnt+2)
  crop_params = [(i * x_len, 0, (i + 1) * x_len, img.size[1]) for i in range(1, cnt+1)]

  return [_proc(img.crop(param),
                ratio=1,
                save_name="reward_{}".format(index) if debug else None)
          for index, param in enumerate(crop_params)]


def pokemons_sidebar(debug=True):
  # TODO
  x1 = 790
  y1 = 160
  x_len = ScreenX2 - x1
  y_len = 215 - 160

  img = pyautogui.screenshot(region=(x1, y1, ScreenX2 - x1, ScreenY2 - y1))

  crop_params = [(0, i*y_len, x_len, (i+1)*y_len) for i in range(10)]

  return [_proc(img.crop(param),
                save_name="sidebar/{}".format(index) if debug else None)
          for index, param in enumerate(crop_params)]
