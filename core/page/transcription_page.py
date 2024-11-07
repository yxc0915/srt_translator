import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import pandas as pd

# 导入你的转录模块
from sensevoice import transcribe

class TranscriptionPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # 设置项目根目录
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 设置视频和输出目录
        self.video_dir = os.path.join(self.project_root, 'uploaded_video')
        self.output_dir = os.path.join(self.project_root, 'transcription_output')
        
        # 自动创建目录
        self.create_directories()

        # 页面标题
        title_label = ctk.CTkLabel(
            self, 
            text="音频转录", 
            font=("Microsoft YaHei", 20, "bold")
        )
        title_label.pack(pady=(20, 10))

        # 视频选择区域
        video_frame = ctk.CTkFrame(self)
        video_frame.pack(pady=10, padx=50, fill="x")

        # 视频选择按钮
        select_video_button = ctk.CTkButton(
            video_frame, 
            text="选择视频", 
            command=self.select_video,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        select_video_button.pack(side="left", padx=10)

        # 显示选中的视频
        self.selected_video_label = ctk.CTkLabel(
            video_frame, 
            text="未选择视频",
            font=("Microsoft YaHei", 12)
        )
        self.selected_video_label.pack(side="left", padx=10)

        # 转录按钮
        transcribe_button = ctk.CTkButton(
            self, 
            text="开始转录", 
            command=self.start_transcription,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        transcribe_button.pack(pady=10)

        # 打开输出目录按钮
        open_output_button = ctk.CTkButton(
            self, 
            text="打开输出目录", 
            command=self.open_output_directory,
            fg_color="#FFA500",
            hover_color="#FF8C00"
        )
        open_output_button.pack(pady=10)

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        # 状态标签
        self.status_label = ctk.CTkLabel(
            self, 
            text="准备就绪", 
            font=("Microsoft YaHei", 12)
        )
        self.status_label.pack(pady=10)

        # 当前选中的视频文件
        self.current_video = None

    def create_directories(self):
        """自动创建视频和输出目录"""
        try:
            os.makedirs(self.video_dir, exist_ok=True)
            os.makedirs(self.output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("目录创建错误", f"无法创建目录：{str(e)}")

    def select_video(self):
        """选择视频文件"""
        filetypes = [
            ("Video Files", "*.mp4 *.avi *.mkv *.mov"),
            ("All Files", "*.*")
        ]
        video_path = filedialog.askopenfilename(
            title="选择视频文件",
            initialdir=self.video_dir,
            filetypes=filetypes
        )

        if video_path:
            self.current_video = video_path
            self.selected_video_label.configure(
                text=os.path.basename(video_path)
            )

    def start_transcription(self):
        """开始转录"""
        if not self.current_video:
            messagebox.showwarning("警告", "请先选择视频文件")
            return

        # 重置进度和状态
        self.progress_bar.set(0)
        self.status_label.configure(text="正在准备转录...")

        # 多线程转录
        transcription_thread = threading.Thread(
            target=self.run_transcription,
            daemon=True
        )
        transcription_thread.start()

    def run_transcription(self):
        """执行转录"""
        try:
            # 更新状态
            self.status_label.configure(
                text="正在转录...", 
                text_color="blue"
            )
            self.progress_bar.set(0.3)

            # 执行转录
            transcribe(self.current_video)

            # 更新状态
            self.status_label.configure(
                text="转录完成", 
                text_color="green"
            )
            self.progress_bar.set(1)

            # 打开输出目录
            self.open_output_directory()

        except Exception as e:
            # 错误处理
            self.status_label.configure(
                text=f"转录失败：{str(e)}", 
                text_color="red"
            )
            self.progress_bar.set(0)
            messagebox.showerror("转录错误", str(e))

    def open_output_directory(self):
        """打开输出目录"""
        try:
            os.startfile(self.output_dir)
        except Exception as e:
            messagebox.showerror("打开目录错误", f"无法打开目录：{str(e)}")
