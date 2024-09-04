import time
from paddleocr import PaddleOCR

import screenshot
import text
from logger import logger
from config import conf

engine = PaddleOCR(
  use_gpu=False,
  use_angle_cls=False,
  lang="en",
  det_model_dir="./infer_model/en_PP-OCRv3_det_slim_infer",
  rec_model_dir="./infer_model/en_PP-OCRv3_rec_slim_infer",
  show_log=False,
)


def ocr(img, det=True):
  """

  :param img: np.array
  :param det: use text detection or not, if False, loc list will not exist in return
  :return: list[list[tuple(str, float, list[4*list[2]])]] =>
           img_idx[text_idx[(text, score, [ul[x,y], ur[x,y], lr[x,y], ll[x,y]])]]
           * ul=upper left, ur=upper right, lr=lower right, ll=lower left
  """
  _start = time.time()  # cal time
  if isinstance(img, list):  # maybe bug in paddle, return cnt not equal list cnt
    res = [engine.ocr(i, det=det, cls=False)[0] for i in img]
  else:
    res = engine.ocr(img, det=det, cls=False)

  if det:
    for img_idx in range(len(res)):
      if res[img_idx] is None:
        continue
      for text_idx in range(len(res[img_idx])):
        if res[img_idx][text_idx] is None:
          continue
        tmp = res[img_idx][text_idx]
        res[img_idx][text_idx] = (tmp[1][0], tmp[1][1], tmp[0])

  _end = time.time()  # cal time
  return res, _end - _start


def fullscreen():
  res, t = ocr(screenshot.fullscreen())
  logger.debug("fullscreen: {} ({:.2f})".format(res[0], t))


def chatbox(line=None):
  res, t = ocr(screenshot.chatbox(line=line))
  texts = [p[0].strip() for p in res[0] if p[0].strip() != ""]
  logger.debug("chatbox({}): {} ({:.2f})".format(line, texts, t))
  return texts


def bottom_screen():
  res, t = ocr(screenshot.bottom_screen())
  if res[0] is None:
    logger.debug("texts: {} ({:.2f}s)".format(None, t))
    return []
  texts = [p[0].strip() for p in res[0] if p[0].strip() != ""]
  logger.debug("texts: {} ({:.2f}s)".format(texts, t))
  return texts


def bottom_screen_with_chat():
  res, t = ocr(screenshot.bottom_screen_with_chat())
  if res[0] is None:
    logger.debug("texts: {} ({:.2f}s)".format(None, t))
    return [], False
  texts = [p[0].strip() for p in res[0] if p[0].strip() != ""]
  trainer = ""
  if res[1] is not None:
    chat = res[1][0]
    logger.debug("chat ocr: {}".format(res[1]))
    x1_max, y1_max, y2_min = 28/conf.RESOLUTION_SCALE, 16/conf.RESOLUTION_SCALE, 54/conf.RESOLUTION_SCALE
    if (chat[2][0][0] <= x1_max and chat[2][0][1] <= y1_max and chat[2][-1][1] >= y2_min
            and 3 <= len(chat[0].strip()) <= 30):
      trainer = chat[0].strip()
  logger.debug("texts: {}, trainer: {} ({:.2f}s)".format(texts, trainer, t))
  return texts, trainer != ""


def fight_moves():
  res, t = ocr(screenshot.fight_moves(), det=False)
  names = [p[0][0].replace("(", "[").rsplit("[")[0].strip() for p in res if p[0][0].strip() != ""]
  logger.debug("moves: {} ({:.2f}s)".format(names, t))
  return names


def learn_moves():
  res, t = ocr(screenshot.learn_moves(), det=False)
  names = [p[0][0].replace("(", "[").rsplit("[")[0].strip() for p in res if p[0][0].strip() != ""]
  logger.debug("moves: {} ({:.2f}s)".format(names, t))
  if len(names) < 4:
    raise Exception("Not enough moves: {}, res: {}".format(names, res))

  return names
# learn_moves()


def pokemons_name(double=None):
  res, t = ocr(screenshot.pokemons_name(double=double), det=False)
  names = [p[0][0].strip(" .").replace("1", "l") for p in res]
  logger.debug("pokemons({}): {} ({:.2f}s)".format(2 if double else 1, names, t))
  if text.check_pokemons_correctness(names) is False and double is None:
    logger.debug("pokemon names incorrect, try double")
    doubles = pokemons_name(double=True)
    return names if len(names) > len(doubles) else doubles
  return names


def pokemons_hp(double=None) -> list[str]:
  res, t = ocr(screenshot.pokemons_hp(double=double), det=False)
  logger.debug("pokemons hp: {} ({:.2f}s)".format(res, t))
  return [r[0].strip() for r in res]


def rewards(cnt=3):
  res, t = ocr(screenshot.rewards(cnt=cnt), det=True)
  names = []
  for idx, reward in enumerate(res):
    if reward is None:
      raise Exception("reward null, idx: {}".format(idx))
    name = " ".join(t[0].strip("-. ") for t in reward)
    names.append(name)
  logger.debug("rewards: {} ({:.2f}s)".format(names, t))
  names = [name for name in names if name != ""]
  if len(names) < cnt:
    raise Exception("Not enough reward: {}/{}".format(len(names), cnt))
  return names
# rewards(cnt=4)


def wave_no():
  res, t = ocr(screenshot.wave_nos(), det=False)
  logger.debug("wave no ocr: {} ({:.2f}s)".format(res, t))

  try:
    wave = res[0][0]
    no1 = (abs(int(wave[0].strip(".:-= "))), wave[1])
  except ValueError:
    no1 = (-1, 0)

  try:
    wave = res[1][0]
    no2 = (abs(int(wave[0].strip(".:- "))), wave[1])
  except ValueError:
    no2 = (-1, 0)

  no = no1 if no1[1] > no2[1] else no2
  logger.debug("wave no: {}({:.3f})".format(no[0], no[1]))

  min_score = 0.4  # TODO
  if no[1] < min_score:
    raise Exception("Not found wave no: {}".format(no))

  return no


def pokemons_sidebar(x1=1430, y1=50):
  res, t = ocr(screenshot.pokemons_sidebar(x1, y1), det=False)
  names = [p[0][0].strip() for p in res if p and p[0][0].strip() != ""]
  logger.debug("pokemons sidebar: {} ({:.2f}s)".format(names, t))
  return names
# pokemons_sidebar()


def egg_num():
  res, t = ocr(screenshot.egg_num(), det=False)
  logger.debug("egg_num: {} ({:.2f}s)".format(res, t))
  if res[0] is None:
    return None
  num = res[0][0][0].strip()
  if num == "":
    return None
  return int(res[0][0][0].strip())
