import time
import numpy as np
from PIL import Image
import cv2

import screenshot
from logger import logger


def ball_cursor_index():
  _start = time.time()  # cal time

  # only screenshot cursor section
  img = screenshot.ball_cursor()

  # divide section into 6 parts (Poke/Great/Ultra/Rogue/Master/Cancel)
  # if the cursor is not on the part, its value will not be 255(white)
  part_size = img.shape[0] // 6
  white_counts = [0] * 6
  for i in range(6):
    start_row = i * part_size
    end_row = min((i + 1) * part_size, img.shape[0])
    white_counts[i] = np.count_nonzero(img[start_row: end_row] == 255)
  index = np.argmax(white_counts)

  _end = time.time()  # cal time
  logger.debug("ball cursor index: {}({:.3f})".format(index, _end - _start))
  return index


def find_icon(img, icon_path, threshold=0.7, find_all=False, save_name=None):
  """
  :param img: screenshot
  :param icon_path: it must be part of img, cannot be resized!
  :param threshold: cv score threshold
  :param save_name: only save when matched
  :return:
    matched_cnt if find_all=True, return matched count
                if find_all=False, return 1 if matched else 0
  """
  icon = Image.open(icon_path)
  icon = icon.resize((icon.size[0] // 2, icon.size[1] // 2))  # TODO
  icon = np.array(icon.convert("RGB"))
  w, h = icon.shape[:2]
  # logger.debug("icon shape: {}x{}, img shape: {}".format(w, h, img.shape[:2]))

  # Convert to grayscale (optional)
  gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  gray_icon = cv2.cvtColor(icon, cv2.COLOR_BGR2GRAY)

  # Apply Canny edge detection
  edges_img = cv2.Canny(gray_img, 50, 150)
  edges_icon = cv2.Canny(gray_icon, 50, 150)
  # Image.fromarray(edges_img).show()
  # Image.fromarray(edges_icon).show()

  # Template matching
  result = cv2.matchTemplate(edges_img, edges_icon, cv2.TM_CCOEFF_NORMED)
  _, max_score, _, max_loc = cv2.minMaxLoc(result)

  x, y = max_loc
  boxes = [(x, y, x + w, y + h)]
  # logger.debug("icon max score: {}({})".format(boxes[0], max_score))

  if max_score < threshold:
    return 0
  elif find_all is False and save_name is None:
    return 1

  while find_all:
    result[y, x] = 0  # clear max score, find next
    _, max_score, _, max_loc = cv2.minMaxLoc(result)
    if max_score < threshold:
      break
    x, y = max_loc

    already_append = False
    for box in boxes:
      # distance too short, same match
      if abs(box[0] - x) < 5 and abs(box[1] - y) < 5:
        already_append = True
        break

    if not already_append:
      box = (x, y, x + w, y + h)
      boxes.append(box)
      logger.debug("icon match[{}]: {}({})".format(len(boxes), box, max_score))

  if save_name is not None:
    for box in boxes:
      cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (255, 255, 255, 1), 5)  # FIXME why color not changed
    Image.fromarray(img).save("./screenshot/{}.png".format(save_name))

  return len(boxes)


def find_shiny():
  _start = time.time()  # cal time
  cnt = find_icon(screenshot.rival_screen(), "./icon/shiny_star.png",
                  threshold=0.5, find_all=True, save_name="shiny")
  _end = time.time()  # cal time
  logger.debug("shiny pokemon cnt: {} ({:.2f}s)".format(cnt, _end - _start))
  return cnt > 0
# find_shiny()
