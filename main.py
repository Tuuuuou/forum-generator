import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import json
import os
import random
from datetime import datetime

from config import DATA_DIR, AVATARS_DIR
from data_manager import load_scenes, load_characters, init_default_data
from reply_engine import generate_reply
from renderer import export_image

init_default_data()

class ForumGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("论坛体自动回复生成器")
        self.root.geometry("1000x700")

        self.scenes = load_scenes()
        self.characters = load_characters()
        self.floor_list = []
        self.active_characters = []

        self.setup_ui()

    def setup_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        # 左侧控制面板
        left_frame = tk.Frame(self.root, padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsew")

        tk.Label(left_frame, text="1. 选择场景", font=("", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.scene_var = tk.StringVar(value="自定义")
        scene_names = ["自定义"] + list(self.scenes.keys())
        self.scene_combo = ttk.Combobox(left_frame, textvariable=self.scene_var, values=scene_names, state="readonly")
        tk.Button(left_frame, text="新建场景", command=self.new_scene).pack(fill="x", pady=(0,5))
        self.scene_combo.pack(fill="x", pady=(0, 5))
        self.scene_combo.bind("<<ComboboxSelected>>", self.on_scene_select)

        tk.Label(left_frame, text="论坛名称:").pack(anchor="w")
        self.forum_name_entry = tk.Entry(left_frame)
        self.forum_name_entry.insert(0, "论坛名称")
        self.forum_name_entry.pack(fill="x", pady=(0, 5))

        tk.Label(left_frame, text="帖子标题:").pack(anchor="w")
        self.title_entry = tk.Entry(left_frame)
        self.title_entry.insert(0, "【帖子标题】")
        self.title_entry.pack(fill="x", pady=(0, 10))

        tk.Label(left_frame, text="2. 角色列表", font=("", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.char_listbox = tk.Listbox(left_frame, height=6)
        self.char_listbox.pack(fill="x", pady=(0, 5))

        char_select_frame = tk.Frame(left_frame)
        char_select_frame.pack(fill="x", pady=(0, 5))
        self.char_select_var = tk.StringVar()
        self.char_select_combo = ttk.Combobox(char_select_frame, textvariable=self.char_select_var,
                                              values=list(self.characters.keys()), state="readonly")
        self.char_select_combo.pack(side="left", fill="x", expand=True)
        tk.Button(char_select_frame, text="添加", command=self.add_character).pack(side="left", padx=2)
        tk.Button(char_select_frame, text="新建角色", command=self.new_character).pack(side="left", padx=2)
        tk.Button(left_frame, text="删除选中角色", command=self.remove_character).pack(fill="x", pady=(0, 10))

        tk.Label(left_frame, text="3. 楼主帖（开篇）", font=("", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.opening_text = tk.Text(left_frame, height=5)
        self.opening_text.insert("1.0", "在这里写下楼主帖的内容...")
        self.opening_text.pack(fill="x", pady=(0, 5))
        tk.Button(left_frame, text="发布开篇", command=self.post_opening, bg="#4a90d9", fg="white").pack(fill="x", pady=(0, 10))

        tk.Label(left_frame, text="4. 操作", font=("", 12, "bold")).pack(anchor="w", pady=(0, 5))
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="自动生成回复", command=self.auto_reply, bg="#27ae60", fg="white").pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Button(btn_frame, text="手动添加楼层", command=self.manual_floor).pack(side="left", fill="x", expand=True)

        tk.Button(left_frame, text="导出长截图", command=self.export, bg="#e67e22", fg="white").pack(fill="x", pady=(10, 0))
        tk.Button(left_frame, text="清空重建", command=self.clear_all).pack(fill="x", pady=(5, 0))

        # 右侧预览面板
        right_frame = tk.Frame(self.root, padx=10, pady=10, bg="#f0f0f0")
        right_frame.grid(row=0, column=1, sticky="nsew")

        tk.Label(right_frame, text="帖子预览", font=("", 12, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(0, 5))

        self.canvas = tk.Canvas(right_frame, bg="white", width=500)
        scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=600,tags="preview_window")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def on_scene_select(self, event=None):
        scene_name = self.scene_var.get()
        if scene_name == "自定义":
            return
        scene = self.scenes.get(scene_name, {})
        self.forum_name_entry.delete(0, tk.END)
        self.forum_name_entry.insert(0, scene.get("forum_name", ""))
        self.active_characters = list(scene.get("preset_characters", []))
        self.refresh_char_listbox()

    def add_character(self):
        name = self.char_select_var.get()
        if name and name not in self.active_characters:
            self.active_characters.append(name)
            self.refresh_char_listbox()

    def remove_character(self):
        sel = self.char_listbox.curselection()
        if sel:
            name = self.char_listbox.get(sel[0])
            self.active_characters.remove(name)
            self.refresh_char_listbox()

    def refresh_char_listbox(self):
        self.char_listbox.delete(0, tk.END)
        for name in self.active_characters:
            self.char_listbox.insert(tk.END, name)

    def post_opening(self):
        content = self.opening_text.get("1.0", tk.END).strip()
        if not content:
            return
        import random
        from datetime import datetime, timedelta
        now = datetime.now()
        random_minutes = random.randint(1, 60*24*3)
        post_time = now - timedelta(minutes=random_minutes)
        time_str = post_time.strftime("%H:%M") if random_minutes < 60*24 else post_time.strftime("%m-%d %H:%M")
        
        self.floor_list = [{
            "speaker": "楼主",
            "content": content,
            "avatar": "default.png",
            "likes": random.randint(10, 999),
            "time": time_str
        }]
        self.refresh_preview()

    def auto_reply(self):
        if not self.floor_list:
            messagebox.showwarning("提示", "请先发布开篇帖")
            return
        if not self.active_characters:
            messagebox.showwarning("提示", "请先添加角色")
            return

        prev = self.floor_list[-1]
        prev_content = prev.get("content", "")
        prev_speaker = prev.get("speaker", "楼主")

        import random
        from datetime import datetime, timedelta
        last_time_str = prev.get("time", "00:00")
        now = datetime.now()
        random_minutes = random.randint(1, 120)
        post_time = now - timedelta(minutes=random_minutes)
        if random_minutes < 60:
            time_str = post_time.strftime("%H:%M")
        elif random_minutes < 60*24:
            time_str = "昨天 " + post_time.strftime("%H:%M")
        else:
            time_str = post_time.strftime("%m-%d %H:%M")

        try:
            result = generate_reply(prev_content, prev_speaker, self.active_characters, self.floor_list)
            new_floor = {
                "speaker": result["speaker"],
                "content": result["content"],
                "avatar": self.characters.get(result["speaker"], {}).get("avatar", "default.png"),
                "likes": random.randint(0, 999),
                "time": time_str
            }
            self.floor_list.append(new_floor)
            self.refresh_preview()
        except Exception as e:
            messagebox.showerror("生成失败", str(e))

    def manual_floor(self):
        if not self.active_characters:
            messagebox.showwarning("提示", "请先添加角色")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("手动添加楼层")
        dialog.geometry("400x300")

        tk.Label(dialog, text="发言者:").pack(pady=(10, 0))
        speaker_var = tk.StringVar(value=self.active_characters[0])
        ttk.Combobox(dialog, textvariable=speaker_var, values=self.active_characters, state="readonly").pack()

        tk.Label(dialog, text="时间（留空随机生成）:").pack(pady=(10,0))
        time_entry = tk.Entry(dialog)
        time_entry.pack()
        tk.Label(dialog, text="内容:").pack(pady=(10, 0))
        content_text = tk.Text(dialog, height=8)
        content_text.pack(fill="both", expand=True, padx=10, pady=5)

        def submit():
            content = content_text.get("1.0", tk.END).strip()
            if content:
                time_str = time_entry.get().strip()
                if not time_str:
                    import random
                    from datetime import datetime, timedelta
                    now = datetime.now()
                    random_minutes = random.randint(1, 180)
                    post_time = now - timedelta(minutes=random_minutes)
                    if random_minutes < 60:
                        time_str = post_time.strftime("%H:%M")
                    elif random_minutes < 60*24:
                        time_str = "昨天 " + post_time.strftime("%H:%M")
                    else:
                        time_str = post_time.strftime("%m-%d %H:%M")
                self.floor_list.append({
                    "speaker": speaker_var.get(),
                    "content": content,
                    "avatar": self.characters.get(speaker_var.get(), {}).get("avatar", "default.png"),
                    "likes": random.randint(0, 999),
                    "time": time_str
                })
                self.refresh_preview()
                dialog.destroy()

    def refresh_preview(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        forum_name = self.forum_name_entry.get()
        title = self.title_entry.get()

        tk.Label(self.scrollable_frame, text=f"【{forum_name}】", font=("", 12, "bold"), bg="white",
                 fg="#666").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Label(self.scrollable_frame, text=title, font=("", 14, "bold"), bg="white").pack(anchor="w", padx=10, pady=(0, 10))
        ttk.Separator(self.scrollable_frame, orient="horizontal").pack(fill="x")

        for i, floor in enumerate(self.floor_list):
            f = tk.Frame(self.scrollable_frame, bg="white", pady=8, padx=10)
            f.pack(fill="x")
            tk.Label(f, text=f"{floor['speaker']}", font=("", 11, "bold"), bg="white", fg="#28468c").pack(anchor="w")
            tk.Label(f, text=f"第{i+1}楼 · 赞 {floor.get('likes', 0)}", font=("", 9), bg="white", fg="#999").pack(anchor="w")
            tk.Label(f, text=floor["content"], font=("", 11), bg="white", wraplength=580, justify="left").pack(anchor="w", pady=(5, 0))
            ttk.Separator(self.scrollable_frame, orient="horizontal").pack(fill="x", padx=10)
            self.scrollable_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.yview_moveto(0)

    def export(self):
        if not self.floor_list:
            messagebox.showwarning("提示", "没有可导出的内容")
            return
        try:
            filepath = export_image(self.floor_list, f"forum_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            messagebox.showinfo("导出成功", f"图片已保存到:\n{filepath}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def clear_all(self):
        self.floor_list = []
        self.active_characters = []
        self.refresh_preview()
        self.refresh_char_listbox()
        self.opening_text.delete("1.0", tk.END)
        self.opening_text.insert("1.0", "在这里写下楼主帖的内容...")
        
    def new_character(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新建角色")
        dialog.geometry("350x280")

        tk.Label(dialog, text="角色ID（唯一标识）:").pack(pady=(10,0))
        id_entry = tk.Entry(dialog)
        id_entry.pack()

        tk.Label(dialog, text="显示昵称:").pack(pady=(10,0))
        name_entry = tk.Entry(dialog)
        name_entry.pack()

        tk.Label(dialog, text="人设描述（选填）:").pack(pady=(10,0))
        persona_entry = tk.Entry(dialog)
        persona_entry.pack()

        tk.Label(dialog, text="口头禅（选填）:").pack(pady=(10,0))
        catch_entry = tk.Entry(dialog)
        catch_entry.pack()

        tk.Label(dialog, text="默认情绪:").pack(pady=(10,0))
        emotion_combo = ttk.Combobox(dialog, values=["吃瓜","愤怒","温柔","吐槽","震惊","冷静","CP","梦女","心虚"], state="readonly")
        emotion_combo.current(0)
        emotion_combo.pack()

        def save():
            char_id = id_entry.get().strip()
            if not char_id:
                messagebox.showwarning("提示", "请输入角色ID")
                return
            try:
                chars = load_characters()
            except:
                chars = {}
            if char_id in chars:
                messagebox.showwarning("提示", "角色ID已存在")
                return
            chars[char_id] = {
                "name": name_entry.get().strip() or char_id,
                "avatar": "default.png",
                "persona": persona_entry.get().strip(),
                "catchphrase": catch_entry.get().strip(),
                "default_emotion": emotion_combo.get(),
                "style": {"sentence_length":"中","aggressiveness":"中","humor":"中"}
            }
            try:
                save_characters(chars)
            except:
                pass
            self.characters = chars
            self.char_select_combo['values'] = list(chars.keys())
            messagebox.showinfo("成功", f"角色 {char_id} 创建成功")
            dialog.destroy()

        tk.Button(dialog, text="保存", command=save, bg="#27ae60", fg="white").pack(pady=15)
    def new_scene(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新建场景")
        dialog.geometry("400x250")

        tk.Label(dialog, text="场景名称:").pack(pady=(10,0))
        name_entry = tk.Entry(dialog)
        name_entry.pack()

        tk.Label(dialog, text="论坛名称:").pack(pady=(10,0))
        forum_entry = tk.Entry(dialog)
        forum_entry.pack()

        tk.Label(dialog, text="预设角色（用逗号分隔）:").pack(pady=(10,0))
        chars_entry = tk.Entry(dialog)
        chars_entry.pack()

        def save():
            scene_name = name_entry.get().strip()
            if not scene_name:
                messagebox.showwarning("提示", "请输入场景名称")
                return
            try:
                scenes = load_scenes()
            except:
                scenes = {}
            chars_str = chars_entry.get().strip()
            preset_chars = [c.strip() for c in chars_str.split(",") if c.strip()] if chars_str else []
            scenes[scene_name] = {
                "forum_name": forum_entry.get().strip() or scene_name,
                "preset_characters": preset_chars
            }
            try:
                from data_manager import save_scenes
                save_scenes(scenes)
            except:
                pass
            self.scenes = scenes
            scene_names = ["自定义"] + list(scenes.keys())
            self.scene_combo['values'] = scene_names
            messagebox.showinfo("成功", f"场景 {scene_name} 已创建")
            dialog.destroy()

        tk.Button(dialog, text="保存", command=save, bg="#27ae60", fg="white").pack(pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = ForumGeneratorApp(root)
    root.mainloop()
