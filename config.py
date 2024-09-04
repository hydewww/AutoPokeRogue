import json
import os


class Config:
  def __init__(self):
    # modify your config in config.json
    self.COOKIE = ""
    self.CHROME_DRIVER_PATH = "./chromedriver"
    self.RESOLUTION_SCALE = 2
    self.DAILY_RUN_GUIDE = "./daily.txt"
    self.SAVE_SCREENSHOT = True
    self.SAVE_DEBUG_LOG = True
    self.SAVE_CMD_JSON = True

    self.WAIT_SECONDS_BEFORE_CRASH = 10


def load_config():
  fname = "config.json"

  if not os.path.exists(fname):
    config = Config()
    with open(fname, 'w') as f:
      json.dump(config.__dict__, f, indent=2)
    return config

  with open(fname, 'r') as f:
    data = json.load(f)

  config = Config()
  for key in config.__dict__.keys():
    if data.get(key):
      setattr(config, key, data[key])

  if len(config.__dict__.keys()) > len(data.keys()):
    with open(fname, 'w') as f:
      json.dump(config.__dict__, f, indent=2)

  return config


conf = load_config()
