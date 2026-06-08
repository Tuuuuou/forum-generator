import jieba
import random
from data_manager import load_characters, load_templates

STOP_WORDS = {"的", "了", "是", "我", "你", "他", "她", "它", "们", "这", "那", "不", "就", "也", "都", "在", "有", "和", "与", "或", "吗", "呢", "吧", "啊", "很", "还", "要", "会", "可以", "这个", "那个", "什么", "怎么", "为什么"}

# 话题关键词库
TOPIC_KEYWORDS = {
    "饭圈": ["粉丝", "爱豆", "偶像", "塌房", "脱粉", "站姐", "唯粉", "毒唯", "CP粉", "磕", "打歌", "回归", "直拍", "应援", "控评", "反黑", "超话"],
    "恐怖": ["恐怖", "鬼", "诡异", "吓人", "背后", "影子", "半夜", "走廊", "哭声", "消失", "失踪", "密室", "闹鬼", "灵异", "死", "诅咒", "阴森", "蜡烛", "害怕", "不敢"],
    "校园": ["学校", "班级", "老师", "同学", "考试", "作业", "宿舍", "食堂", "选修", "奖学金", "点名", "逃课", "图书馆", "自习", "班会", "班长", "学霸", "学渣", "期末", "挂科"],
    "CP": ["CP", "cp", "磕", "糖", "发糖", "在一起", "好配", "kswl", "是真的", "锁了", "双担", "爸妈", "爱情", "结婚", "般配", "原地结婚", "好甜", "嗑死"],
    "搞笑": ["笑死", "哈哈哈", "搞笑", "离谱", "社死", "翻车", "尴尬", "绝了", "救命", "哈哈", "笑疯了", "名场面", "笑不活了", "沙雕", "人才"],
    "悬疑": ["谁", "为什么", "怎么", "真相", "证据", "线索", "推测", "分析", "怀疑", "到底", "究竟", "难道", "不会吧", "细思极恐", "不对劲"],
    "职场": ["老板", "公司", "同事", "工资", "加班", "辞职", "甲方", "乙方", "996", "内卷", "摸鱼", "年会", "升职", "跳槽", "年终奖"],
    "游戏": ["游戏", "开黑", "排位", "段位", "队友", "对面", "操作", "团战", "输出", "辅助", "打野", "ADC", "单排", "双排", "连跪"],
    "宠物": ["猫", "狗", "喵", "汪", "主子", "铲屎官", "毛孩子", "可爱", "萌", "吸猫", "撸狗", "流浪", "领养"],
    "日常": ["今天", "昨天", "刚刚", "吃了", "买了", "去了", "看了", "听了", "分享", "记录", "打卡", "日常"],
    "考试": ["考试", "复习", "重点", "挂科", "及格", "成绩", "绩点", "作弊", "监考", "补考", "重修", "裸考"],
    "玄学": ["星座", "塔罗", "占卜", "运势", "水逆", "牌面", "天蝎", "射手", "双鱼", "算命", "风水"],
    "穿搭": ["穿搭", "衣服", "裙子", "裤子", "鞋", "包包", "显瘦", "搭配", "好看", "丑", "退", "买"],
    "美食": ["好吃", "难吃", "外卖", "探店", "打卡", "餐厅", "奶茶", "火锅", "烧烤", "甜品", "绝了", "推荐"],
    "修仙": ["宗门", "师门", "师兄", "师弟", "门派", "剑修", "剑宗", "修行", "功法", "慎言"]
}

# 情绪关键词库
EMOTION_KEYWORDS = {
    "愤怒": ["挂人", "爆料", "举报", "你出来", "你再说", "不服", "凭什么", "恶心", "要不要脸", "滚", "别太过分", "你配吗", "要点脸", "素质", "你tm", "有病"],
    "震惊": ["真的假的", "反转", "天哪", "我的天", "不是吧", "居然", "竟然", "不敢相信", "震惊", "什么情况", "我靠", "卧槽", "离谱他妈给离谱开门"],
    "吃瓜": ["蹲", "等后续", "求私", "笑死", "哈哈哈", "精彩", "围观", "吃瓜", "前排", "课代表", "总结", "还有吗", "详细说说"],
    "温柔": ["心疼", "抱抱", "难过", "好温柔", "好可爱", "辛苦了", "注意休息", "早点睡", "爱你", "摸摸", "乖", "没事的", "会好的"],
    "吐槽": ["离谱", "无语", "就这", "救命", "尴尬", "社死", "翻车", "绝了", "笑不活了", "人才", "服了", "我真服了"],
    "心虚": ["删了", "懂的都懂", "不能说", "不好说", "等实锤", "老粉知道", "澄清", "不是我", "别截图", "当我没说"],
    "冷静": ["客观来说", "理性分析", "有一说一", "不吹不黑", "两边都有", "各打五十大板", "实事求是", "冷静看待"],
    "CP": ["kswl", "是真的", "锁了", "般配", "在一起", "发糖", "好甜", "磕到了", "双担", "我的cp", "szd"],
    "梦女": ["老公", "老婆", "结婚", "嫁给我", "领证", "做梦", "梦到", "我的男人", "我的女人", "想嫁"],
    "挑事": ["对比", "别家不行", "我们门派更强", "你们宗门规矩太差"]
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
    scores = {}
    for emotion, emotion_words in EMOTION_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in emotion_words)
        if score > 0:
            scores[emotion] = score
    if not scores:
        return None
    return max(scores, key=scores.get)


def score_character(char_data, topic, emotion, keywords):
    score = 0
    persona = char_data.get("persona", "")
    catchphrase = char_data.get("catchphrase", "")
    combined = persona + catchphrase

    for kw in keywords:
        if kw in combined:
            score += 2

    default_emotion = char_data.get("default_emotion", "")
    if default_emotion == emotion:
        score += 5
    elif emotion and default_emotion in ["吃瓜", "吐槽"]:
        score += 2

    topic_persona_map = {
        "恐怖": ["恐怖", "鬼", "诡异", "吓人", "灵异", "胆小", "探灵", "害怕"],
        "校园": ["校园", "学生", "学霸", "学渣", "老师", "宿舍", "同学", "学校"],
        "CP": ["CP", "磕", "糖", "甜", "爱情", "般配", "cp", "嗑"],
        "搞笑": ["搞笑", "沙雕", "离谱", "翻车", "社死", "笑死", "幽默"],
        "悬疑": ["分析", "推测", "证据", "线索", "理性", "逻辑", "推理"],
        "饭圈": ["粉丝", "爱豆", "偶像", "站姐", "唯粉", "毒唯", "塌房", "控评"],
        "职场": ["职场", "老板", "公司", "上班", "加班", "甲方", "摸鱼"],
        "游戏": ["游戏", "开黑", "排位", "操作", "队友", "团战", "段位"],
        "宠物": ["猫", "狗", "宠", "主子", "毛孩子", "可爱", "萌"],
        "考试": ["考试", "复习", "挂科", "学霸", "学渣", "及格", "裸考"],
        "玄学": ["星座", "塔罗", "占卜", "运势", "水逆", "算命"],
        "穿搭": ["穿搭", "衣服", "显瘦", "搭配", "时尚", "好看"],
        "美食": ["美食", "好吃", "探店", "外卖", "餐厅", "打卡"],
        "日常": ["日常", "生活", "分享", "记录", "打卡"],
        "修仙": ["宗门", "师门", "师兄", "师弟", "门派", "剑修", "剑宗", "修行", "功法", "慎言"]
    }
    for tag in topic_persona_map.get(topic, []):
        if tag in combined:
            score += 3

    return score


def choose_best_character(character_names, topic, emotion, keywords):
    characters = load_characters()
    best_name = None
    best_score = -1
    for name in character_names:
        if name not in characters:
            continue
        char_data = characters[name]
        s = score_character(char_data, topic, emotion, keywords)
        if s > best_score:
            best_score = s
            best_name = name
    if best_name is None and character_names:
        best_name = random.choice(character_names)
    return best_name


def choose_speaker(prev_speaker, character_names, floor_list):
    all_text = " ".join([f.get("content", "") for f in floor_list])
    all_keywords = extract_keywords(all_text)
    topic = detect_topic(all_keywords)
    emotion = detect_emotion(all_keywords)

    if len(floor_list) <= 5:
        recent_speakers = [f.get("speaker", "") for f in floor_list[-2:]]
        available = [c for c in character_names if c != prev_speaker and c not in recent_speakers]
        if not available:
            available = [c for c in character_names if c != prev_speaker]
        if not available:
            available = list(character_names)
        if available:
            return choose_best_character(available, topic, emotion, all_keywords), topic, emotion

    recent_speakers = [f.get("speaker", "") for f in floor_list[-3:]]
    available = [c for c in character_names if c != prev_speaker and c not in recent_speakers]
    if not available:
        available = [c for c in character_names if c != prev_speaker]
    if not available:
        available = list(character_names)
    return random.choice(available), topic, emotion


def generate_reply(prev_content, prev_speaker, character_names, floor_list):
    characters = load_characters()
    templates = load_templates()

    if not character_names:
        return {"speaker": "系统", "content": "没有可用角色", "emotion": "普通", "topic": "日常"}

    speaker_name, topic, detected_emotion = choose_speaker(prev_speaker, character_names, floor_list)

    char = characters.get(speaker_name, {
        "name": speaker_name,
        "catchphrase": "",
        "persona": "通用",
        "default_emotion": "吃瓜"
    })

    default_emotion = char.get("default_emotion", "吃瓜")
    emotion = detected_emotion if detected_emotion else default_emotion

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
        pool = template_pool.get("吃瓜", ["蹲一个后续。"])

    template = random.choice(pool)

    tone_words = ["呵呵", "草", "啧", "...", "笑死", "emmm", "啊这", "6", "就是说", "一整个", "救命"]
    catchphrase = char.get("catchphrase", "")

    curr_keywords = extract_keywords(prev_content)

    reply = template.replace("{对方ID}", prev_speaker)
    reply = reply.replace("{口头禅}", catchphrase)
    reply = reply.replace("{关键词}", curr_keywords[0] if curr_keywords else "这事")
    reply = reply.replace("{语气词}", random.choice(tone_words))

    return {
        "speaker": speaker_name,
        "content": reply,
        "emotion": emotion,
        "topic": topic
    }
