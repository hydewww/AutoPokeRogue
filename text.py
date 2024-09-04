import Levenshtein
import re
import numpy as np

import const
from logger import logger


_replace_texts = [
  ["1", "l"],
  ["0", "O"],
  ["é", "e"],
  ["X", "H"],
  ["M", "H"],
  ["w", "H"],
  ["m", "n"],
  [" l", "l"],
  [" i", "i"],
  ["U", "V"],
  ["5x ", ""],
  ["!", "l"],
]


def compare(origin: str, ocr: str):
  for t in _replace_texts:
    origin = origin.replace(t[0], t[1])
    ocr = ocr.replace(t[0], t[1])
  origin = origin.lower()
  ocr = ocr.lower()
  ocr2 = ocr

  # if origin pattern too short, only compare part to control score
  if len(ocr) >= len(origin) * 1.5:
    # consider the shortest and often used pattern "All"
    tmp = max(int(len(origin) * 1.25), len(origin)+2)
    # sequence is important
    ocr2 = ocr[-tmp:]
    ocr = ocr[:tmp]

  dis = min(Levenshtein.distance(origin, ocr, weights=(1, 1, 1)),
            Levenshtein.distance(origin, ocr2, weights=(1, 1, 1)))
  score = dis / len(origin)
  return score


def find_in_ocr_texts(text, texts, no=1, min_score=None, debug=False):
  scores = [compare(text, t) for t in texts]
  if debug:
    logger.debug("compare [{}] to {} score: {}".format(text, texts, scores))

  index = np.argsort(scores)[no - 1]
  score = scores[index]

  if min_score is not None and score > min_score:
    raise Exception("Not Found [{}] in texts: {}, scores: {}, min: {}".format(text, texts, scores, min_score))
  return index, score, texts[index]


def find_all_in_ocr_texts(text: str, texts: list[str], min_score=None, debug=False) -> list[tuple[int, float]]:
  scores = [compare(text, t) for t in texts]
  if debug:
    logger.debug("compare [{}] to {} score: {}".format(text, texts, scores))

  res = []
  for idx in np.argsort(scores):
    if min_score is None or scores[idx] <= min_score:
      res.append((idx, scores[idx]))

  if len(res) == 0:
    raise Exception("Not Found [{}] in texts: {}, scores: {}, min: {}".format(text, texts, scores, min_score))

  return res


def find_closest_pattern(patterns, texts, debug=False):
  if len(texts) == 0 or len(patterns) == 0:
    return -1, 10
  res = [find_in_ocr_texts(pattern, texts, debug=False) for pattern in patterns]

  scores = [r[1] for r in res]
  index, score = np.argmin(scores), np.min(scores)

  if debug:
    for i in range(len(patterns)):
      pattern = patterns[i]
      r = res[i]
      logger.debug("match [{}]-[{}]={:.3f}".format(pattern, texts[r[0]], r[1]))

  return index, score


def check_pokemons_correctness(pokemons):
  if len(pokemons[0]) < const.POKEMON_NAME_MIN_LEN:
    return False

  flag = False
  for i in range(len(pokemons)-1, 0, -1):
    if len(pokemons[i]) >= const.POKEMON_NAME_MIN_LEN:
      flag = True
    elif flag is True:
      return False

  return True
