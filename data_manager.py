import json
import os
from config import SCENES_FILE, CHARACTERS_FILE, TEMPLATES_FILE

def load_json(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_scenes():
    return load_json(SCENES_FILE)

def load_characters():
    return load_json(CHARACTERS_FILE)

def load_templates():
    return load_json(TEMPLATES_FILE)

def save_scenes(data):
    save_json(SCENES_FILE, data)

def save_characters(data):
    save_json(CHARACTERS_FILE, data)

def save_templates(data):
    save_json(TEMPLATES_FILE, data)

def init_default_data():
    if not os.path.exists(SCENES_FILE) or os.path.getsize(SCENES_FILE) == 0:
        save_scenes({
            "修仙门派论坛": {
                "forum_name": "青云门内部论坛",
                "preset_characters": ["大师兄", "吃瓜师弟", "暴躁师弟", "隔壁门派弟子"]
            },
            "饭圈讨论楼": {
                "forum_name": "娱乐八卦论坛",
                "preset_characters": ["毒唯", "CP粉", "路人", "站姐"]
            },
            "匿名爆料区": {
                "forum_name": "匿名吐槽区",
                "preset_characters": ["楼主(匿名)", "吃瓜群众", "当事人", "求私信的"]
            }
        })

    if not os.path.exists(CHARACTERS_FILE) or os.path.getsize(CHARACTERS_FILE) == 0:
        save_characters({
            "大师兄": {
                "name": "大师兄",
                "avatar": "default.png",
                "persona": "稳重但话少，用敬语阴阳怪气",
                "catchphrase": "师弟，慎言。",
                "default_emotion": "冷静",
                "style": {"sentence_length": "短", "aggressiveness": "低", "humor": "中"}
            },
            "吃瓜师弟": {
                "name": "云游弟子",
                "avatar": "default.png",
                "persona": "看热闹不嫌事大，什么帖子都要蹲",
                "catchphrase": "前排占座。",
                "default_emotion": "吃瓜",
                "style": {"sentence_length": "中", "aggressiveness": "低", "humor": "高"}
            },
            "暴躁师弟": {
                "name": "剑修不认输",
                "avatar": "default.png",
                "persona": "一点就炸，看谁都不顺眼",
                "catchphrase": "不服来辩。",
                "default_emotion": "愤怒",
                "style": {"sentence_length": "短", "aggressiveness": "高", "humor": "低"}
            },
            "隔壁门派弟子": {
                "name": "隔壁剑宗弟子",
                "avatar": "default.png",
                "persona": "表面客气暗地挑事",
                "catchphrase": "我们剑宗就没这个问题。",
                "default_emotion": "挑事",
                "style": {"sentence_length": "中", "aggressiveness": "中", "humor": "中"}
            },
            "毒唯": {
                "name": "只爱我担",
                "avatar": "default.png",
                "persona": "护主狂魔，谁说我担跟谁急",
                "catchphrase": "有锤放锤，没锤闭嘴。",
                "default_emotion": "愤怒",
                "style": {"sentence_length": "中", "aggressiveness": "高", "humor": "低"}
            },
            "CP粉": {
                "name": "磕到了谢谢",
                "avatar": "default.png",
                "persona": "什么都能磕，什么都是糖",
                "catchphrase": "这是真的。",
                "default_emotion": "吃瓜",
                "style": {"sentence_length": "短", "aggressiveness": "低", "humor": "高"}
            },
            "路人": {
                "name": "路过看看",
                "avatar": "default.png",
                "persona": "真路人，偶尔说风凉话",
                "catchphrase": "就我觉得...",
                "default_emotion": "吃瓜",
                "style": {"sentence_length": "中", "aggressiveness": "低", "humor": "中"}
            },
            "站姐": {
                "name": "高清直拍站",
                "avatar": "default.png",
                "persona": "甩图说话，技术流",
                "catchphrase": "图来了，自己看。",
                "default_emotion": "冷静",
                "style": {"sentence_length": "短", "aggressiveness": "中", "humor": "低"}
            },
            "吃瓜群众": {
                "name": "瓜田里的猹",
                "avatar": "default.png",
                "persona": "专门蹲爆料，求更多",
                "catchphrase": "还有吗还有吗？",
                "default_emotion": "吃瓜",
                "style": {"sentence_length": "短", "aggressiveness": "低", "humor": "高"}
            },
            "当事人": {
                "name": "别猜了是我",
                "avatar": "default.png",
                "persona": "被爆料后自己跳出来对线",
                "catchphrase": "楼主你出来，我们聊聊。",
                "default_emotion": "愤怒",
                "style": {"sentence_length": "中", "aggressiveness": "高", "humor": "低"}
            },
            "求私信的": {
                "name": "求私求私",
                "avatar": "default.png",
                "persona": "只想吃完整的瓜",
                "catchphrase": "求私！好人一生平安！",
                "default_emotion": "吃瓜",
                "style": {"sentence_length": "短", "aggressiveness": "低", "humor": "中"}
            }
        })

    if not os.path.exists(TEMPLATES_FILE) or os.path.getsize(TEMPLATES_FILE) == 0:
        save_templates({
            "通用": {
                "吃瓜": [
                    "前排占座，等一个后续。",
                    "我就知道这帖要火。",
                    "有没有人总结一下，太长没看。",
                    "所以到底是真的还是假的？",
                    "截图了，这条必火。"
                ],
                "震惊": [
                    "？？？？",
                    "等等，信息量有点大，让我缓缓。",
                    "这是我今年看到最离谱的帖子。",
                    "真的假的？？有锤吗？？",
                    "草，这要是真的就太精彩了。"
                ],
                "愤怒": [
                    "？？？{对方ID}你出来。",
                    "截图了，等着。",
                    "已举报，不谢。",
                    "你说的每一句我都截图了。"
                ],
                "吐槽": [
                    "不是我说，这也太离谱了。{语气词}",
                    "笑死，{对方ID}你认真的吗？",
                    "我看了三遍，确认自己没看错。",
                    "今日离谱+1。"
                ],
                "温柔": [
                    "楼主别难过，抱抱。",
                    "心疼，怎么会这样...",
                    "一切都会好起来的。"
                ]
            },
            "吃瓜路人": {
                "吃瓜": [
                    "蹲，等课代表。",
                    "又来晚了，有没有好心人总结一下？",
                    "这个走向我是没想到的。",
                    "精彩，太精彩了。"
                ]
            },
            "暴躁型": {
                "愤怒": [
                    "{对方ID}你tm再说一遍？",
                    "有本事别匿名，出来对线。",
                    "你这是在找骂。{语气词}",
                    "别删帖，我已经截图了。"
                ],
                "吐槽": [
                    "就这？就这？",
                    "笑死我了，{对方ID}你是认真的吗",
                    "今日笑话+1。"
                ]
            },
            "阴阳怪气型": {
                "挑事": [
                    "我们{关键词}就没这个问题呢。",
                    "不会吧不会吧，不会真有人觉得{关键词}没问题吧？",
                    "说得好，建议加大力度。{语气词}",
                    "我只是路过，但是{对方ID}说的确实有点好笑。"
                ]
            },
            "CP脑型": {
                "吃瓜": [
                    "这是真的。",
                    "已磕，谢谢楼主。",
                    "我宣布，{关键词}是真的。",
                    "有没有人注意到{关键词}？这不是真的什么是真的？？"
                ]
            }
        })
