from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from logger import logger

_browser: WebDriver

CANVAS_ORI_WIDTH = 1920
CANVAS_ORI_HEIGHT = 1080
TOP_BAR_HEIGHT = 30
RATIO = 1  # 1 / 1.6 / 2
_browser_width = 1920 // RATIO
_canvas_height = 1080 // RATIO
_browser_height = _canvas_height + TOP_BAR_HEIGHT


def init(session_id: str, chromedriver_path='./chromedriver'):
  global _browser

  options = webdriver.ChromeOptions()
  options.add_experimental_option("excludeSwitches", ["enable-automation"])
  options.add_argument('--disable-infobars')
  options.add_argument('--disable-extensions')
  options.add_argument("--app=https://pokerogue.net/")
  options.add_argument(f'--window-size={_browser_width},{_browser_height}')
  # options.add_argument('--headless')
  _browser = webdriver.Chrome(service=ChromeService(chromedriver_path), options=options)

  # _browser.get("https://pokerogue.net/")
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
                       'value': session_id,
                       'domain': 'pokerogue.net',
                       'path': '/',
                       'secure': True,
                       'sameSite': 'Strict'})

  sleep(10)


def close():
  _browser.quit()


def screenshot_as_base64():
  wait = WebDriverWait(_browser, 30)
  canvas = wait.until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))

  while canvas.size != {'width': _browser_width, 'height': _canvas_height}:
    logger.warning("canvas size is {}".format(canvas.size))
    _browser.set_window_size(_browser_width, _browser_height)
    _browser.set_window_size(_browser_width, _browser_height + 10)

  # data = _browser.execute_script("return arguments[0].toDataURL('image/png');", _canvas).split(",", 1)[1]
  return canvas.screenshot_as_base64
