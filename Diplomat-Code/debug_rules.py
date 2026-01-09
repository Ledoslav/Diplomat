from domain.rules import RuleEngine
from domain.models import Tone

engine = RuleEngine()

# Test Case 1: Simple Formal Replacement
input_1 = "hey u wanna go?"
tone_1 = Tone.FORMAL
res_1, expl_1, chg_1 = engine.refine_message(input_1, tone_1, {})
print(f"Input: '{input_1}' -> Target: {tone_1}")
print(f"Result: '{res_1}'")
print(f"Changes: {chg_1}\n")

# Test Case 2: Friendly Replacement
input_2 = "Sincerely, I must say no"
tone_2 = Tone.FRIENDLY
res_2, expl_2, chg_2 = engine.refine_message(input_2, tone_2, {})
print(f"Input: '{input_2}' -> Target: {tone_2}")
print(f"Result: '{res_2}'")
print(f"Changes: {chg_2}\n")

# Test Case 3: Professional (Problematic?)
input_3 = "hey u"
tone_3 = Tone.PROFESSIONAL
res_3, expl_3, chg_3 = engine.refine_message(input_3, tone_3, {})
print(f"Input: '{input_3}' -> Target: {tone_3}")
print(f"Result: '{res_3}'")
print(f"Changes: {chg_3}\n")
