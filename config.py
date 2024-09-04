import json
import os


class Config:
  def __init__(self):
    self.COOKIE = ""
    self.CHROME_DRIVER_PATH = "./chromedriver"
    self.RESOLUTION_SCALE = 2


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
