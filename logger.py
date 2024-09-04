import logging
import datetime
import sys
import os

from config import conf

logger = logging.getLogger("pokerogue")
logger.setLevel(logging.DEBUG)
logger.propagate = False

formatter = logging.Formatter('%(asctime)s[%(levelname)5s] %(filename)10s:%(lineno)3d - %(message)s', datefmt="%H:%M:%S")

console = logging.StreamHandler()
console.setFormatter(formatter)

debug = True
for arg in sys.argv:
  if "machine" in arg:
    debug = False

if debug:
  console.setLevel(logging.DEBUG)
  logger.addHandler(console)
else:
  console.setLevel(logging.INFO)
  logger.addHandler(console)

  if conf.SAVE_DEBUG_LOG:
    if not os.path.exists("./log"):
      os.mkdir("./log")
    log_filename = "./log/{}.log".format(datetime.datetime.now().strftime('%m%d_%H%M'))
    file = logging.FileHandler(filename=log_filename, encoding='utf-8', mode='w')
    file.setLevel(logging.DEBUG)
    file.setFormatter(formatter)

    logger.addHandler(file)
