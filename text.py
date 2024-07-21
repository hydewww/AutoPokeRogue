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

  reg = re.compile(r"(\d){2,}")
  for p in pokemons:
    if reg.search(p) is not None:
      return False

  return True


def split_pokemon_name_and_no(name):
  match = re.search(r"#(\d)", name)
  if match:
    return name[:match.start()].strip(), int(match.group(1))
  return name, 1
# print(split_pokemon_name_and_no("Vulpix #2 (w/ full HP)"))
