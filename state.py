import ocr
import text
from logger import logger

START = "Start Page"
LOADING = "Loading"
COOKIE_BANNER = "Cookie Banner"
NEW_GAME = "New Game"
SESSION_LOADED = "Session Loaded"

ACTION = "Action"
PRE_SWITCH = "Pre Switch"
SHOP = "Shop"
SHOP_WITH_LOCK = "Shop(Rarity Lock)"

MOVE_SELECTION = "Move Selection"
MOVE_EFFECT = "Move Effect"
WEATHER = "Weather"
LEARN_MOVE = "Learn Move"
LEARN_MOVE2 = "Learn Move2"
GAIN_EXP = "Gain Exp"
GAIN_MONEY = "Gain Money"
EVOLVING = "Evolving"
EVOLVED = "Evolved"

POKEMON_CAUGHT = "Pokemon Caught"
PARTY_FULL = "Party Full"
POKEMON_LIST = "Pokemon List"
POKEMON_FAINTED = "Pokemon Fainted"

CLEAR_STAT = "Clear Stat"
TRAINER_BATTLE = "Trainer Battle"
TRAINER_DEFEATED = "Trainer Defeated"
TRAINER_REPLACE = "Trainer Replace"
WIN_ITEM = "Gain Item"
WIN_MONEY = "Gain Money"

EGG_HATCHED = "Egg Hatched"
MOVE_UNLOCKED = "Move Unlocked"
STARTER_ADDED = "Starter Added"

LEVEL_CAP_UP = "Level Cap Up"

INVALID = "Invalid"

__match_text_to_state = {
  "Load Game": START,
  "Select a game mode.": NEW_GAME,
  "We use essential cookies to make our site work. With your consent,": COOKIE_BANNER,
  "This game is an unfinished product": LOADING,
  "Session loaded successfully": SESSION_LOADED,

  "Fight": ACTION,
  "Will you switch": PRE_SWITCH,
  "Reroll": SHOP,
  "Transfer": SHOP,
  "Lock Rarities": SHOP_WITH_LOCK,

  "super effective": MOVE_EFFECT,  # It's super effective!
  "with recoil!": MOVE_EFFECT,  # xxx is hit / with recoil!
  "out of confusion!": MOVE_EFFECT,  # xxx snapped / out of confusion!
  " to learn the": LEARN_MOVE,  # xxx wants to learn the / move xxx.
  "knows four moves.": LEARN_MOVE2,  # However, xxx already / knows four moves.
  "You picked up ": GAIN_MONEY,  # You picked up Pxx!
  " is evolving! ": EVOLVING,  # What? / xxx is evolving!
  " evolving! ": EVOLVING,  # What? / xxx is evolving!
  "Congratulations!": EVOLVED,  # Congratulations! / xxx evolved into yyy!

  # xxx gained / xxx EXP. Points!
  "Points!": GAIN_EXP,
  " EXP.Points!": GAIN_EXP,
  " EXP. Points!": GAIN_EXP,

  " was caught!": POKEMON_CAUGHT,  # xxx was caught!
  "Your party is full.": PARTY_FULL,  # Your party is full. / Release a Pokemon to make room for xxx?
  "Choose a Pokemon.": POKEMON_LIST,
  " fainted!": POKEMON_FAINTED,  # Wild xxx fainted

  "Come back, ": CLEAR_STAT,  # Come back, xxx!
  "A downpour started!": WEATHER,
  "would like to battle!": TRAINER_BATTLE,  # xxx / would like to battle!
  " sent out Foe ": TRAINER_REPLACE,  # xxx sent out Foe yyy!
  "You defeated": TRAINER_DEFEATED,  # You defeated / xxx
  "You received": WIN_ITEM,  # You received / xxx
  " for winning!": WIN_MONEY,  # You got / xxx for winning!

  " hatched from the egg!": EGG_HATCHED,  # xxx hatched from the egg!
  "Egg Move unlocked: ": MOVE_UNLOCKED,  # Egg Move unlocked: xxx
  "added as a starter!": STARTER_ADDED,  # xxx has been / added as a starter!

  "The level cap": LEVEL_CAP_UP,  # The level cap / has increased to xxx

  "'left to battle!": INVALID,  # xxx has no energy / left to battle!
  "met at Lv": INVALID,  # xxx nature / met at Lv20, xxx Field.
  "apparently met at Lv": INVALID,  # xxx nature / apparently met at Lv20, / Somewhere you can't remember.
}

match_texts = [k for k in __match_text_to_state.keys()]
state_max_score = 0.50  # TODO
cur_state_max_score = 0


def recognize_state(debug_texts=None):
  global cur_state_max_score

  if debug_texts is None:
    texts, is_chat = ocr.bottom_screen_with_chat()
  else:
    texts, is_chat = debug_texts, False

  idx, score = text.find_closest_pattern(match_texts, texts, debug=False)
  state = __match_text_to_state[match_texts[idx]]
  if score < state_max_score and state not in [INVALID, ACTION]:  # TODO
    cur_state_max_score = max(score, cur_state_max_score)
    logger.info("⚠️STA {}({:.3f})".format(state, score))
  elif "Accuracy" in texts and "Power" in texts and "PP" in texts:
    # special case: move selection
    state = MOVE_SELECTION
    logger.info("⚠️STA {} detected".format(state))
  elif is_chat is True:
    state = TRAINER_BATTLE
    logger.info("⚠️STA {} detected".format(state))
  elif score < state_max_score:
    cur_state_max_score = max(score, cur_state_max_score)
    logger.info("⚠️STA {}({:.3f})".format(state, score))
  else:
    logger.info("🔴STA {} not sure({:.3f}>={})".format(state, score, state_max_score))
    state = None

  return state, texts
