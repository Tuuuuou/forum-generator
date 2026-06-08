import jieba
import random
from data_manager import load_characters, load_templates

STOP_WORDS = {"的", "了", "是", "我", "你", "他", "她", "它", "们", "这", "那", "不", "就", "也", "都", "在", "有", "和", "与", "或", "吗", "呢", "吧", "啊", "很", "还", "要", "会", "可以", "这个", "那个", "什么", "怎么", "为什么"}

# ===== 话题关键词库 =====
TOPIC_KEYWORDS = {
    "饭圈": ["粉丝", "爱豆", "偶像", "塌房", "脱粉", "站姐", "唯粉", "毒唯", "CP粉", "磕", "应援", "控评"],
    "恐怖": ["恐怖", "鬼", "诡异", "吓人", "半夜", "灵异", "害怕"],
    "校园": ["学校", "老师", "同学", "考试", "作业", "宿舍", "学霸", "学渣", "挂科"],
    "CP": ["CP", "磕", "糖", "发糖", "kswl", "是真的", "锁了", "好甜"],
    "搞笑": ["笑死", "哈哈哈", "搞笑", "离谱", "社死", "尴尬", "沙雕"],
    "悬疑": ["真相", "证据", "线索", "分析", "怀疑", "细思极恐"],
    "职场": ["老板", "公司", "同事", "工资", "加班", "辞职", "摸鱼", "画饼", "996"],
    "游戏": ["游戏", "开黑", "排位", "队友", "操作", "团战", "段位"],
    "宠物": ["猫", "狗", "喵", "汪", "主子", "铲屎官", "可爱", "萌"],
    "日常": ["今天", "昨天", "吃了", "买了", "分享", "日常"],
    "考试": ["考试", "复习", "挂科", "及格", "成绩", "裸考"],
    "玄学": ["星座", "塔罗", "占卜", "运势", "水逆"],
    "穿搭": ["穿搭", "衣服", "搭配", "显瘦", "好看"],
    "美食": ["好吃", "难吃", "外卖", "奶茶", "火锅", "探店"]
}

# ===== 情绪关键词库 =====
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

def detect_topic(keywords):
    scores = {}
    for topic, topic_words in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in topic_words)
        if score > 0:
            scores[topic] = score
    if not scores:
        return "日常"
    return max(scores, key=scores.get)

def detect_emotion(keywords):
    for kw in keywords:
        if kw in EMOTION_KEYWORDS:
            return EMOTION_KEYWORDS[kw]
    text = " ".join(keywords)
    for phrase, emotion in EMOTION_KEYWORDS.items():
        if phrase in text:
            return emotion
    return None

# ===== 智能选角色（核心！不是纯随机）=====
def score_character(char_data, topic, emotion, keywords):
    score = 0
    persona = char_data.get("persona", "") + char_data.get("catchphrase", "")
    default_emotion = char_data.get("default_emotion", "")

    if default_emotion == emotion:
        score += 5

    topic_map = {
        "职场": ["职场", "老板", "加班", "摸鱼", "画饼", "社畜"],
        "饭圈": ["粉丝", "爱豆", "偶像", "唯粉", "毒唯"],
        "CP": ["CP", "磕", "糖", "甜"],
        "恐怖": ["恐怖", "鬼", "灵异", "胆小"],
        "校园": ["校园", "学生", "考试", "宿舍"],
        "游戏": ["游戏", "开黑", "排位", "队友"],
        "宠物": ["猫", "狗", "宠", "萌"],
        "考试": ["考试", "复习", "学霸", "学渣"],
    }
    for tag in topic_map.get(topic, []):
        if tag in persona:
            score += 3
    return score

def choose_best_character(candidates, topic, emotion, keywords):
    chars = load_characters()
    best = None
    best_score = -1
    for name in candidates:
        if name not in chars:
            continue
        s = score_character(chars[name], topic, emotion, keywords)
        if s > best_score:
            best_score = s
            best = name
    return best or random.choice(candidates)

def choose_speaker(prev_speaker, character_names, floor_list):
    all_text = " ".join(f.get("content", "") for f in floor_list)
    all_kw = extract_keywords(all_text)
    topic = detect_topic(all_kw)
    emotion = detect_emotion(all_kw)

    recent = [f.get("speaker") for f in floor_list[-3:]]
    available = [c for c in character_names if c != prev_speaker and c not in recent]
    if not available:
        available = [c for c in character_names if c != prev_speaker]
    if not available:
        available = character_names

    return choose_best_character(available, topic, emotion, all_kw)

# ===== 主回复生成 =====
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
    emotion = detect_emotion(keywords) or default_emotion

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
    template_pool = templates.get(persona_type) or templates.get("通用", {"吃瓜": ["蹲后续"]})
    pool = template_pool.get(emotion) or template_pool.get("吃瓜", ["蹲一个后续。"])
    template = random.choice(pool)

    tone_words = ["呵呵", "草", "啧", "...", "笑死", "emmm", "啊这", "6", "就是说", "一整个", "救命"]
    reply = template.replace("{对方ID}", prev_speaker)
    reply = reply.replace("{口头禅}", char.get("catchphrase", ""))
    reply = reply.replace("{关键词}", keywords[0] if keywords else "这事")
    reply = reply.replace("{语气词}", random.choice(tone_words))

    return {
        "speaker": speaker_name,
        "content": reply,
        "emotion": emotion
    }
