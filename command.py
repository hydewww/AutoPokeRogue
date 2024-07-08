import command
import text
from logger import logger
import const

import re

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


class Command:
  def __init__(self, act, double=None, double_idx=None,
               from_p=None, to_p=None, p_click_cnt=None,
               move=None, side=None, old_move=None,
               item=None, ball=None, wave_no=None,
               times=None):
    self.act = act
    self.double = double
    self.double_idx = double_idx
    self.ball = ball
    self.from_p = from_p
    self.to_p = to_p
    self.p_click_cnt = p_click_cnt
    self.move = move
    self.old_move = old_move
    self.side = side
    self.item = item
    self.wave_no = wave_no
    self.times = times
    self.line_no = None

  def __str__(self):
    attrs = {}
    for k, v in self.__dict__.items():
      if v is not None:
        attrs[k] = v
    return str(attrs)

  def __repr__(self):
    return self.__str__()

  def __eq__(self, other):
    sd, od = self.__dict__, other.__dict__
    for k in sd.keys():
      if k == "double":
        continue
      if sd[k] != od[k]:
        return False
    return True


def preproc(cmd: str):
  cmd = cmd.strip()
  if cmd.startswith("- "):
    cmd = cmd[len("- "):].strip()
  res = (cmd.
         replace("Send in ", "Switch > ").
         replace("Pick ", "Switch > ").
         replace("Swap ", "Switch ").  # TODO: swap in or swap?
         replace(" for ", " > ").  # Pre-switch a for b
         replace(" to ", " > ").
         replace(" + ", " & ").
         replace(" ALL ", " All ")  # Transfer ALL
         )
  if res != cmd:
    pass
    # logger.debug("preproc cmd: [{}] => [{}]".format(cmd, res))
  return res


def __rec_switch(cmd: str):
  match = re.search(r"witch( >)?(?P<from>( [\w\-']+)+)?( >)?(?P<to>( [\w\-']+)+)", cmd)
  if match is None:
    raise Exception("Not match switch [{}]".format(cmd))
  f = match.group("from")
  if f is not None:
    f = f.strip()
  return f, match.group("to").strip()


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
  if "Berry Pouch" in cmd:  # special case
    cmds.append(Command(REWARD, item=reward))
    return cmds

  for key in const.ITEM_2CLICK + const.ITEM_1CLICK_WITH_MOVE:
    if key not in reward:
      continue

    item_last_idx = reward.index(key) + len(key)
    pokemon = reward[item_last_idx:].strip()
    if len(pokemon) <= const.POKEMON_NAME_MIN_LEN:
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


def recognize_cmd(cmd: str, double=None, double_idx=None):
  cmd = preproc(cmd)
  lcmd = cmd.lower()

  if lcmd.startswith("wave "):
    try:
      wave_no = int(cmd.split(" ")[1])
      return [Command(NEW_WAVE, wave_no=wave_no)]
    except ValueError:
      print("not new wave: {}".format(cmd))

  if lcmd == "save and quit":
    return [Command(SAVE_AND_QUIT)]

  if lcmd.startswith("reload ") or "f5" in lcmd:
    return [Command(RELOAD)]

  if "end of run" in lcmd:
    return [Command(DAILY_DONE)]

  if lcmd == "do not keep":
    return [Command(NOT_KEEP_POKEMON)]

  if lcmd.startswith("transfer "):
    return __rec_transfer(cmd)

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

  # double battle, split cmds
  if " & " in cmd:
    cmds = []
    for idx, c in enumerate(cmd.split(" & ")):
      if idx == 1:
        # modify "switch a>b & c>d" => "switch a>b", "switch c>d "
        if (lcmd.startswith("switch ") and
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
  elif lcmd.startswith("switch, do not pre"):  # Switch, DO NOT PRESWITCH Beedrill
    cmd = "Switch " + cmd[lcmd.index("pre"):].split(" ", 1)[1]
    from_pokemon, to_pokemon = __rec_switch(cmd)
    return [Command(SWITCH_POKEMON, double=double, double_idx=double_idx,
                    from_p=from_pokemon, to_p=to_pokemon)]

  # TODO: more solid
  if " > " in cmd:
    tmp = cmd.split(" > ")
    if " | " in cmd:
      tmp2 = tmp[0].split(" | ")
      pokemon = tmp2[0]
      return [Command(LEARN_MOVE, move=tmp2[1], old_move=tmp[1], to_p=pokemon)]

    new, old = tmp[0].strip(), tmp[1].strip()
    if const.POKEMONS_PATTERN.search(old):
      return [Command(REPLACE_POKEMON, from_p=old, to_p=new)]

    match = const.POKEMONS_PATTERN.search(new)
    if match:
      # xxx aaa > bbb
      new = new[match.end():].strip()
      return [Command(LEARN_MOVE, move=new, old_move=old, to_p=match.group())]

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
  match = re.search(r"(- )?(.*) x(\d+)$", cmd, re.IGNORECASE)
  if not match:
    return cmd, 1

  return match.group(2), int(match.group(3))


def cmd_generator(fname):
  all_cmds = []
  with open(fname, 'r') as file:
    wave_cmds = []
    line_no = 0
    for line in file:
      line_no += 1
      line = line.strip("-").strip()
      if line == "" or line.startswith("Daily Run Guide"):
        continue

      cmd, times = __rec_times(line)
      try:
        cmds = recognize_cmd(cmd)
        cmds[0].line_no = line_no
      except Exception as e:
          logger.warn("❌ CMD Error: {}, line={}".format(e, line_no))
          continue
      if times > 1:
        cmds = cmds * times
        # logger.debug("💬CMD {} x {} times".format(cmds[0], times))
      if cmds[0].act == NEW_WAVE:
        all_cmds.append(wave_cmds)
        wave_cmds = cmds
      else:
        wave_cmds.extend(cmds)
    all_cmds.append(wave_cmds)  # last wave
  all_cmds = all_cmds[1:]

  for cmds in all_cmds:
    double = False
    for cmd in cmds:
      if cmd.double:
        double = True
        break
    if double:
      for cmd in cmds:
        cmd.double = double

  for cmds in all_cmds:
    yield cmds

