import pyautogui
from time import sleep

WaitDirect = 0.1
WaitAction = 0.5
WaitRefresh = 5

WaitPokemonList = 0.4
WaitPokemonListForPreSwitch = 0.8
WaitSwitchPokemon = 1.2
WaitFight = 1.6
WaitThrowBall = 1.8
WaitNewCombat = 2.5
WaitDialog = 0.8
WaitReroll = 1.5
WaitShortAction = 0.2
WaitHatchEgg = 2
WaitDeactivate = 5


def up():
  pyautogui.press('w')
  sleep(WaitDirect)


def down():
  pyautogui.press('s')
  sleep(WaitDirect)


def left():
  pyautogui.press('a')
  sleep(WaitDirect)


def right():
  pyautogui.press('d')
  sleep(WaitDirect)


def refresh(no_wait=False):
  pyautogui.keyDown("command")
  sleep(0.3)
  pyautogui.keyDown("r")
  sleep(0.2)
  pyautogui.keyUp("r")
  sleep(0.2)
  pyautogui.keyUp("command")
  if not no_wait:
    sleep(WaitRefresh)


def confirm(wait=WaitAction):
  pyautogui.press('z')
  sleep(wait)


def cancel(wait=WaitAction):
  pyautogui.press('x')
  sleep(wait)


def menu(wait=WaitAction):
  pyautogui.press('m')
  sleep(wait)


def confirm_down():
  pyautogui.keyDown("z")


def confirm_up():
  pyautogui.keyUp("z")
