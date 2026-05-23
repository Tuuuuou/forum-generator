import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
AVATARS_DIR = os.path.join(BASE_DIR, "avatars")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

SCENES_FILE = os.path.join(DATA_DIR, "scenes.json")
CHARACTERS_FILE = os.path.join(DATA_DIR, "characters.json")
TEMPLATES_FILE = os.path.join(DATA_DIR, "templates.json")

for d in [DATA_DIR, AVATARS_DIR, EXPORTS_DIR]:
    os.makedirs(d, exist_ok=True)
