import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yt_dlp
import shutil

class VideoDownloadPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # 设置项目根目录
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 设置下载和上传目录
        self.downloaded_video_dir = os.path.join(self.project_root, 'downloaded_video')
        self.uploaded_video_dir = os.path.join(self.project_root, 'uploaded_video')
        
        # 自动创建目录
        self.create_directories()

        # 页面标题
        title_label = ctk.CTkLabel(
            self, 
            text="视频管理", 
            font=("Microsoft YaHei", 20, "bold")
        )
        title_label.pack(pady=(20, 10))

        # YouTube 下载区域
        youtube_frame = ctk.CTkFrame(self)
        youtube_frame.pack(pady=10, padx=50, fill="x")

        # YouTube 链接输入
        ctk.CTkLabel(
            youtube_frame, 
            text="YouTube 视频链接:", 
            font=("Microsoft YaHei", 14)
        ).pack(side="left", padx=10)

        self.youtube_url_entry = ctk.CTkEntry(
            youtube_frame, 
            width=300
        )
        self.youtube_url_entry.pack(side="left", padx=10)

        # 下载按钮
        download_button = ctk.CTkButton(
            youtube_frame, 
            text="下载", 
            command=self.download_youtube_video,
            fg_color="#FF0000",  # YouTube 红色
            hover_color="#CC0000"
        )
        download_button.pack(side="left", padx=10)

        # 打开下载目录按钮
        open_download_dir_button = ctk.CTkButton(
            youtube_frame, 
            text="打开下载目录", 
            command=lambda: self.open_directory(self.downloaded_video_dir),
            fg_color="#1E90FF",
            hover_color="#4169E1"
        )
        open_download_dir_button.pack(side="left", padx=10)

        # 本地视频选择区域
        local_video_frame = ctk.CTkFrame(self)
        local_video_frame.pack(pady=10, padx=50, fill="x")

        # 本地视频选择按钮
        local_video_button = ctk.CTkButton(
            local_video_frame, 
            text="选择本地视频", 
            command=self.select_local_video,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        local_video_button.pack(side="left", padx=10)

        # 打开上传目录按钮
        open_upload_dir_button = ctk.CTkButton(
            local_video_frame, 
            text="打开上传目录", 
            command=lambda: self.open_directory(self.uploaded_video_dir),
            fg_color="#FFA500",
            hover_color="#FF8C00"
        )
        open_upload_dir_button.pack(side="left", padx=10)

        # 下载进度条
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

    def create_directories(self):
        """自动创建下载和上传目录"""
        try:
            os.makedirs(self.downloaded_video_dir, exist_ok=True)
            os.makedirs(self.uploaded_video_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("目录创建错误", f"无法创建目录：{str(e)}")

    def open_directory(self, directory):
        """打开指定目录"""
        try:
            os.startfile(directory)
        except Exception as e:
            messagebox.showerror("打开目录错误", f"无法打开目录：{str(e)}")

    def download_youtube_video(self):
        url = self.youtube_url_entry.get().strip()
        if not url:
            messagebox.showwarning("警告", "请输入YouTube视频链接")
            return

        # 重置进度和状态
        self.progress_bar.set(0)
        self.status_label.configure(text="正在准备下载...")

        # 多线程下载
        download_thread = threading.Thread(
            target=self._download_youtube_video, 
            args=(url,),
            daemon=True
        )
        download_thread.start()

    def _download_youtube_video(self, url):
        try:
            # YouTube-DL 配置
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': os.path.join(self.downloaded_video_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 获取视频信息
                info_dict = ydl.extract_info(url, download=True)
                video_title = info_dict.get('title', None)
                
                # 更新UI
                self.status_label.configure(
                    text=f"下载完成：{video_title}", 
                    text_color="green"
                )
                self.progress_bar.set(1)

                # 打开下载目录
                self.open_directory(self.downloaded_video_dir)

        except Exception as e:
            # 错误处理
            self.status_label.configure(
                text=f"下载失败：{str(e)}", 
                text_color="red"
            )
            self.progress_bar.set(0)
            messagebox.showerror("下载错误", str(e))

    def progress_hook(self, d):
        # 更新下载进度
        if d['status'] == 'downloading':
            p = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
            self.progress_bar.set(p / 100)
            self.status_label.configure(
                text=f"正在下载：{p:.2f}%", 
                text_color="blue"
            )
        elif d['status'] == 'finished':
            self.status_label.configure(
                text="下载完成", 
                text_color="green"
            )

    def select_local_video(self):
        # 选择本地视频文件
        filetypes = [
            ("Video Files", "*.mp4 *.avi *.mkv *.mov"),
            ("All Files", "*.*")
        ]
        video_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=filetypes
        )

        if video_path:
            # 复制文件到上传目录
            try:
                destination = os.path.join(self.uploaded_video_dir, os.path.basename(video_path))
                shutil.copy2(video_path, destination)
                messagebox.showinfo(
                    "视频选择", 
                    f"已复制视频到上传目录：\n{os.path.basename(video_path)}"
                )
                # 打开上传目录
                self.open_directory(self.uploaded_video_dir)
            except Exception as e:
                messagebox.showerror("错误", f"复制文件失败：{str(e)}")
