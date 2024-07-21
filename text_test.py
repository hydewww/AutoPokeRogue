import state
import text


def test_exp():
  s, _ = state.recognize_state(debug_texts=['2010.223', 'Stunfisk gained', '15320 ExP Pointsl'])
  assert s == state.GAIN_EXP


def test_tm():
  idx, score, _ = text.find_in_ocr_texts('TM Toxic', ['M031-Toic', '5x Poke Ba11', 'ApicotBerry'])
  assert idx == 0
  assert score <= 0.75
