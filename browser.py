import json
import psutil
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from psutil import ZombieProcess
from selenium.common.exceptions import NoSuchWindowException, InvalidSessionIdException, WebDriverException

from logger import logger
from config import conf

_browser: WebDriver

CANVAS_ORI_WIDTH = 1920
CANVAS_ORI_HEIGHT = 1080
TOP_BAR_HEIGHT = 30
RATIO = 2  # 1 / 1.6 / 2
_browser_width = int(1920 / RATIO)
_canvas_height = int(1080 / RATIO)
_browser_height = _canvas_height + TOP_BAR_HEIGHT

sess_file = './chrome_sess'


def get_existing_sess():
  global _browser
  try:
    with open(sess_file, 'r') as f:
      data = json.load(f)
    url = data['url']
    port = url.rsplit(':', 1)[1]
    sess_id = data['sess_id']

    existed = False
    for process in psutil.process_iter():
      if existed:
        break
      if 'chrome' in process.name().lower():
        try:
          # logger.debug(f"{process.name()} {process.cmdline()}")
          for line in process.cmdline():
            if port in line:
              existed = True
              break
        except ZombieProcess:
          continue
        except Exception as e:
          raise e

    if not existed:
      return False

    driver = webdriver.Remote(command_executor=url, options=webdriver.ChromeOptions())
    driver.close()
    driver.quit()
    driver.session_id = sess_id
    sleep(1)
    driver.find_element(By.TAG_NAME, 'canvas')
  except FileNotFoundError:
    return False
  except (NoSuchWindowException, InvalidSessionIdException):
    driver.quit()
    return False
  except WebDriverException as e:
    driver.quit()
    return False
  except Exception as e:
    print("Exception: {}".format(e))
    return False

  _browser = driver
  return True


def save_sess():
  with open(sess_file, 'w') as f:
    json.dump({'url': _browser.command_executor._url, 'sess_id': _browser.session_id}, f)


def init():
  global _browser

  if get_existing_sess():
    return

  options = webdriver.ChromeOptions()
  options.add_experimental_option("excludeSwitches", ["enable-automation"])
  options.add_argument('--disable-infobars')
  options.add_argument('--disable-extensions')
  options.add_argument("--app=https://pokerogue.net/")
  options.add_argument(f'--window-size={_browser_width},{_browser_height}')
  # options.add_argument('--headless')
  _browser = webdriver.Chrome(service=ChromeService(conf.chrome_driver_path), options=options)

  kvs = {
    "GAME_SPEED": 7,
    "HP_BAR_SPEED": 3,
    "EXP_GAINS_SPEED": 3,
    "EXP_PARTY_DISPLAY": 2,
    "ENABLE_RETRIES": 1,
    "TUTORIALS": 0,
    "MOVE_ANIMATIONS": 0,
    "MASTER_VOLUME": 0,
    "SHOW_LEVEL_UP_STATS": 0,
    "SKIP_SEEN_DIALOGUES": 1
  }
  _browser.execute_script(f"localStorage.setItem('settings', JSON.stringify({str(kvs)}));")
  _browser.add_cookie({'name': 'pokerogue_sessionId',
                       'value': conf.cookie,
                       'domain': 'pokerogue.net',
                       'path': '/',
                       'secure': True,
                       'sameSite': 'Strict'})

  save_sess()
  sleep(10)


def close():
  _browser.quit()


def screenshot_as_base64():
  wait = WebDriverWait(_browser, 5)
  canvas = wait.until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))

  while canvas.size != {'width': _browser_width, 'height': _canvas_height}:
    logger.warning("canvas size is {}".format(canvas.size))
    _browser.set_window_size(_browser_width, _browser_height)
    _browser.set_window_size(_browser_width, _browser_height + 10)

  # data = _browser.execute_script("return arguments[0].toDataURL('image/png');", _canvas).split(",", 1)[1]
  return canvas.screenshot_as_base64
