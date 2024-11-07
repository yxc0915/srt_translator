import customtkinter as ctk

from core.page.home_page import HomePage
from core.page.settings_page import SettingsPage
from core.page.translator_page import TranslatorPage

class BaseApp:
    def __init__(self, master):
        # 设置主题和颜色
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # 主窗口设置
        self.master = master
        master.title("字幕翻译助手 v2.1")
        
        # 窗口大小和位置
        window_width = 900
        window_height = 700
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        master.minsize(800, 600)

        # DPI自适应缩放
        master.tk.call('tk', 'scaling', 1.5)

        # 创建导航栏
        self.create_navigation()

        # 创建页面容器
        self.page_frame = ctk.CTkFrame(master)
        self.page_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # 初始化页面
        self.pages = {
            "主页": HomePage(self.page_frame),
            "翻译": TranslatorPage(self.page_frame),
            "设置": SettingsPage(self.page_frame)
        }

        # 默认显示主页
        self.show_page("主页")

    def create_navigation(self):
        # 创建导航栏
        nav_frame = ctk.CTkFrame(self.master, height=50)
        nav_frame.pack(fill="x", padx=20, pady=(20, 0))

        # 为每个页面创建导航按钮
        for page_name in ["主页", "翻译", "设置"]:
            button = ctk.CTkButton(
                nav_frame, 
                text=page_name, 
                command=lambda name=page_name: self.show_page(name)
            )
            button.pack(side="left", padx=10)

    def show_page(self, page_name):
        # 隐藏所有页面
        for page in self.pages.values():
            page.pack_forget()
        
        # 显示选中的页面
        self.pages[page_name].pack(fill="both", expand=True)

def run_app():
    root = ctk.CTk()
    app = BaseApp(root)
    root.mainloop()
