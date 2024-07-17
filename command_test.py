import command


def test_switch_single1():
  c = command.recognize_cmd("Switch a to b")
  assert len(c) == 1
  assert c[0] == command.Command(command.SWITCH_POKEMON,
                                 double_idx=None, from_p="a", to_p="b")


def test_switch_single2():
  c = command.recognize_cmd("Switch to b")
  assert len(c) == 1
  assert c[0] == command.Command(command.SWITCH_POKEMON,
                                 double_idx=None, from_p=None, to_p="b")


def test_switch_single3():
  c = command.recognize_cmd("Send in b")
  assert len(c) == 1
  assert c[0] == command.Command(command.SWITCH_POKEMON,
                                 double_idx=None, from_p=None, to_p="b")


def test_switch_double1():
  c = command.recognize_cmd("Switch a > b & c > d")
  assert len(c) == 2
  assert c[0] == command.Command(command.SWITCH_POKEMON,
                                 double_idx=1, from_p="a", to_p="b")
  assert c[1] == command.Command(command.SWITCH_POKEMON,
                                 double_idx=2, from_p="c", to_p="d")


def test_switch_double2():
  c = command.recognize_cmd("Switch to a > b & c > d")
  assert len(c) == 2
  assert c[0] == command.Command(command.SWITCH_POKEMON,
                                 double_idx=1, from_p="a", to_p="b")
  assert c[1] == command.Command(command.SWITCH_POKEMON,
                                 double_idx=2, from_p="c", to_p="d")


def test_switch_double3():
  c = command.recognize_cmd("Pre-Switch to b & d")
  assert len(c) == 2
  assert c[0] == command.Command(command.PRE_SWITCH_POKEMON,
                                 double_idx=1, from_p=None, to_p="b")
  assert c[1] == command.Command(command.PRE_SWITCH_POKEMON,
                                 double_idx=2, from_p=None, to_p="d")


def test_switch_double4():
  c = command.recognize_cmd("Switch to Weavile & Detect")
  assert len(c) == 2
  assert c[0] == command.Command(command.SWITCH_POKEMON,
                                 double_idx=1, from_p=None, to_p="Weavile")
  assert c[1] == command.Command(command.FIGHT, move="Detect", double_idx=2)
  "Switch to Weavile & Detect"


def test_switch_special():
  c = command.recognize_cmd("Switch, DO NOT PRESWITCH Beedrill")
  assert len(c) == 1
  assert c[0] == command.Command(command.SWITCH_POKEMON,
                                 double_idx=None, from_p=None, to_p="Beedrill")


def test_transfer1():
  c = command.recognize_cmd("Transfer item from a to b")
  assert len(c) == 1
  assert c[0] == command.Command(command.TRANSFER,
                                 item="item", from_p="a", to_p="b")


def test_transfer2():
  c = command.recognize_cmd("- Transfer | Unown & Wigglytuff ALL to Silvally")
  assert len(c) == 2
  assert c[0] == command.Command(command.TRANSFER,
                                 item="All", from_p="Unown", to_p="Silvally")
  assert c[1] == command.Command(command.TRANSFER,
                                 item="All", from_p="Wigglytuff", to_p="Silvally")


def test_transfer3():
  c = command.recognize_cmd("Transfer ALL from Paras & Stunfisk > Druddigon")
  assert len(c) == 2
  assert c[0] == command.Command(command.TRANSFER,
                                 item="All", from_p="Paras", to_p="Druddigon")
  assert c[1] == command.Command(command.TRANSFER,
                                 item="All", from_p="Stunfisk", to_p="Druddigon")


def test_transfer4():
  c = command.recognize_cmd("Transfer Lum Berry Ambipom > Lokix")
  assert len(c) == 1
  assert c[0] == command.Command(command.TRANSFER,
                                 item="Lum Berry", from_p="Ambipom", to_p="Lokix")


def test_transfer5():
  c = command.recognize_cmd("Transfer | Landorus Leppa Berry > Amoonguss")
  assert len(c) == 1
  assert c[0] == command.Command(command.TRANSFER,
                                 item="Leppa Berry", from_p="Landorus", to_p="Amoonguss")


def test_wave():
  c = command.recognize_cmd("Wave 5")
  assert len(c) == 1
  assert c[0] == command.Command(command.NEW_WAVE, wave_no=5)


def test_learn_move1():
  c = command.recognize_cmd("Salazzle | Fire Lash > Sweet Scent")
  assert len(c) == 1
  assert c[0] == command.Command(command.LEARN_MOVE, to_p="Salazzle",
                                 old_move="Sweet Scent", move="Fire Lash")


def test_learn_move2():
  c = command.recognize_cmd("Shiftry Leaf Blade > Razor Leaf")
  assert len(c) == 1
  assert c[0] == command.Command(command.LEARN_MOVE, to_p="Shiftry",
                                 old_move="Razor Leaf", move="Leaf Blade")


def test_reward1():
  c = command.recognize_cmd("Reward: Reroll x2 > Dire Hit")
  assert len(c) == 2
  assert c[0] == command.Command(command.REROLL, times=2)
  assert c[1] == command.Command(command.REWARD, item="Dire Hit")


def test_reward2():
  c = command.recognize_cmd("Reward: Super Potion Palossand")
  assert len(c) == 1
  assert c[0] == command.Command(command.REWARD,
                                 item="Super Potion", to_p="Palossand", p_click_cnt=2)


def test_reward3():
  c = command.recognize_cmd("Reward: PP Up Trevenant (Horn Leech)")
  assert len(c) == 1
  assert c[0] == command.Command(command.REWARD,
                                 item="PP Up", to_p="Trevenant", move="Horn Leech", p_click_cnt=1)


def test_reward4():
  c = command.recognize_cmd("Reward: Icicle Spear > Weavile")
  assert len(c) == 1
  assert c[0] == command.Command(command.REWARD,
                                 item="Icicle Spear", to_p="Weavile", p_click_cnt=2)


def test_reward5():
  c = command.recognize_cmd("Reward: Max Ether Parasect > Giga Drain")
  assert len(c) == 1
  assert c[0] == command.Command(command.REWARD,
                                 item="Max Ether", to_p="Parasect", move="Giga Drain", p_click_cnt=1)


def test_reward6():
  c = command.recognize_cmd("Reward: Acid Spray (Glimmora)")
  assert len(c) == 1
  assert c[0] == command.Command(command.REWARD,
                                 item="Acid Spray", to_p="Glimmora", p_click_cnt=2)


def test_reward7():
  c = command.recognize_cmd("Reward: Reroll > PP Max Garganacl Recover")
  assert len(c) == 2
  assert c[0] == command.Command(command.REROLL, times=1)
  assert c[1] == command.Command(command.REWARD, item="PP Max",
                                 to_p="Garganacl", p_click_cnt=1, move="Recover")


def test_reward8():  #
  c = command.recognize_cmd("Reward: King's Rock Shedinja")
  assert len(c) == 1
  assert c[0] == command.Command(command.REWARD, item="King's Rock",
                                 to_p="Shedinja", p_click_cnt=2)


def test_reward9():  #
  c = command.recognize_cmd("Reward: Reroll > TM Poltergeist Shedinja")
  assert len(c) == 2
  assert c[0] == command.Command(command.REROLL, times=1)
  assert c[1] == command.Command(command.REWARD, item="TM Poltergeist",
                                 to_p="Shedinja", p_click_cnt=2)


def test_reward10():
  c = command.recognize_cmd("Reward: Memory Mushroom Mightyena | Crunch > Leer")
  assert len(c) == 2
  assert c[0] == command.Command(command.REWARD, item="Memory Mushroom")
  assert c[1] == command.Command(command.LEARN_MOVE, to_p="Mightyena",
                                 old_move="Leer", move="Crunch")


def test_evolve():
  c = command.recognize_cmd("Release Carracosta, Lapras, Ninjask")
  assert len(c) == 1
  assert c[0] == command.Command(command.RELEASE_POKEMON, to_p=["Carracosta", "Lapras", "Ninjask"])


def test_switch_move():
  c = command.recognize_cmd("Volt Switch to Malamar")
  assert len(c) == 2
  assert c[0] == command.Command(command.FIGHT, move="Volt Switch")
  assert c[1] == command.Command(command.SWITCH_POKEMON, to_p="Malamar")


def test_replace1():
  c = command.recognize_cmd("Kricketune > Vulpix (10 HP)")
  assert len(c) == 1
  assert c[0] == command.Command(command.REPLACE_POKEMON, from_p="Vulpix", from_p_hp=10, to_p="Kricketune")


def test_replace2():
  c = command.recognize_cmd("Kricketune > Vulpix #2 (w/ full HP)")
  assert len(c) == 1
  assert c[0] == command.Command(command.REPLACE_POKEMON, from_p="Vulpix", from_p_no=2, to_p="Kricketune")


def test_replace3():
  c = command.recognize_cmd("Kricketune > Vulpix (lvl21)")
  assert len(c) == 1
  assert c[0] == command.Command(command.REPLACE_POKEMON, from_p="Vulpix", from_p_lv=21, to_p="Kricketune")
