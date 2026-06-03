from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
from config import AVATARS_DIR, EXPORTS_DIR

FONT_PATH_SYSTEM = None
for p in ["C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/msyh.ttc",
          "/System/Library/Fonts/PingFang.ttc", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]:
    if os.path.exists(p):
        FONT_PATH_SYSTEM = p
        break

def get_font(size, bold=False):
    if FONT_PATH_SYSTEM:
        try:
            return ImageFont.truetype(FONT_PATH_SYSTEM, size)
        except:
            pass
    return ImageFont.load_default()

def render_floor(floor_data, width=600):
    num = floor_data.get("floor_num", 1)
    speaker = floor_data.get("speaker", "匿名")
    content = floor_data.get("content", "")
    avatar_file = floor_data.get("avatar", "default.png")
    avatar_path = os.path.join(AVATARS_DIR, avatar_file)

    line_height = 28
    content_lines = []
    for line in content.split("\n"):
        if len(line) > 38:
            wrapped = textwrap.wrap(line,width=38)
            content_lines.extend(wrapped)
        else:
            content_lines.append(line)

    content_height = max(len(content_lines) * line_height + 20, 60)
    floor_height = 80 + content_height
    img = Image.new("RGB", (width, floor_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 分割线
    draw.line([(10, floor_height-1), (width-10, floor_height-1)], fill=(230, 230, 230), width=1)

    # 头像
    avatar_size = 40
    avatar_x, avatar_y = 15, 15
    try:
        avatar = Image.open(avatar_path).resize((avatar_size, avatar_size))
        mask = Image.new("L", (avatar_size, avatar_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
        img.paste(avatar, (avatar_x, avatar_y), mask)
    except:
        draw.ellipse([avatar_x, avatar_y, avatar_x+avatar_size, avatar_y+avatar_size],
                     fill=(200, 200, 200), outline=(180, 180, 180))

    # 用户名和楼层
    font_name = get_font(14, bold=True)
    font_info = get_font(11)
    draw.text((65, 15), speaker, fill=(40, 40, 140), font=font_name)
    draw.text((65, 35), f"第{num}楼 · 刚刚 · 赞 {floor_data.get('likes', 0)}", fill=(150, 150, 150), font=font_info)

    # 正文
    font_content = get_font(15)
    y = 65
    for line in content_lines:
        draw.text((20, y), line, fill=(30, 30, 30), font=font_content)
        y += line_height

    return img

def render_long_image(floor_list, width=600):
    floor_images = []
    for i, floor in enumerate(floor_list):
        floor["floor_num"] = i + 1
        floor_images.append(render_floor(floor, width))

    total_height = sum(img.height for img in floor_images)
    long_img = Image.new("RGB", (width, total_height), color=(255, 255, 255))
    y_offset = 0
    for img in floor_images:
        long_img.paste(img, (0, y_offset))
        y_offset += img.height

    return long_img

def export_image(floor_list, filename="output.png"):
    long_img = render_long_image(floor_list)
    filepath = os.path.join(EXPORTS_DIR, filename)
    long_img.save(filepath)
    return filepath
