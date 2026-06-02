import jieba
import random
from data_manager import load_characters, load_templates

STOP_WORDS = {"的", "了", "是", "我", "你", "他", "她", "它", "们", "这", "那", "不", "就", "也", "都", "在", "有", "和", "与", "或"}

EMOTION_KEYWORDS = {
    "挂人": "愤怒", "爆料": "震惊", "笑死": "吃瓜", "哈哈哈": "吃瓜",
    "心疼": "温柔", "离谱": "吐槽", "删帖": "心虚", "截图": "心虚",
    "举报": "愤怒", "出来": "愤怒", "锤": "震惊", "别删": "愤怒",
    "反转": "震惊", "真的假的": "震惊", "蹲": "吃瓜", "求私": "吃瓜",
    "可爱": "温柔", "萌": "温柔", "老公": "梦女", "是真的": "CP",
    "kswl": "CP", "磕到了": "CP", "好帅": "梦女"
}

def extract_keywords(text):
    words = jieba.lcut(text)
    keywords = [w for w in words if w not in STOP_WORDS and len(w) > 1]
    return keywords

def detect_emotion(keywords):
    for kw in keywords:
        if kw in EMOTION_KEYWORDS:
            return EMOTION_KEYWORDS[kw]
    text = " ".join(keywords)
    for phrase, emotion in EMOTION_KEYWORDS.items():
        if phrase in text:
            return emotion
    return None

def choose_speaker(prev_speaker, character_names, floor_list):
    recent_speakers = [f.get("speaker", "") for f in floor_list[-3:]]
    available = [c for c in character_names if c != prev_speaker and c not in recent_speakers]
    if not available:
        available = [c for c in character_names if c != prev_speaker]
    if not available:
        available = list(character_names)
    return random.choice(available)

def generate_reply(prev_content, prev_speaker, character_names, floor_list):
    characters = load_characters()
    templates = load_templates()

    if not character_names:
        return {"speaker": "系统", "content": "没有可用角色", "emotion": "普通"}

    speaker_name = choose_speaker(prev_speaker, character_names, floor_list)

    char = characters.get(speaker_name, {
        "name": speaker_name,
        "catchphrase": "",
        "persona": "通用",
        "default_emotion": "吃瓜"
    })

    default_emotion = char.get("default_emotion", "吃瓜")

    keywords = extract_keywords(prev_content)
    emotion = detect_emotion(keywords)
    if emotion is None:
        emotion = default_emotion

    persona_map = {
        "吃瓜": "吃瓜路人",
        "愤怒": "暴躁型",
        "挑事": "阴阳怪气型",
        "CP": "CP脑型",
        "温柔": "妈粉型",
        "梦女": "梦女型",
        "冷静": "理中客型",
        "心虚": "谜语人型",
        "吐槽": "歪楼型",
        "震惊": "吃瓜路人"
    }

    persona_type = persona_map.get(default_emotion, "通用")

    template_pool = templates.get(persona_type)
    if template_pool is None:
        template_pool = templates.get("通用", {"吃瓜": ["蹲一个后续。"]})

    pool = template_pool.get(emotion)
    if pool is None:
        emotion = "吃瓜"
        pool = template_pool.get("吃瓜", ["蹲一个后续。"])

    template = random.choice(pool)

    tone_words = ["呵呵", "草", "啧", "...", "笑死", "emmm", "啊这", "6", "就是说", "一整个"]
    catchphrase = char.get("catchphrase", "")

    reply = template.replace("{对方ID}", prev_speaker)
    reply = reply.replace("{口头禅}", catchphrase)
    reply = reply.replace("{关键词}", keywords[0] if keywords else "这事")
    reply = reply.replace("{语气词}", random.choice(tone_words))

    return {
        "speaker": speaker_name,
        "content": reply,
        "emotion": emotion
    }
