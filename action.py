import time

import keyboard
import ocr
import text
from logger import logger
import const
import cv

max_ocr_score = {
  "pokemon": 0.0,
  "fight_move": 0.0,
  "learn_move": 0.0,
  "reward": 0.0,
  "sidebar": 0.0,
}  # debug


def choose_pokemon(pokemon, double=None, final_click=2):
  global max_ocr_score
  # Pokemon List Page
  # ensure the cursor is on the first pokemon
  keyboard.right()  # if only press left in doubles, cursor maybe on the second
  keyboard.left()

  # recognize
  min_score = 0.8  # TODO
  pokemons_name = ocr.pokemons_name(double=double)
  rank = text.find_all_in_ocr_texts(pokemon.p, pokemons_name, min_score=min_score)
  index, score, match = rank[0][0], rank[0][1], pokemons_name[rank[0][0]]

  if pokemon.hp is not None:
    flag = False
    hps = ocr.pokemons_hp(double=double)
    for i, s in rank:
      if hps[i].startswith(str(pokemon.hp)):
        index, score = i, s
        match = "{}({}hp)".format(pokemons_name[index], pokemon.hp)
        flag = True
    if not flag:
      pokemons = [(pokemons_name[i], hps[i]) for i in range(pokemons_name)]
      raise Exception("not found target: {}, pokemons: {}".format(pokemon, pokemons))
  elif pokemon.lv:
    raise Exception("not support yet")
  elif pokemon.gender is not None:
    raise Exception("not support yet")
  elif pokemon.no:
    index, score = rank[pokemon.no-1]
    match = "{}(#{})".format(pokemons_name[index], pokemon.no)
  max_ocr_score["pokemon"] = max(max_ocr_score["pokemon"], score)
  logger.info("🕹ACT choose pokemon[{}]: {}({:.3f})".format(index, match, score))

  # select
  for i in range(index):
    keyboard.down()

  if final_click is None:
    final_click = 2
  for i in range(final_click - 1):
    keyboard.confirm()

  keyboard.confirm(wait=keyboard.WaitSwitchPokemon)


def fight(move, side=None, double_idx=None):
  global max_ocr_score
  if double_idx is None:
    wait_time = keyboard.WaitFight
  elif double_idx == 1:
    wait_time = keyboard.WaitShortAction
  else:
    wait_time = keyboard.WaitFight * 2

  # Action Page
  keyboard.left()
  keyboard.up()
  keyboard.confirm(keyboard.WaitShortAction)

  # move recognize
  min_score = 0.5  # TODO
  moves = ocr.fight_moves()
  for m in moves:
    if "of confusion!" in m:
      moves = ocr.fight_moves()
  index, score, match = text.find_in_ocr_texts(move, moves, min_score=min_score)
  max_ocr_score["fight_move"] = max(max_ocr_score["fight_move"], score)
  logger.info("🕹ACT use move[{}]: {}({:.3f})-{}".format(index, match, score, side if side else ""))

  # move select
  if index & 1:
    keyboard.right()
  else:
    keyboard.left()
  if index & 2:
    keyboard.down()
  else:
    keyboard.up()
  if not side:
    keyboard.confirm(wait=wait_time)
    keyboard.up()  # after life dew
    return

  keyboard.confirm()
  keyboard.up()  # after life dew
  # side select
  if side == "R":
    keyboard.right()
  else:
    keyboard.left()
  keyboard.confirm(wait=wait_time)


def throw_ball(ball):
  # Action Page
  keyboard.up()
  keyboard.right()
  keyboard.confirm(wait=keyboard.WaitShortAction)

  # ball recognize
  cur_index = cv.ball_cursor_index()
  to_index = text.find_in_ocr_texts(ball, const.BALLS, min_score=0.5)[0]
  logger.info("🕹ACT throw {}[{}=>{}]".format(ball, cur_index, to_index))

  # ball select
  down = (to_index - cur_index) % len(const.BALLS)
  up = (cur_index - to_index) % len(const.BALLS)
  if down <= up:
    for i in range(down):
      keyboard.down()
  else:
    for i in range(up):
      keyboard.up()

  keyboard.confirm(wait=keyboard.WaitThrowBall)


def enter_pokemon_list_from_action_page():
  keyboard.left()
  keyboard.down()
  keyboard.confirm(keyboard.WaitPokemonList)


def active_switch_pokemon(pokemon, double=None):
  # Action Page
  logger.info("🕹ACT active switch to {}".format(pokemon))
  enter_pokemon_list_from_action_page()

  # pokemon list page
  choose_pokemon(pokemon, double=double)


def choose_reward(reward, total):
  global max_ocr_score
  # Shop Page
  if reward == "reroll":
    logger.info("🕹ACT reroll reward")
    keyboard.down()
    keyboard.confirm(keyboard.WaitReroll)
    return
  elif reward == "lock rarities":
    logger.info("🕹ACT lock rarities")
    keyboard.down()
    keyboard.down()
    keyboard.confirm(keyboard.WaitShortAction)
    keyboard.up()
    keyboard.up()
    return

  # reward recognize
  min_score = 0.75  # TODO
  rewards = ocr.rewards(cnt=total)
  index, score, match = text.find_in_ocr_texts(reward, rewards, min_score=min_score)
  max_ocr_score["reward"] = max(max_ocr_score["reward"], score)
  logger.info("🕹ACT choose reward[{}]: {}({:.3f})".format(index, match, score))

  # select
  for i in range(index):
    keyboard.right()
  keyboard.confirm(keyboard.WaitShortAction)


def choose_move(move):
  global max_ocr_score
  # Move Info Page
  # recognize
  min_score = 0.5
  moves = ocr.learn_moves()
  index, score, match = text.find_in_ocr_texts(move, moves, min_score=min_score)
  max_ocr_score["learn_move"] = max(max_ocr_score["learn_move"], score)
  logger.info("🕹ACT choose move[{}]: {}({:.3f})".format(index, match, score))

  # select
  for i in range(index):
    keyboard.down()
  keyboard.confirm()


def learn_new_move(old_move=None, new_move=None, step=None):
  # New Move

  if step is None:
    # xxx wants to learn the / move xxx.
    keyboard.confirm(wait=keyboard.WaitShortAction)
  # However, xxx already / knows four moves.
  keyboard.confirm(wait=keyboard.WaitShortAction)
  # Should a move be forgotten and / replaced with xxx?

  if old_move is None:
    logger.info("🕹ACT not learn move: {}".format(new_move))
    # > No
    keyboard.cancel(wait=keyboard.WaitShortAction)
    # Stop trying to teach / xxx?
    keyboard.confirm(wait=keyboard.WaitShortAction)
    # xxx did not learn the / move xxx.
    keyboard.confirm()
    return

  logger.info("🕹ACT learn move [{}]=>[{}]".format(old_move, new_move))
  # > Yes
  keyboard.confirm(wait=keyboard.WaitShortAction)
  # Which move should be forgotten? > Move Page
  keyboard.confirm()

  # Choose
  choose_move(old_move)
  time.sleep(keyboard.WaitDialog*2)
  # 1,2,and... ... ... Poof!
  keyboard.confirm(wait=keyboard.WaitDialog)
  # xxx forgot how to / use xxx.
  keyboard.confirm(wait=keyboard.WaitDialog*3)
  # And ...
  keyboard.confirm(wait=keyboard.WaitDialog*2)
  # xxx learned / xxx!
  keyboard.confirm(wait=keyboard.WaitDialog*2)


def memory_mushroom(pokemon, new_move, old_move, double=None):
  # Pokemons Page
  logger.info("🕹ACT [{}] memory move [{}]=>[{}]".format(pokemon, old_move, new_move))

  choose_pokemon(pokemon, final_click=1, double=double)

  # Move List
  min_score = 0.3  # TODO
  choose_from_sidebar(new_move, min_score=min_score)

  # replace old move
  learn_new_move(old_move)


def transfer_item(from_pokemon, item, to_pokemon, double=None):
  # Shop Page
  logger.info("🕹ACT transfer {} from {} to {}".format(item, from_pokemon, to_pokemon))

  # Shop Page => Pokemon List Page
  keyboard.down()
  keyboard.right()
  keyboard.confirm(keyboard.WaitPokemonList)

  # open list
  choose_pokemon(from_pokemon, final_click=1, double=double)

  # recognize
  min_score = 0.5  # TODO
  choose_from_sidebar(item, min_score=min_score)

  # transfer to to_pokemon
  choose_pokemon(to_pokemon, double=double)

  # back to Shop Page
  keyboard.cancel()

  # back to first reward
  keyboard.left()
  keyboard.up()


def save_and_quit():
  # Action Page
  logger.info("[Action] save and quit")
  keyboard.menu()
  keyboard.up()
  keyboard.up()
  keyboard.confirm(keyboard.WaitRefresh)


# transfer item / memory move
def choose_from_sidebar(name, min_score=1.0):
  global max_ocr_score

  if name.strip().lower() == "all":
    keyboard.up()
    keyboard.up()
    keyboard.confirm()
    return

  _, y1, x2, _ = cv.find_arrow()
  # recognize from bottom by default
  keyboard.up()
  items = ocr.pokemons_sidebar(x1=x2, y1=y1)
  index, score, match = text.find_in_ocr_texts(name, items, debug=True)
  index = len(items) - index - 1
  if score <= min_score:
    # select item
    max_ocr_score["sidebar"] = max(max_ocr_score["sidebar"], score)
    logger.info("🕹ACT choose sidebar[-{}]: {}({:.3f})".format(index, match, score))
    for i in range(index):
      keyboard.up()
    keyboard.confirm()
    return

  # maybe items/moves too much, find from top
  logger.debug("sidebar [{}]({:.3f}) not match [{}], find from top".format(match, score, name))
  keyboard.down()

  # select item
  index, score, match = text.find_in_ocr_texts(name, ocr.pokemons_sidebar(x1=x2, y1=y1), debug=True,
                                               min_score=min_score)
  max_ocr_score["sidebar"] = max(max_ocr_score["sidebar"], score)
  logger.info("🕹ACT choose sidebar[{}]: {}({:.3f})".format(index, match, score))
  for i in range(index):
    keyboard.down()
  keyboard.confirm()


def release_pokemon(p, double=None):
  # Pokemon List Page
  logger.info("🕹ACT release pokemon: [{}]".format(p))
  choose_pokemon(p, final_click=1, double=double)
  keyboard.up()
  keyboard.up()

  # Release
  # Do you really want to release xxx？
  # Goodbye, xxx
  keyboard.confirm(wait=keyboard.WaitShortAction)  # Release
  keyboard.confirm(wait=keyboard.WaitShortAction)  # Do you really want to release xxx？
  keyboard.confirm(wait=keyboard.WaitShortAction)  # Goodbye, xxx
