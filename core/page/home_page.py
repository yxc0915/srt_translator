import customtkinter as ctk
import webbrowser

class HomePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # 标题
        title_label = ctk.CTkLabel(
            self, 
            text="字幕翻译助手", 
            font=("Microsoft YaHei", 24, "bold")
        )
        title_label.pack(pady=(20, 10))

        # 版本和简介
        version_label = ctk.CTkLabel(
            self, 
            text="Version 2.1 - 智能字幕翻译工具", 
            font=("Microsoft YaHei", 14)
        )
        version_label.pack(pady=(0, 20))

        # 功能介绍
        features_frame = ctk.CTkFrame(self)
        features_frame.pack(pady=20, padx=50, fill="x")

        features = [
            "✅ 支持多种语言字幕翻译",
            "✅ 智能AI翻译",
            "✅ 多API支持",
            "✅ 自定义专用词汇",
            "✅ 批量翻译"
        ]

        for feature in features:
            feature_label = ctk.CTkLabel(
                features_frame, 
                text=feature, 
                anchor="w", 
                font=("Microsoft YaHei", 12)
            )
            feature_label.pack(pady=5, fill="x")

        # 快速开始按钮
        start_button = ctk.CTkButton(
            self, 
            text="快速开始翻译", 
            command=self.goto_translator,
            fg_color="#4CAF50",
            hover_color="#45a049",
            font=("Microsoft YaHei", 14)
        )
        start_button.pack(pady=20)

        # 帮助链接
        help_frame = ctk.CTkFrame(self, fg_color="transparent")
        help_frame.pack(pady=20)

        github_link = ctk.CTkButton(
            help_frame, 
            text="GitHub项目", 
            command=self.open_github,
            fg_color="#333333",
            hover_color="#555555"
        )
        github_link.pack(side="left", padx=10)

        docs_link = ctk.CTkButton(
            help_frame, 
            text="使用文档", 
            command=self.open_docs,
            fg_color="#1E90FF",
            hover_color="#4169E1"
        )
        docs_link.pack(side="left", padx=10)



    def open_github(self):
        webbrowser.open("https://github.com/yxc0915/srt_translator")

    def open_docs(self):
        webbrowser.open("https://github.com/yxc0915/srt_translator/")
