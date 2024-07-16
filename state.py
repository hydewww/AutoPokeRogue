import ocr
import text
from logger import logger

START = "Start Page"
ACTION = "Action"
PRE_SWITCH = "Pre Switch"
SHOP = "Shop"
SHOP_WITH_LOCK = "Shop(Rarity Lock)"

LEARN_MOVE = "Learn Move"
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
WIN_ITEM = "Gain Item"
WIN_MONEY = "Gain Money"

EGG_HATCHED = "Egg Hatched"
MOVE_UNLOCKED = "Move Unlocked"
STARTER_ADDED = "Starter Added"

LEVEL_CAP_UP = "Level Cap Up"

INVALID = "invalid"

__match_text_to_state = {
  "Load Game": START,
  "Fight": ACTION,
  "Will you switch": PRE_SWITCH,
  "Reroll": SHOP,
  "Transfer": SHOP,
  "Lock Rarities": SHOP_WITH_LOCK,

  "wants to learn the": LEARN_MOVE,  # xxx wants to learn the / move xxx.
  "You picked up ": GAIN_MONEY,  # You picked up Pxx!
  " is evolving! ": EVOLVING,  # What? / xxx is evolving!
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
  "Gym Lead": TRAINER_BATTLE,
  "Breeder ": TRAINER_BATTLE,
  "would like to battle!": TRAINER_BATTLE,  # xxx / would like to battle!
  "You defeated": TRAINER_DEFEATED,  # You defeated / xxx
  "You received": WIN_ITEM,  # You received / xxx
  " for winning!": WIN_MONEY,  # You got / xxx for winning!

  " hatched from the egg!": EGG_HATCHED,  # xxx hatched from the egg!
  "Egg Move unlocked: ": MOVE_UNLOCKED,  # Egg Move unlocked: xxx
  "added as a starter!": STARTER_ADDED,  # xxx has been / added as a starter!

  "The level cap": LEVEL_CAP_UP,  # The level cap / has increased to xxx

  "'left to battle!": INVALID,  # xxx has no energy / left to battle!
}

match_texts = [k for k in __match_text_to_state.keys()]
state_min_score = 0.51  # TODO


def recognize_state():
  texts = ocr.bottom_screen()
  idx, score = text.find_closest_pattern(match_texts, texts, debug=False)
  state = __match_text_to_state[match_texts[idx]]
  if score >= state_min_score:
    logger.debug("🔴STA {} not sure({:.3f}>={})".format(state, score, state_min_score))
    state = None

  logger.info("⚠️STA {}({:.3f})".format(state, score))

  return state, texts
