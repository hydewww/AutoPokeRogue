import state
from text import *


def test_exp():
  s, _ = state.recognize_state(debug_texts=['2010.223', 'Stunfisk gained', '15320 ExP Pointsl'])
  assert s == state.GAIN_EXP


def test_tm():
  idx, score, _ = find_in_ocr_texts('TM Toxic', ['M031-Toic', '5x Poke Ba11', 'ApicotBerry'])
  assert idx == 0
  assert score <= 0.75


def test_find_all():
  res = find_all_in_ocr_texts("AA", ["AA", "B", "C", "D", "AA", "X"], min_score=0.1)
  assert res == [(0, 0.0), (4, 0.0)]


def test_find_pokemon1():
  res = find_pokemon("Nature's Madness")
  assert res is None


def test_find_pokemon2():
  res = find_pokemon("Acrobatics L")
  assert res is None


def test_find_pokemon3():
  res = find_pokemon("x crobat y")
  assert res is not None
  assert res.group() == "crobat"
