import textwrap
from PIL import Image, ImageDraw, ImageFont
import os
from config import AVATARS_DIR, EXPORTS_DIR

# 尝试加载中文字体
FONT_PATH = None
for p in ["C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/msyh.ttc",
          "/System/Library/Fonts/PingFang.ttc", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]:
    if os.path.exists(p):
        FONT_PATH = p
        break

def get_font(size, bold=False):
    if FONT_PATH:
        try:
            return ImageFont.truetype(FONT_PATH, size)
        except:
            pass
    return ImageFont.load_default()

def render_floor(floor_data, width=620):
    num = floor_data.get("floor_num", 1)
    speaker = floor_data.get("speaker", "匿名")
    content = floor_data.get("content", "")
    avatar_file = floor_data.get("avatar", "default.png")
    avatar_path = os.path.join(AVATARS_DIR, avatar_file)
    is_op = (speaker == "楼主")

    # 正文自动换行
    content_lines = []
    for line in content.split("\n"):
        if len(line) > 36:
            wrapped = textwrap.wrap(line, width=36)
            content_lines.extend(wrapped)
        else:
            content_lines.append(line)

    line_height = 30
    content_height = max(len(content_lines) * line_height + 40, 80)
    
    # 楼主帖子高度稍大
    floor_height = 90 + content_height
    if is_op:
        floor_height += 30

    # 背景色：楼主淡蓝，其他白色
    bg_color = (245, 250, 255) if is_op else (255, 255, 255)
    img = Image.new("RGB", (width, floor_height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # 边框
    draw.rectangle([(8, 2), (width-8, floor_height-2)], outline=(210, 220, 235), width=1)

    # 圆形头像
    avatar_size = 44
    avatar_x, avatar_y = 20, 18
    try:
        avatar = Image.open(avatar_path).resize((avatar_size, avatar_size))
        mask = Image.new("L", (avatar_size, avatar_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
        img.paste(avatar, (avatar_x, avatar_y), mask)
    except:
        draw.ellipse([avatar_x, avatar_y, avatar_x+avatar_size, avatar_y+avatar_size],
                     fill=(200, 210, 225), outline=(180, 190, 210), width=2)

    # 用户名
    font_name = get_font(15, bold=True)
    font_info = get_font(11)
    name_color = (40, 68, 140)
    if is_op:
        speaker_text = f"📌 {speaker}（楼主）"
    else:
        speaker_text = speaker
    draw.text((75, 18), speaker_text, fill=name_color, font=font_name)

    # 楼层信息
    likes = floor_data.get("likes", 0)
    floor_time = floor_data.get("time", "刚刚")
    info_text = f"🏠 第{num}楼  ⏱ {floor_time}  👍 {likes}"
    draw.text((75, 42), info_text, fill=(150, 160, 180), font=font_info)

    # 正文内容
    font_content = get_font(16)
    text_y = 75 if not is_op else 85
    for line in content_lines:
        draw.text((25, text_y), line, fill=(50, 55, 65), font=font_content)
        text_y += line_height

    # 楼主蓝底标签
    if is_op:
        tag_y = text_y + 8
        draw.rounded_rectangle([(25, tag_y), (100, tag_y+20)], radius=4, fill=(26, 115, 232), outline=None)
        draw.text((35, tag_y+2), "楼主", fill=(255, 255, 255), font=get_font(11))

    return img

def render_long_image(floor_list, width=620):
    floor_images = []
    for i, floor in enumerate(floor_list):
        floor["floor_num"] = i + 1
        floor_images.append(render_floor(floor, width))

    # 顶部蓝色标题栏
    header_height = 60
    total_height = header_height + sum(img.height for img in floor_images)
    long_img = Image.new("RGB", (width, total_height), color=(255, 255, 255))
    
    draw = ImageDraw.Draw(long_img)
    draw.rectangle([(0, 0), (width, header_height)], fill=(232, 240, 254))
    draw.text((20, 15), "论坛体生成截图", fill=(26, 115, 232), font=get_font(18, bold=True))
    draw.text((20, 40), "由 NPC水论坛模拟器 导出", fill=(120, 140, 170), font=get_font(12))

    y_offset = header_height
    for img in floor_images:
        long_img.paste(img, (0, y_offset))
        y_offset += img.height

    return long_img

def export_image(floor_list, filename="output.png"):
    long_img = render_long_image(floor_list)
    filepath = os.path.join(EXPORTS_DIR, filename)
    long_img.save(filepath)
    return filepath
