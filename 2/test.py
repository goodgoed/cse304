import re

pattern = r'".*?"'
text = "The computer simply responded with \"A:\\>\""

matches = re.findall(pattern, text)

for match in matches:
    print(match)