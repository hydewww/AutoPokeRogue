import state


def test_exp():
  s, _ = state.recognize_state(debug_texts=['2010.223', 'Stunfisk gained', '15320 ExP Pointsl'])
  assert s == state.GAIN_EXP
