import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import json
import os
import random
from datetime import datetime

from config import DATA_DIR, AVATARS_DIR
from data_manager import load_scenes, load_characters, init_default_data, save_characters
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
        dialog.geometry("400x450")

        tk.Label(dialog, text="发言者:").pack(pady=(10,0))
        speaker_var = tk.StringVar(value=self.active_characters[0])
        ttk.Combobox(dialog, textvariable=speaker_var, values=self.active_characters, state="readonly").pack(fill="x", padx=10)

        tk.Label(dialog, text="时间（留空随机生成）:").pack(pady=(10,0))
        time_entry = tk.Entry(dialog)
        time_entry.pack(fill="x", padx=10)

        tk.Label(dialog, text="内容:").pack(pady=(10, 0))
        content_text = tk.Text(dialog, height=8)
        content_text.pack(fill="both", expand=True, padx=10, pady=5)

        add_btn = tk.Button(dialog, text="➕ 添加楼层", bg="#27ae60", fg="white", font=("", 12, "bold"),
                            command=lambda: submit())
        add_btn.pack(pady=15, ipadx=20, ipady=5)

        def submit():
            content = content_text.get("1.0", tk.END).strip()
            if content:
                time_str = time_entry.get().strip()
                if not time_str:
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

        header_frame = tk.Frame(self.scrollable_frame, bg="#e8f0fe", pady=10)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        tk.Label(header_frame, text=f"【{forum_name}】", font=("微软雅黑", 11, "bold"), bg="#e8f0fe", fg="#1a73e8").pack(anchor="w", padx=10)
        tk.Label(header_frame, text=title, font=("微软雅黑", 14, "bold"), bg="#e8f0fe", fg="#222").pack(anchor="w", padx=10)

        if self.floor_list:
            first_floor = self.floor_list[0]
            info_text = f"🕒 {first_floor.get('time', '未知')}  💬 {len(self.floor_list)}回复  👀 {random.randint(1000,9999)}浏览"
            info_label = tk.Label(self.scrollable_frame, text=info_text, font=("微软雅黑", 9), bg="white", fg="#999")
            info_label.pack(anchor="w", padx=15, pady=(0, 10))

        ttk.Separator(self.scrollable_frame, orient="horizontal").pack(fill="x", padx=10)

        for i, floor in enumerate(self.floor_list):
            is_op = (floor.get("speaker") == "楼主")
            floor_bg = "#f8fbff" if is_op else "white"
            f = tk.Frame(self.scrollable_frame, bg=floor_bg, pady=8, padx=10, highlightbackground="#e8e8e8", highlightthickness=1)
            f.pack(fill="x", padx=10, pady=(5, 0))

            speaker_name = floor['speaker']
            display_name = speaker_name
            if is_op:
                display_name = f"📌 {speaker_name}（楼主）"
            tk.Label(f, text=display_name, font=("微软雅黑", 11, "bold"), bg=floor_bg, fg="#28468c").pack(anchor="w")
            
            floor_time = floor.get('time', '刚刚')
            meta_text = f"🏠 第{i+1}楼  ⏱ {floor_time}  👍 {floor.get('likes', 0)}"
            meta_label = tk.Label(f, text=meta_text, font=("微软雅黑", 9), bg=floor_bg, fg="#aaa")
            meta_label.pack(anchor="w")

            content_label = tk.Label(f, text=floor["content"], font=("微软雅黑", 11), bg=floor_bg, wraplength=560, justify="left", fg="#333")
            content_label.pack(anchor="w", pady=(8, 0))

            action_frame = tk.Frame(f, bg=floor_bg)
            action_frame.pack(fill="x", pady=(8, 0))
            tk.Label(action_frame, text="💬 回复", font=("微软雅黑", 8), bg=floor_bg, fg="#999").pack(side="left", padx=(0, 15))
            tk.Label(action_frame, text="👍 点赞", font=("微软雅黑", 8), bg=floor_bg, fg="#999").pack(side="left", padx=(0, 15))
            tk.Label(action_frame, text="🚩 举报", font=("微软雅黑", 8), bg=floor_bg, fg="#999").pack(side="left")

            if i < len(self.floor_list) - 1:
                ttk.Separator(self.scrollable_frame, orient="horizontal").pack(fill="x", padx=10, pady=(5,0))

        bottom_spacer = tk.Frame(self.scrollable_frame, height=30, bg="white")
        bottom_spacer.pack(fill="x")

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
            self.scene_var.set(scene_name)
            self.on_scene_select()
            messagebox.showinfo("成功", f"场景 {scene_name} 已创建")
            dialog.destroy()

        tk.Button(dialog, text="保存", command=save, bg="#27ae60", fg="white").pack(pady=15)
        
    def new_character(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新建角色")
        dialog.geometry("350x450")

        tk.Label(dialog, text="角色ID（唯一标识）:").pack(pady=(10,0))
        id_entry = tk.Entry(dialog)
        id_entry.pack(fill="x", padx=10)

        tk.Label(dialog, text="显示昵称:").pack(pady=(10,0))
        name_entry = tk.Entry(dialog)
        name_entry.pack(fill="x", padx=10)

        tk.Label(dialog, text="人设描述（选填）:").pack(pady=(10,0))
        persona_entry = tk.Entry(dialog)
        persona_entry.pack(fill="x", padx=10)

        tk.Label(dialog, text="口头禅（选填）:").pack(pady=(10,0))
        catch_entry = tk.Entry(dialog)
        catch_entry.pack(fill="x", padx=10)

        tk.Label(dialog, text="选择头像:").pack(pady=(10,0))
        import os
        from config import AVATARS_DIR
        avatar_files = [f for f in os.listdir(AVATARS_DIR) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if not avatar_files:
            avatar_files = ["default.png"]
        avatar_var = tk.StringVar(value=avatar_files[0])
        avatar_combo = ttk.Combobox(dialog, textvariable=avatar_var, values=avatar_files, state="readonly")
        avatar_combo.pack(fill="x", padx=10, pady=(0,5))

        def upload_avatar():
            from tkinter import filedialog
            import shutil
            file_path = filedialog.askopenfilename(
                title="选择头像图片",
                filetypes=[("图片文件", "*.png *.jpg *.jpeg *.gif")]
            )
            if file_path:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(AVATARS_DIR, filename)
                shutil.copy(file_path, dest_path)
                new_avatar_files = [f for f in os.listdir(AVATARS_DIR) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                avatar_combo['values'] = new_avatar_files
                avatar_var.set(filename)
                messagebox.showinfo("成功", f"头像已上传: {filename}")
        
        upload_btn = tk.Button(dialog, text="上传自定义头像", command=upload_avatar)
        upload_btn.pack(pady=(5,0))

        tk.Label(dialog, text="默认情绪:").pack(pady=(10,0))
        emotion_combo = ttk.Combobox(dialog, values=["吃瓜","愤怒","温柔","吐槽","震惊","冷静","CP","梦女","心虚"], state="readonly")
        emotion_combo.current(0)
        emotion_combo.pack(fill="x", padx=10, pady=(0,10))

        save_btn = tk.Button(dialog, text="💾 保存角色", bg="#27ae60", fg="white", font=("", 12, "bold"),
                             command=lambda: save())
        save_btn.pack(pady=10, ipadx=20, ipady=5)

        def save():
            char_id = id_entry.get().strip()
            if not char_id:
                messagebox.showwarning("提示", "请输入角色ID")
                return
            chars = load_characters()
            if char_id in chars:
                messagebox.showwarning("提示", "角色ID已存在")
                return
            chars[char_id] = {
                "name": name_entry.get().strip() or char_id,
                "avatar": avatar_var.get(),
                "persona": persona_entry.get().strip(),
                "catchphrase": catch_entry.get().strip(),
                "default_emotion": emotion_combo.get(),
                "style": {"sentence_length":"中","aggressiveness":"中","humor":"中"}
            }
            save_characters(chars)
            self.characters = chars
            self.char_select_combo['values'] = list(chars.keys())
            self.char_select_var.set('')
            messagebox.showinfo("成功", f"角色 {char_id} 创建成功")
            dialog.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ForumGeneratorApp(root)
    root.mainloop()
