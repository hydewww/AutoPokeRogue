import time

import action
import command
import ocr
import screenshot
import state
import text
import keyboard
from logger import logger
import browser
import cv
from config import conf


begin_wave = -1
cmd_wave = -1
game_beginning = False
unknown_confirm = 0


def start_page(sta: str, cmd: command.Command | None, texts: list[str] | None, init=False):
  global begin_wave

  if cmd and cmd.act == command.DAILY_DONE:
    logger.info("⌨️CMD ALL DONE!")
    return True

  keyboard.confirm(wait=keyboard.WaitNewCombat)
  if init:
    sta, texts = state.recognize_state()
    while sta == state.SESSION_LOADED:
      keyboard.confirm()
      time.sleep(1)
      sta, texts = state.recognize_state()
    begin_wave = ocr.wave_no()[0]  # TODO
    logger.info("begin wave: {}".format(begin_wave))

  return cmd and cmd.act == command.RELOAD


def reload_game(sta: str, cmd: command.Command, texts: list[str], init=False):
  if sta == state.START:  # ready
    return start_page(sta, cmd, texts, init=init)

  logger.info("🕹ACT reload game")

  # often failed to refresh successfully, use len(texts)=0 to confirm
  while True:
    keyboard.refresh(no_wait=True)
    time.sleep(0.5)
    texts = ocr.bottom_screen()
    if len(texts) == 0:
      break
  time.sleep(keyboard.WaitRefresh)

  check_interval = 2  # TODO
  wait_times = 5
  for i in range(wait_times):
    sta, texts = state.recognize_state()
    if sta == state.START:
      return start_page(sta, cmd, texts, init=init)

    time.sleep(check_interval)

  logger.debug("waiting too long, reload again")
  return reload_game(sta, cmd, texts)


def pre_switch_pokemon(sta: str, cmd: command.Command, texts: list[str]):
  if cmd.act != command.PRE_SWITCH_POKEMON:
    logger.info("🕹ACT cancel pre-switch.")
    keyboard.cancel()
    return False

  # single: 'Will you switch', 'Pokemon?'
  if cmd.double_idx is None:
    logger.info("🕹ACT pre switch to {}".format(cmd.to_p))
    keyboard.confirm(keyboard.WaitPokemonListForPreSwitch)
    action.choose_pokemon(cmd.to_p, double=cmd.double)
    return True

  # double: 'Will you switch', 'xxx?'
  if cmd.from_p is not None:
    cur_p = ocr.chatbox(line=2)[0].strip('?')
    score = text.compare(cmd.from_p.p, cur_p)
    if score > 0.5:  # TODO
      logger.info("🕹ACT [{}] not match {}[{:.3f}], cancel pre switch".format(cur_p, cmd.from_p, score))
      keyboard.cancel()
      return False
  logger.info("🕹ACT pre switch {}=>{}".format(cmd.from_p, cmd.to_p))
  keyboard.confirm(keyboard.WaitPokemonListForPreSwitch)

  # maybe there is nature effect, wait
  sta, texts = state.recognize_state()
  while sta != state.POKEMON_LIST:
    sta, texts = state.recognize_state()

  action.choose_pokemon(cmd.to_p, double=True)
  return True


def action_page(sta: str, cmd: command.Command, texts: list[str]):
  if cmd.act == command.SAVE_AND_QUIT:
    action.save_and_quit()
    return True
  elif cmd.act == command.THROW_BALL:
    action.throw_ball(cmd.ball)
    return True
  elif cmd.act == command.SWITCH_POKEMON:
    action.active_switch_pokemon(cmd.to_p, double=cmd.double)
    return True
  elif cmd.act == command.FIGHT:
    action.fight(cmd.move, cmd.side, double_idx=cmd.double_idx)
    return True
  elif cmd.act == command.RELEASE_POKEMON:
    action.enter_pokemon_list_from_action_page()
    for p in cmd.to_p:
      action.release_pokemon(p, double=cmd.double)
    keyboard.cancel()
    return True

  raise Exception("state [{}] not match command {}".format(sta, cmd))


def learn_new_move(sta: str, cmd: command.Command, texts: list[str]):
  if cmd.act == command.SKIP_MOVE:
    action.learn_new_move(new_move=cmd.move,
                          step=2 if sta == state.LEARN_MOVE2 else None)
    return True
  elif cmd.act == command.LEARN_MOVE:
    action.learn_new_move(old_move=cmd.old_move, new_move=cmd.move,
                          step=2 if sta == state.LEARN_MOVE2 else None)
    return True

  raise Exception("state [{}] not match command {}".format(sta, cmd))


def choose_reward(sta: str, cmd: command.Command, texts: list[str]):
  if cmd.act == command.TRANSFER:
    action.transfer_item(cmd.from_p, cmd.item, cmd.to_p, double=cmd.double)
    return True

  # screenshot.fullscreen(save_name="rewards/{}".format(cmd_wave))  # for debug
  total = 3 if cmd_wave < 20 else cmd_wave // 10 + 2  # TODO
  if cmd.act == command.REROLL:
    for _ in range(cmd.times):
      action.choose_reward("reroll", total)
    return True
  elif cmd.act == command.LOCK_RARITIES:
    action.choose_reward("lock rarities", total)
    return True
  elif cmd.act == command.REWARD:
    action.choose_reward(cmd.item, total)
    if cmd.to_p is None:
      time.sleep(keyboard.WaitNewCombat)
      return True

    action.choose_pokemon(cmd.to_p, final_click=cmd.p_click_cnt, double=cmd.double)
    if cmd.move is None:
      logger.info("🕹ACT special item [{}] for [{}]".format(cmd.item, cmd.to_p))
      time.sleep(keyboard.WaitNewCombat)
      return True
    else:
      logger.info("🕹ACT special item [{}] for [{}]'s [{}]".format(cmd.item, cmd.to_p, cmd.move))
      action.choose_from_sidebar(cmd.move)
      time.sleep(keyboard.WaitNewCombat)
      return True

  raise Exception("state [{}] not match command {}".format(sta, cmd))


def party_full(sta: str, cmd: command.Command, texts: list[str]):
  if cmd.act == command.NOT_KEEP_POKEMON:
    logger.info("🕹ACT not keep pokemon")
    keyboard.cancel()
    return True
  elif cmd.act == command.REPLACE_POKEMON:
    logger.info("[Action] replace pokemon [{}]=>[{}]".format(cmd.from_p, cmd.to_p))
    keyboard.down()
    keyboard.confirm(keyboard.WaitPokemonList)
    action.choose_pokemon(cmd.from_p, final_click=3, double=cmd.double)
    return True

  raise Exception("state [{}] not match command {}".format(sta, cmd))


def skip_dialog(sta: str, cmd: command.Command, texts: list[str]):
  logger.debug("🕹ACT skip dialog")
  keyboard.confirm(keyboard.WaitDialog)
  if sta == state.EVOLVED:
    logger.info("🕹ACT evolution: {}".format(texts[-1]))
    return cmd.act == command.EVOLVE
  return False


def hatch_egg(sta: str, cmd: command.Command, texts: list[str]):
  logger.debug("🕹ACT hatch egg")
  if sta == state.EGG_SUMMARY:
    keyboard.confirm(wait=keyboard.WaitDialog)
    keyboard.cancel(wait=keyboard.WaitDialog)
    return False

  num = ocr.egg_num()
  if num is not None and num > 3:
    keyboard.confirm_down()
    while num > 3:
      num2 = ocr.egg_num()
      if num2 is not None:
        num = num2
      time.sleep(keyboard.WaitHatchEgg)
    keyboard.confirm_up()

  keyboard.confirm(keyboard.WaitDialog)
  return False


def choose_pokemon(sta: str, cmd: command.Command, texts: list[str]):
  # Memory Mushroom  # TODO
  if cmd.act == command.LEARN_MOVE:
    action.memory_mushroom(cmd.to_p, cmd.move, cmd.old_move, double=cmd.double)
    return True
  elif cmd.act == command.SWITCH_POKEMON or cmd.act == command.PRE_SWITCH_POKEMON:
    logger.info("🕹ACT switch to {}".format(cmd.to_p))
    action.choose_pokemon(cmd.to_p, double=cmd.double)
    return True

  raise Exception("state [{}] not match command {}".format(sta, cmd))


def wait_dialog(sta: str, cmd: command.Command, texts: list[str]):
  time.sleep(keyboard.WaitDialog)
  return False


def new_wave(sta: str, cmd: command.Command, texts: list[str]):
  global cmd_wave
  cmd_wave = cmd.wave_no

  if cmd_wave < begin_wave:
    return True

  logger.info("🐵Wave {}".format(cmd_wave))
  if sta not in [state.TRAINER_BATTLE, state.PRE_SWITCH, state.ACTION, state.LEARN_MOVE]:
    raise Exception("Not New Wave, state: {}".format(sta))

  # screenshot.fullscreen(save_name="wave/{}".format(cmd_wave))  # for debug
  if sta != state.TRAINER_BATTLE and cv.find_shiny():
    logger.info("🌟Shiny Pokemon!")
    if conf.SHINY_EXIT:
      exit(0)

  return True


def get_state_func(sta):
  if sta == state.START:
    return start_page
  elif sta == state.ACTION:
    return action_page
  elif sta == state.PRE_SWITCH:
    return pre_switch_pokemon
  elif sta in [state.SHOP, state.SHOP_WITH_LOCK]:
    return choose_reward
  elif sta in [state.LEARN_MOVE, state.LEARN_MOVE2]:
    return learn_new_move
  elif sta == state.PARTY_FULL:
    return party_full
  elif sta == state.POKEMON_LIST:
    return choose_pokemon
  elif sta in [state.GAIN_EXP, state.GAIN_MONEY, state.POKEMON_FAINTED,
               state.EVOLVED, state.POKEMON_CAUGHT,
               state.TRAINER_BATTLE, state.TRAINER_DEFEATED,
               state.WIN_ITEM, state.WIN_MONEY,
               state.LEVEL_CAP_UP, state.OH]:
    return skip_dialog
  elif sta in [state.EGG_HATCHED, state.MOVE_UNLOCKED, state.STARTER_ADDED, state.EGG_SUMMARY]:
    return hatch_egg
  elif sta in [state.EVOLVING, state.CLEAR_STAT, state.MOVE_EFFECT, state.WEATHER,
               state.TRAINER_REPLACE, state.LOADING]:
    return wait_dialog
  elif sta in [state.NEW_GAME, state.MOVE_SELECTION]:
    keyboard.cancel()
    return wait_dialog
  elif sta == state.COOKIE_BANNER:
    browser.close_cookie_banner()
    return wait_dialog

  raise Exception("Not supported state [{}]".format(sta))


def proc_command(cmd: command.Command):
  global game_beginning
  global cmd_wave, begin_wave
  global unknown_confirm

  sta, texts = state.recognize_state()
  unknown_times = 0
  while sta is None:
    unknown_times += 1
    if unknown_times % 3 == 0:
      logger.info("🕹ACT try press confirm to continue")
      unknown_confirm += 1
      # screenshot.fullscreen(save_name="unknown/{}_{}".format(cmd_wave, unknown_confirm))  # for debug
      keyboard.confirm(keyboard.WaitDialog)
    elif unknown_times == 7:  # TODO
      raise Exception("unknown state")
    time.sleep(1.5)
    sta, texts = state.recognize_state()
  f = get_state_func(sta)

  # be sure to clear dialogs to finish the wave
  if f in [skip_dialog, wait_dialog, start_page, hatch_egg]:
    return f(sta, cmd, texts)

  if cmd.act == command.NEW_WAVE:
    return new_wave(sta, cmd, texts)
  elif cmd_wave < begin_wave:
    return True
  elif cmd.act == command.RELOAD:
    if game_beginning is False:  # already reload when program start
      return True
    return reload_game(sta, cmd, texts)

  if game_beginning is False:
    game_beginning = True

  return f(sta, cmd, texts)


def init():
  browser.init()
  sta, texts = state.recognize_state()
  if sta == state.COOKIE_BANNER:
    browser.close_cookie_banner()
    sta, texts = state.recognize_state()

  reload_game(sta, None, texts, init=True)


def main():
  init()
  generator = command.cmd_generator()

  try:
    for cmds in generator:
      if cmds[0].wave_no and cmds[0].wave_no < begin_wave:
        continue

      for cmd in cmds:
        logger.info("💬CMD {}".format(cmd))
        # only pass command after proceed successfully
        while proc_command(cmd) is False:
          pass
  except Exception as e:
    logger.debug("{}".format(e))
    time.sleep(conf.WAIT_SECONDS_BEFORE_CRASH)
    raise e
  finally:
    browser.close()
    logger.debug("max score: {}".format(action.max_ocr_score))
    logger.debug("max state score: {}".format(state.cur_state_max_score))


main()
