import json
import re

import text
from logger import logger
import const
from config import conf

THROW_BALL = "ThrowBall"
SWITCH_POKEMON = "SwitchPokemon"
FIGHT = "Fight"
SAVE_AND_QUIT = "SaveAndQuit"
PRE_SWITCH_POKEMON = "PreSwitchPokemon"
TRANSFER = "Transfer"
NEW_WAVE = "NewWave"
RELOAD = "Reload"
LOCK_RARITIES = "LockRarities"
REROLL = "Reroll"
REWARD = "Reward"
SKIP_MOVE = "Skip Move"
LEARN_MOVE = "Learn Move"
NOT_KEEP_POKEMON = "Not Keep Pokemon"
REPLACE_POKEMON = "Replace Pokemon"
RELEASE_POKEMON = "Release Pokemon"
EVOLVE = "Evolve"
DAILY_DONE = "Daily Done"


class Pokemon:
  __re_no = re.compile(r"#(\d)")
  __re_hp = re.compile(r"(\d+) ?HP\)", re.I)
  __re_lv = re.compile(r"lvl(\d+)", re.I)

  def __init__(self, s: str):
    self.p = None
    self.hp = None
    self.no = None
    self.lv = None
    self.gender = None

    s = s.strip()
    match = self.__re_no.search(s)
    if match:
      self.p = s[:match.start()].strip("() ")
      self.no = int(match.group(1))
      return

    match = self.__re_lv.search(s)
    if match:
      self.p = s[:match.start()].strip("() ")
      self.lv = int(match.group(1))
      return

    if "(male)" in s:
      self.p = s.replace("(male)", "").strip()
      self.gender = 1
      return
    elif "(female)" in s:
      self.p = s.replace("(female)", "").strip()
      self.gender = 0
      return

    match = self.__re_hp.search(s)
    if match:
      self.p = s[:match.start()].strip("() ")
      self.hp = int(match.group(1))
      return

    if "(" in s and ")" in s:
      raise Exception("Unknown special pokemon: {}".format(s))

    self.p = s
    return

  def my_dict(self):
    attrs = {}
    for k, v in self.__dict__.items():
      if v is not None:
        attrs[k] = v
    return attrs

  def __str__(self):
    return str(self.my_dict())

  def __repr__(self):
    return str(self.my_dict())

  def __eq__(self, other):
    sd, od = self.__dict__, other.__dict__
    for k in sd.keys():
      if sd[k] != od[k]:
        return False
    return True


class Command:
  def __init__(self, act, double=None, double_idx=None, item=None, ball=None, wave_no=None, times=None,
               move=None, side=None, old_move=None,
               from_p=None, to_p=None, p_click_cnt=None):
    self.act = act
    self.double = double
    self.double_idx = double_idx
    self.item = item
    self.ball = ball
    self.wave_no = wave_no
    self.times = times
    self.move = move
    self.old_move = old_move
    self.side = side
    self.from_p = Pokemon(from_p) if from_p else None
    if isinstance(to_p, list):  # Release
      self.to_p = [Pokemon(p) for p in to_p]
    else:
      self.to_p = Pokemon(to_p) if to_p else None
    self.p_click_cnt = p_click_cnt

  def from_dict(self, dicts):
    for k, v in dicts.items():
      self.__dict__[k] = v
    return self

  def my_dict(self):
    attrs = {}
    for k, v in self.__dict__.items():
      if v is not None:
        attrs[k] = v
    return attrs

  def __str__(self):
    return str(self.my_dict())

  def __repr__(self):
    return str(self.my_dict())

  def __eq__(self, other):
    sd, od = self.__dict__, other.__dict__
    for k in sd.keys():
      if k == "double":
        continue
      if sd[k] != od[k]:
        return False
    return True


__re_switch = re.compile(r"^(send in|send|pick) ", re.I)
__re_to = re.compile(r"( for | to )", re.I)
__re_reward = re.compile(r"^(shop|reward):* ", re.I)
__re_all = re.compile(" all ", re.I)


def preproc(cmd: str):
  cmd = cmd.strip(' "')
  if cmd.startswith("- "):
    cmd = cmd[len("- "):].strip()
  cmd = (cmd.
         replace("::", ":").
         replace("Swap ", "Switch ").
         replace(" + ", " & ").
         replace("  ", " ")
         )
  cmd = __re_switch.sub("Switch > ", cmd)
  cmd = __re_to.sub(" > ", cmd)
  cmd = __re_reward.sub("Reward: ", cmd)
  cmd = __re_all.sub(" All ", cmd)
  if "switch" in cmd.lower() and len(cmd.split(" ")) == 2:
    cmd = " > ".join(cmd.split(" "))
  return cmd


def __rec_switch(cmd: str):
  match = re.search(r"Switch( >)?(?P<from>( [\w\-'.]+)+)? >(?P<to> .*)", cmd, re.I)
  if match is None:
    raise Exception("Not match switch [{}]".format(cmd))
  f = match.group("from")
  return f, match.group("to")


def __rec_transfer(cmd: str):
  cmd = cmd.replace("| ", "")
  tmp = cmd.split("Transfer ")[1]

  if " All > " in tmp:  # Transfer | Unown & Wigglytuff All > Silvally
    tmp = tmp.split(" All > ")
    item = "All"
    from_pokemon = tmp[0]
    to_pokemon = tmp[1].strip()
  elif " from " in tmp:  # Transfer item from a to b
    tmp = tmp.split(" from ")
    item = tmp[0]
    if " > " not in tmp[1]:
      raise Exception("No match transfer [{}]".format(cmd))
    tmp2 = tmp[1].split(" > ")
    from_pokemon, to_pokemon = tmp2[0], tmp2[1]
  elif "'s " in tmp:  # Transfer a's item to b
    tmp = tmp.split("'s ")
    from_pokemon = tmp[0]
    if " > " not in tmp[1]:
      raise Exception("No match transfer [{}]".format(cmd))
    tmp2 = tmp[1].split(" > ")
    item, to_pokemon = tmp2[0], tmp2[1]
  elif " > " in tmp:
    tmp = tmp.split(" > ")
    to_pokemon = tmp[1].strip()
    match = const.POKEMONS_PATTERN.search(tmp[0])  # FIXME: multiple
    if not match:
      raise Exception("No match transfer [{}]".format(cmd))

    from_pokemon = match.group()
    item = tmp[0].replace(from_pokemon, "").strip()
  else:
    raise Exception("No match transfer [{}]".format(cmd))

  res = []
  for p in from_pokemon.split(" & "):
    res.append(Command(TRANSFER, from_p=p.strip(), item=item, to_p=to_pokemon))

  return res


# TODO
def __rec_transfer2(cmd: str):
  tmp = cmd.split(" | ")
  from_pokemon = tmp[0].strip()
  tmp = tmp[1].split(">")
  item = tmp[0].replace("Transfer ", "").strip()
  to_pokemon = tmp[1].strip()

  return [Command(TRANSFER, from_p=from_pokemon, item=item, to_p=to_pokemon)]


def __rec_move_in_reward(cmd: str):
  if " | " not in cmd or not (" > " in cmd or " skip " in cmd.lower()):
    return None

  cmds = recognize_cmd(cmd)
  if cmds and len(cmds) == 1 and cmds[0].act in [LEARN_MOVE, SKIP_MOVE]:
    return cmds
  else:
    raise Exception("not found move in reward: {}".format(cmd))


def __rec_reward(cmd: str):
  match = re.search(r"Reward: (?P<lock>LOCK RARITIES > )?(?P<reroll>Reroll (x(?P<re_cnt>\d) )?> )?(?P<reward>.+)",
                    cmd, re.I)
  cmds = []
  if match.group("lock") is not None:
    cmds.append(Command(LOCK_RARITIES))
  if match.group("reroll") is not None:
    if match.group("re_cnt") is None:
      cmds.append(Command(REROLL, times=1))
    else:
      cnt = int(match.group("re_cnt"))
      cmds.append(Command(REROLL, times=cnt))

  reward = match.group("reward").strip()
  if "Berry Pouch" in reward:  # special case
    cmds.append(Command(REWARD, item=reward))
    return cmds

  if "Memory Mushroom" in reward:
    cmds.append(Command(REWARD, item="Memory Mushroom"))
    idx = reward.index("Memory Mushroom") + len("Memory Mushroom")
    cmds2 = __rec_move_in_reward(reward[idx:])
    if cmds2:
      cmds.extend(cmds2)
    return cmds

  if "TM" in reward:
    match = const.POKEMONS_PATTERN.search(reward)
    if not match:
      raise Exception("Invalid TM Command: {}".format(cmd))
    item = reward[:match.start()].strip()
    pokemon = match.group()
    cmds.append(Command(REWARD, item=item, to_p=pokemon, p_click_cnt=2))
    cmds2 = __rec_move_in_reward(reward[match.start():])
    if cmds2:
      cmds.extend(cmds2)
    return cmds

  for key in const.ITEM_2CLICK + const.ITEM_1CLICK_WITH_MOVE:
    if key not in reward:
      continue

    item_last_idx = reward.index(key) + len(key)
    pokemon = reward[item_last_idx:].strip()
    if len(pokemon) < const.POKEMON_NAME_MIN_LEN:
      continue

    reward = reward[:item_last_idx].strip()

    if key in const.ITEM_1CLICK_WITH_MOVE:
      pokemon_move = pokemon
      if "(" in pokemon_move:
        tmp = pokemon_move.split("(")
        pokemon, move = tmp[0].strip(), tmp[1].strip(") ")
      elif " > " in pokemon_move:
        tmp = pokemon_move.split(" > ")
        pokemon, move = tmp[0], tmp[1]
      else:
        match = const.POKEMONS_PATTERN.search(pokemon_move)
        if not match:
          raise Exception("Unknown reward [{}]".format(reward))
        pokemon, move = match.group(), pokemon_move[match.end():].strip()
      cmds.append(Command(REWARD, item=reward, to_p=pokemon, move=move, p_click_cnt=1))
      return cmds
    elif key in const.ITEM_EVOLUTION and " | " in pokemon:
      cmds2 = __rec_move_in_reward(pokemon)
      pokemon = pokemon[:pokemon.index(" |")]
      cmds.append(Command(REWARD, item=reward, to_p=pokemon, p_click_cnt=2))
      if cmds2:
        cmds.extend(cmds2)
      return cmds
    else:
      pokemon = pokemon.strip("() ")
      cmds.append(Command(REWARD, item=reward, to_p=pokemon, p_click_cnt=2))
      return cmds

  # unknown
  if " > " in reward:
    logger.debug("unsure reward: {}, cmd: {}".format(reward, cmd))
    tmp = reward.split(" > ")
    item, to_pokemon = tmp[0].strip(), tmp[1].strip()
    cmds.append(Command(REWARD, item=item, to_p=to_pokemon, p_click_cnt=2))
    return cmds
  elif "(" in reward:
    logger.debug("unsure reward: {}, cmd: {}".format(reward, cmd))
    tmp = reward.split("(")
    item, to_pokemon = tmp[0].strip(), tmp[1].strip(") ")
    cmds.append(Command(REWARD, item=item, to_p=to_pokemon, p_click_cnt=2))
    return cmds

  cmds.append(Command(REWARD, item=reward))
  return cmds


def __rec_special_pokemon(pokemon: str):
  if "#" not in pokemon and "lvl" not in pokemon and " HP" not in pokemon:
    return pokemon, None, None, None

  match = re.search(r"#(\d)", pokemon)
  if match:
    return pokemon[:match.start()].strip("() "), int(match.group(1)), None, None

  match = re.search(r"lvl(\d+)", pokemon)
  if match:
    return pokemon[:match.start()].strip("() "), None, int(match.group(1)), None

  match = re.search(r"(\d+) HP", pokemon)
  if match:
    return pokemon[:match.start()].strip("() "), None, None, int(match.group(1))

  raise Exception("Unknown special pokemon: {}".format(pokemon))


def recognize_cmd(cmd: str, double=None, double_idx=None):
  cmd = preproc(cmd)
  lcmd = cmd.lower()

  if lcmd.startswith("wave "):
    try:
      wave_no = int(cmd.split(" ")[1])
      return [Command(NEW_WAVE, wave_no=wave_no)]
    except ValueError:
      logger.debug("not new wave: {}".format(cmd))

  if lcmd == "save and quit":
    return [Command(SAVE_AND_QUIT)]

  if lcmd.startswith("reload ") or "f5" in lcmd:
    return [Command(RELOAD)]

  if "end of run" in lcmd:
    return [Command(DAILY_DONE)]

  if lcmd == "do not keep" or lcmd == "don't keep":
    return [Command(NOT_KEEP_POKEMON)]

  if lcmd.startswith("transfer "):
    return __rec_transfer(cmd)
  elif " Transfer " in cmd:
    return __rec_transfer2(cmd)

  if lcmd.startswith("reward: "):
    return __rec_reward(cmd)

  if lcmd.startswith("let ") and lcmd.endswith(" evolve"):
    pokemon = cmd[len("let "):-len(" evolve")]
    return [Command(EVOLVE, to_p=pokemon)]

  if lcmd.startswith("release "):
    pokemons = cmd[len("release "):].split(", ")
    return [Command(RELEASE_POKEMON, to_p=pokemons)]

  # throw ball
  if lcmd.endswith("ball"):
    # ensure it's not move (e.g: shadow ball)
    _, score, ball = text.find_in_ocr_texts(cmd, const.BALLS, debug=False)
    if score < 0.2:
      return [Command(THROW_BALL, ball=ball)]

  if lcmd.startswith("skip "):
    return [Command(SKIP_MOVE, move=cmd[len("Skip "):])]
  if " | " in lcmd and " skip " in lcmd:
    tmp = cmd.split(" | ")[1]
    return [Command(SKIP_MOVE, move=tmp[len("skip "):])]

  if " > " in cmd and " | " not in cmd:
    tmp = cmd.split(" > ")
    for move in const.SWITCH_MOVES:
      if move in tmp[0]:
        return [
          Command(FIGHT, move=move),
          Command(SWITCH_POKEMON, to_p=tmp[1].strip())
        ]

  # double battle, split cmds
  if " & " in cmd:
    cmds = []
    for idx, c in enumerate(cmd.split(" & ")):
      if idx == 1:
        # modify "switch a>b & c>d" => "switch a>b", "switch c>d "
        if (lcmd.startswith("switch ") and
                not (c.endswith(" L") or c.endswith(" R")) and
                (" > " in c or
                 const.POKEMONS_PATTERN.search(c.strip()) is not None)):  # maybe is move
          c = "Switch " + c
        elif lcmd.startswith("pre-switch "):
          c = "Pre-Switch > " + c
      cmds.extend(recognize_cmd(c, double=True, double_idx=idx + 1))
    return cmds

  if lcmd.startswith("switch "):
    from_pokemon, to_pokemon = __rec_switch(cmd)
    return [Command(SWITCH_POKEMON, double=double, double_idx=double_idx,
                    from_p=from_pokemon, to_p=to_pokemon)]
  elif lcmd.startswith("pre-switch "):
    from_pokemon, to_pokemon = __rec_switch(cmd)
    if double_idx is None and from_pokemon is not None:
      double_idx = -1  # TODO
    return [Command(PRE_SWITCH_POKEMON, double=double, double_idx=double_idx,
                    from_p=from_pokemon, to_p=to_pokemon)]

  # TODO: more solid
  if " > " in cmd:
    tmp = cmd.split(" > ")
    if " | " in cmd:
      tmp2 = tmp[0].split(" | ")
      pokemon = tmp2[0]
      return [Command(LEARN_MOVE, move=tmp2[1], old_move=tmp[1], to_p=pokemon)]

    new, old = tmp[0].strip(), tmp[1].strip()
    match = const.POKEMONS_PATTERN.search(old)
    if match:
      return [Command(REPLACE_POKEMON, to_p=new, from_p=old)]

    match = const.POKEMONS_PATTERN.search(new)
    if match:
      if len(new) - match.end() >= const.MOVE_NAME_MIN_LEN:
        # xxx aaa > bbb
        new = new[match.end():].strip()
        return [Command(LEARN_MOVE, move=new, old_move=old, to_p=match.group())]
      else:
        return [Command(REPLACE_POKEMON, to_p=new, from_p=old)]

    logger.warning("unsure learn move command: {}".format(cmd))
    return [Command(LEARN_MOVE, move=new, old_move=old)]

  # rest is fight
  if re.search(r"[^\w -]", cmd) is not None:
    raise Exception("Unknown command: {}".format(cmd))

  move, side = cmd, None
  if cmd.endswith(" L") or cmd.endswith(" R"):
    move, side = cmd[:-2], cmd[-1]
  return [Command(FIGHT, move=move, side=side, double=double, double_idx=double_idx)]


def __rec_times(cmd: str):
  match = re.search(r"(- )?(.*) x ?(\d+)$", cmd, re.IGNORECASE)
  if not match:
    return cmd, 1

  return match.group(2), int(match.group(3))


def split_cmds(all_cmds: list[list[Command]]):
  wave_cmds = []
  final_cmds = []
  for cmds in all_cmds:
    if cmds[0].act not in [NEW_WAVE, DAILY_DONE]:
      wave_cmds.extend(cmds)
      continue
    elif len(wave_cmds) == 0:
      wave_cmds = cmds
      continue
    else:
      double = False
      for cmd in wave_cmds:
        if cmd.double:
          double = True
          break
      if double:
        for cmd in wave_cmds:
          cmd.double = double
      final_cmds.append(wave_cmds)
      wave_cmds = cmds
  final_cmds.append(wave_cmds)
  return final_cmds


def cmd_gen():
  ori = open(conf.DAILY_RUN_GUIDE, 'r', encoding='utf-8')
  lines = ori.readlines()
  ori.close()

  json_lines = []
  all_cmds = []
  has_err = False

  for idx, line in enumerate(lines):
    line = line.strip("-").strip()
    if line == "" or "Daily Run Guide" in line:
      json_lines.append("\n")
      continue

    cmd, times = __rec_times(line)
    try:
      cmds = recognize_cmd(cmd)
    except Exception as e:
      logger.warning("❌ line:{}, {},".format(idx + 1, e))
      json_lines.append("{}\n".format(e))
      has_err = True
      continue
    if times > 1:
      cmds = cmds * times
    json_lines.append("{}\n".format(json.dumps(cmds, default=lambda x: x.my_dict(), ensure_ascii=False)))
    all_cmds.append(cmds)

  if conf.SAVE_CMD_JSON:
    f = open('daily.gen', 'w', encoding='utf-8')
    f.writelines(json_lines)
    f.close()

  if has_err:
    raise Exception("has unknown command")

  return split_cmds(all_cmds)


def cmd_generator():
  for cmds in cmd_gen():
    yield cmds


cmd_gen()
