import pyautogui
import time

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
WaitReroll = 1
WaitShortAction = 0.2


def up():
  pyautogui.press('w')
  time.sleep(WaitDirect)


def down():
  pyautogui.press('s')
  time.sleep(WaitDirect)


def left():
  pyautogui.press('a')
  time.sleep(WaitDirect)


def right():
  pyautogui.press('d')
  time.sleep(WaitDirect)


def refresh(no_wait=False):
  pyautogui.keyDown("command")
  time.sleep(0.3)
  pyautogui.keyDown("r")
  time.sleep(0.2)
  pyautogui.keyUp("r")
  time.sleep(0.2)
  pyautogui.keyUp("command")
  if not no_wait:
    time.sleep(WaitRefresh)


def confirm(wait=WaitAction):
  pyautogui.press('z')
  time.sleep(wait)


def cancel(wait=WaitAction):
  pyautogui.press('x')
  time.sleep(wait)


def menu(wait=WaitAction):
  pyautogui.press('m')
  time.sleep(wait)
