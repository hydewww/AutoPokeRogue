from command import *


def test_switch_single1():
  c = recognize_cmd("Switch a to b")
  assert len(c) == 1
  assert c[0] == Command(SWITCH_POKEMON,
                         double_idx=None, from_p="a", to_p="b")


def test_switch_single2():
  c = recognize_cmd("Switch to b")
  assert len(c) == 1
  assert c[0] == Command(SWITCH_POKEMON,
                         double_idx=None, from_p=None, to_p="b")


def test_switch_send_in():
  c = recognize_cmd("- Send In Vulpix")
  assert len(c) == 1
  assert c[0] == Command(SWITCH_POKEMON,
                         double_idx=None, from_p=None, to_p="Vulpix")
  c = recognize_cmd("- Send in Vulpix")
  assert len(c) == 1
  assert c[0] == Command(SWITCH_POKEMON,
                         double_idx=None, from_p=None, to_p="Vulpix")


def test_switch_double1():
  c = recognize_cmd("Switch a > b & c > d")
  assert len(c) == 2
  assert c[0] == Command(SWITCH_POKEMON,
                         double_idx=1, from_p="a", to_p="b")
  assert c[1] == Command(SWITCH_POKEMON,
                         double_idx=2, from_p="c", to_p="d")


def test_switch_double2():
  c = recognize_cmd("Switch to a > b & c > d")
  assert len(c) == 2
  assert c[0] == Command(SWITCH_POKEMON,
                         double_idx=1, from_p="a", to_p="b")
  assert c[1] == Command(SWITCH_POKEMON,
                         double_idx=2, from_p="c", to_p="d")


def test_switch_double3():
  c = recognize_cmd("Switch to Weavile & Detect")
  assert len(c) == 2
  assert c[0] == Command(SWITCH_POKEMON,
                         double_idx=1, from_p=None, to_p="Weavile")
  assert c[1] == Command(FIGHT, move="Detect", double_idx=2)


def test_switch_double4():
  c = recognize_cmd("Switch to Gourgeist & Acrobatics L")
  assert len(c) == 2
  assert c[0] == Command(SWITCH_POKEMON,
                         double_idx=1, from_p=None, to_p="Gourgeist")
  assert c[1] == Command(FIGHT, move="Acrobatics", side="L", double_idx=2)


def test_switch_double4():
  c = recognize_cmd("Switch to Camerupt & Nature's Madness")
  assert len(c) == 2
  assert c[0] == Command(SWITCH_POKEMON,
                         double_idx=1, from_p=None, to_p="Camerupt")
  assert c[1] == Command(FIGHT, move="Nature's Madness", double_idx=2)


def test_pre_switch_double():
  c = recognize_cmd("Pre-Switch to b & d")
  assert len(c) == 2
  assert c[0] == Command(PRE_SWITCH_POKEMON,
                         double_idx=1, from_p=None, to_p="b")
  assert c[1] == Command(PRE_SWITCH_POKEMON,
                         double_idx=2, from_p=None, to_p="d")


def test_pre_switch_special():
  c = recognize_cmd("- Pre-Switch to Mr. Mime")
  assert len(c) == 1
  assert c[0] == Command(PRE_SWITCH_POKEMON,
                         from_p=None, to_p="Mr. Mime")


def test_transfer1():
  c = recognize_cmd("Transfer item from a to b")
  assert len(c) == 1
  assert c[0] == Command(TRANSFER,
                         item="item", from_p="a", to_p="b")


def test_transfer2():
  c = recognize_cmd("- Transfer | Unown & Wigglytuff ALL to Silvally")
  assert len(c) == 2
  assert c[0] == Command(TRANSFER,
                         item="All", from_p="Unown", to_p="Silvally")
  assert c[1] == Command(TRANSFER,
                         item="All", from_p="Wigglytuff", to_p="Silvally")


def test_transfer3():
  c = recognize_cmd("Transfer ALL from Paras & Stunfisk > Druddigon")
  assert len(c) == 2
  assert c[0] == Command(TRANSFER,
                         item="All", from_p="Paras", to_p="Druddigon")
  assert c[1] == Command(TRANSFER,
                         item="All", from_p="Stunfisk", to_p="Druddigon")


def test_transfer4():
  c = recognize_cmd("Transfer Lum Berry Ambipom > Lokix")
  assert len(c) == 1
  assert c[0] == Command(TRANSFER,
                         item="Lum Berry", from_p="Ambipom", to_p="Lokix")


def test_transfer5():
  c = recognize_cmd("Transfer | Landorus Leppa Berry > Amoonguss")
  assert len(c) == 1
  assert c[0] == Command(TRANSFER,
                         item="Leppa Berry", from_p="Landorus", to_p="Amoonguss")


def test_wave():
  c = recognize_cmd("Wave 5")
  assert len(c) == 1
  assert c[0] == Command(NEW_WAVE, wave_no=5)


def test_learn_move1():
  c = recognize_cmd("Salazzle | Fire Lash > Sweet Scent")
  assert len(c) == 1
  assert c[0] == Command(LEARN_MOVE, to_p="Salazzle",
                         old_move="Sweet Scent", move="Fire Lash")


def test_learn_move2():
  c = recognize_cmd("Shiftry Leaf Blade > Razor Leaf")
  assert len(c) == 1
  assert c[0] == Command(LEARN_MOVE, to_p="Shiftry",
                         old_move="Razor Leaf", move="Leaf Blade")


def test_learn_move3():
  c = recognize_cmd("- Drizzile | U-Turn > Tearful Look")
  assert len(c) == 1
  assert c[0] == Command(LEARN_MOVE, to_p="Drizzile",
                         old_move="Tearful Look", move="U-Turn")


def test_reward_reroll():
  c = recognize_cmd("Reward: Reroll x2 > Dire Hit")
  assert len(c) == 2
  assert c[0] == Command(REROLL, times=2)
  assert c[1] == Command(REWARD, item="Dire Hit")


def test_reward_pokemon1():
  c = recognize_cmd("Reward: Super Potion Palossand")
  assert len(c) == 1
  assert c[0] == Command(REWARD,
                         item="Super Potion", to_p="Palossand", p_click_cnt=2)


def test_reward_pokemon2():
  c = recognize_cmd("Reward: Icicle Spear > Weavile")
  assert len(c) == 1
  assert c[0] == Command(REWARD,
                         item="Icicle Spear", to_p="Weavile", p_click_cnt=2)


def test_reward_pokemon3():  #
  c = recognize_cmd("Reward: King's Rock Shedinja")
  assert len(c) == 1
  assert c[0] == Command(REWARD, item="King's Rock",
                         to_p="Shedinja", p_click_cnt=2)


def test_reward_evolution_reward():  #
  c = recognize_cmd("Reward: Reroll > Linking Cord Poliwhirl | Skip Bounce ")
  assert len(c) == 3
  assert c[0] == Command(REROLL, times=1)
  assert c[1] == Command(REWARD, item="Linking Cord",
                         to_p="Poliwhirl", p_click_cnt=2)
  assert c[2] == Command(SKIP_MOVE, move="Bounce")


def test_reward_evolution_reward2():  #
  c = recognize_cmd("Reward: Reroll > Linking Cord Poliwhirl | Bounce > Horn Leech")
  assert len(c) == 3
  assert c[0] == Command(REROLL, times=1)
  assert c[1] == Command(REWARD, item="Linking Cord",
                         to_p="Poliwhirl", p_click_cnt=2)
  assert c[2] == Command(LEARN_MOVE, to_p="Poliwhirl",
                         old_move="Horn Leech", move="Bounce")


def test_reward_evolution_reward_typo():  #
  c = recognize_cmd("Reward: Dusk Stone Doublade Skip King's Shield")
  assert len(c) == 2
  assert c[0] == Command(REWARD, item="Dusk Stone",
                         to_p="Doublade", p_click_cnt=2)
  assert c[1] == Command(SKIP_MOVE, move="King's Shield")


def test_reward_move1():
  c = recognize_cmd("Reward: PP Up Trevenant (Horn Leech)")
  assert len(c) == 1
  assert c[0] == Command(REWARD,
                         item="PP Up", to_p="Trevenant", move="Horn Leech", p_click_cnt=1)


def test_reward_move2():
  c = recognize_cmd("Reward: Max Ether Parasect > Giga Drain")
  assert len(c) == 1
  assert c[0] == Command(REWARD,
                         item="Max Ether", to_p="Parasect", move="Giga Drain", p_click_cnt=1)


def test_reward_move3():
  c = recognize_cmd("Reward: Acid Spray (Glimmora)")
  assert len(c) == 1
  assert c[0] == Command(REWARD,
                         item="Acid Spray", to_p="Glimmora", p_click_cnt=2)


def test_reward_move4():
  c = recognize_cmd("Reward: Reroll > PP Max Garganacl Recover")
  assert len(c) == 2
  assert c[0] == Command(REROLL, times=1)
  assert c[1] == Command(REWARD, item="PP Max",
                         to_p="Garganacl", p_click_cnt=1, move="Recover")


def test_reward_tm1():  #
  c = recognize_cmd("Reward: Reroll > TM Poltergeist Shedinja")
  assert len(c) == 2
  assert c[0] == Command(REROLL, times=1)
  assert c[1] == Command(REWARD, item="TM Poltergeist",
                         to_p="Shedinja", p_click_cnt=2)


def test_reward_tm2():
  c = recognize_cmd("Reward: TM Toxic Clauncher | Toxic > Flail")
  assert len(c) == 2
  assert c[0] == Command(REWARD, item="TM Toxic", to_p="Clauncher", p_click_cnt=2)
  assert c[1] == Command(LEARN_MOVE, to_p="Clauncher",
                         old_move="Flail", move="Toxic")


def test_reward_tm3():
  c = recognize_cmd("Reward: TM017 Surf Psyduck | Surf > Water Pulse")
  assert len(c) == 2
  assert c[0] == Command(REWARD, item="TM017 Surf", to_p="Psyduck", p_click_cnt=2)
  assert c[1] == Command(LEARN_MOVE, to_p="Psyduck",
                         old_move="Water Pulse", move="Surf")


def test_reward_memory_mushroom1():
  c = recognize_cmd("Reward: Memory Mushroom Mightyena | Crunch > Leer")
  assert len(c) == 2
  assert c[0] == Command(REWARD, item="Memory Mushroom")
  assert c[1] == Command(LEARN_MOVE, to_p="Mightyena",
                         old_move="Leer", move="Crunch")


def test_reward_memory_mushroom2():
  c = recognize_cmd("Reward: Memory Mushroom Butterfree | Sleep Powder > Quiver Dance")
  assert len(c) == 2
  assert c[0] == Command(REWARD, item="Memory Mushroom")
  assert c[1] == Command(LEARN_MOVE, to_p="Butterfree",
                         old_move="Quiver Dance", move="Sleep Powder")


def test_reward_typo1():
  c = recognize_cmd("Reward X Speed")
  assert len(c) == 1
  assert c[0] == Command(REWARD, item="X Speed")


def test_reward_typo2():
  c = recognize_cmd("shop:: X Speed")
  assert len(c) == 1
  assert c[0] == Command(REWARD, item="X Speed")


def test_release():
  c = recognize_cmd("Release Carracosta, Lapras, Ninjask")
  assert len(c) == 1
  assert c[0] == Command(RELEASE_POKEMON, to_p=["Carracosta", "Lapras", "Ninjask"])


def test_switch_move():
  c = recognize_cmd("Volt Switch to Malamar")
  assert len(c) == 2
  assert c[0] == Command(FIGHT, move="Volt Switch")
  assert c[1] == Command(SWITCH_POKEMON, to_p="Malamar")


def test_replace_typo():
  c = recognize_cmd("- Greninja > Dreadnaw")
  assert len(c) == 1
  assert c[0] == Command(REPLACE_POKEMON, to_p="Greninja",
                         from_p="Dreadnaw")


def test_replace1():
  c = recognize_cmd("Kricketune > Vulpix (10 HP)")
  assert len(c) == 1
  assert c[0] == Command(REPLACE_POKEMON, to_p="Kricketune",
                         from_p="Vulpix (10 HP)")
  assert c[0].from_p.p == "Vulpix"
  assert c[0].from_p.hp == 10


def test_replace2():
  c = recognize_cmd("Kricketune > Vulpix (10 hp)")
  assert len(c) == 1
  assert c[0] == Command(REPLACE_POKEMON, to_p="Kricketune",
                         from_p="Vulpix (10 HP)")
  assert c[0].from_p.p == "Vulpix"
  assert c[0].from_p.hp == 10


def test_replace3():
  c = recognize_cmd("Kricketune > Vulpix (lvl21)")
  assert len(c) == 1
  assert c[0] == Command(REPLACE_POKEMON, to_p="Kricketune",
                         from_p="Vulpix (lvl21)")
  assert c[0].from_p.p == "Vulpix"
  assert c[0].from_p.lv == 21


def test_replace4():
  c = recognize_cmd("Kricketune > Vulpix #2")
  assert len(c) == 1
  assert c[0] == Command(REPLACE_POKEMON, to_p="Kricketune",
                         from_p="Vulpix #2")
  assert c[0].from_p.p == "Vulpix"
  assert c[0].from_p.no == 2


def test_replace5():
  c = recognize_cmd("Kricketune > Vulpix (male)")
  assert len(c) == 1
  assert c[0] == Command(REPLACE_POKEMON, to_p="Kricketune",
                         from_p="Vulpix (male)")
  assert c[0].from_p.p == "Vulpix"
  assert c[0].from_p.gender == 1


# Kricketune > Vulpix #2 (w/ full HP)
# Transfer Gourgeist | Silk Scarf & Black Glasses > Liepard
# Spidops | Transfer All to Cloyster
# Baton to Snorlax
