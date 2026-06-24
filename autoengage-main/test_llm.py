import os
from llm_helper import generate_text

print("Start")
res = generate_text("You are a bot. IMPORTANT: Write entirely in Hebrew.", "Say hello.")
print("Res:", res)
print("End")
