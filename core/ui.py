import os
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import traceback

import customtkinter as ctk

from config import config_manager
from core.file_handler import FileHandler
from core.translator import Translator
from core.subtitle_translator import SmartSubtitleTranslator

class TranslatorApp:
    def __init__(self, master):
        # 设置主题和颜色
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # 主窗口设置
        self.master = master
        master.title("字幕翻译助手 v2.0")
        
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

        # 创建主框架
        self.main_frame = ctk.CTkFrame(master)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # 创建文件选择区域
        self.create_file_section()

        # 创建语言选择区域
        self.create_language_section()

        # 创建API配置区域
        self.create_api_section()

        # 创建翻译设置区域
        self.create_translation_settings()

        # 创建翻译按钮
        self.create_translate_button()

        # 创建进度和状态区域
        self.create_progress_section()

        # 初始化文件路径列表
        self.file_paths = []

    def create_file_section(self):
        # 文件选择框架
        file_frame = ctk.CTkFrame(self.main_frame)
        file_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(file_frame, text="选择字幕文件:").pack(side="left", padx=10)

        select_button = ctk.CTkButton(
            file_frame, 
            text="浏览文件", 
            command=self.select_files,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        select_button.pack(side="left", padx=10)

        # 文件列表
        self.file_listbox = tk.Listbox(
            self.main_frame, 
            selectmode=tk.MULTIPLE, 
            height=10
        )
        self.file_listbox.pack(padx=10, pady=10, fill="both", expand=True)

    def create_language_section(self):
        lang_frame = ctk.CTkFrame(self.main_frame)
        lang_frame.pack(padx=10, pady=10, fill="x")

        languages = ["English", "Chinese", "Japanese", "Korean", "Spanish", "French"]

        # 源语言
        ctk.CTkLabel(lang_frame, text="源语言:").pack(side="left", padx=5)
        self.source_lang = ctk.CTkComboBox(
            lang_frame, 
            values=languages,
            width=150
        )
        self.source_lang.pack(side="left", padx=5)
        self.source_lang.set("English")

        # 目标语言
        ctk.CTkLabel(lang_frame, text="目标语言:").pack(side="left", padx=5)
        self.target_lang = ctk.CTkComboBox(
            lang_frame, 
            values=languages,
            width=150
        )
        self.target_lang.pack(side="left", padx=5)
        self.target_lang.set("Chinese")

    def create_api_section(self):
        api_frame = ctk.CTkFrame(self.main_frame)
        api_frame.pack(padx=10, pady=10, fill="x")

        # API选择
        ctk.CTkLabel(api_frame, text="API选择:").pack(side="left", padx=5)
        self.api_select = ctk.CTkComboBox(
            api_frame, 
            values=[api['name'] for api in config_manager.get_apis()],
            width=200,
            command=self.update_models
        )
        self.api_select.pack(side="left", padx=5)
        self.api_select.set(config_manager.get_apis()[0]['name'])

        # 模型选择
        ctk.CTkLabel(api_frame, text="模型:").pack(side="left", padx=5)
        self.model_select = ctk.CTkComboBox(
            api_frame, 
            width=150
        )
        self.model_select.pack(side="left", padx=5)

        # API Key
        ctk.CTkLabel(api_frame, text="API Key:").pack(side="left", padx=5)
        self.api_key_entry = ctk.CTkEntry(
            api_frame, 
            show="*", 
            width=250
        )
        self.api_key_entry.pack(side="left", padx=5)

        # 添加API按钮
        add_api_button = ctk.CTkButton(
            api_frame, 
            text="+", 
            width=30,
            command=self.show_add_api_dialog
        )
        add_api_button.pack(side="left", padx=5)

        # 初始化模型
        self.update_models(self.api_select.get())

    def create_translation_settings(self):
        settings_frame = ctk.CTkFrame(self.main_frame)
        settings_frame.pack(padx=10, pady=10, fill="x")

        # 并发数设置
        ctk.CTkLabel(settings_frame, text="并发数:").pack(side="left", padx=5)
        self.concurrent_workers = ctk.CTkEntry(settings_frame, width=100)
        self.concurrent_workers.pack(side="left", padx=5)
        self.concurrent_workers.insert(0, "5")

        # 温度设置
        ctk.CTkLabel(settings_frame, text="温度:").pack(side="left", padx=5)
        self.temperature = ctk.CTkEntry(settings_frame, width=100)
        self.temperature.pack(side="left", padx=5)
        self.temperature.insert(0, "0.7")

    def create_translate_button(self):
        self.translate_button = ctk.CTkButton(
            self.main_frame, 
            text="开始翻译", 
            command=self.start_translation,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        self.translate_button.pack(padx=10, pady=10)

    def create_progress_section(self):
        # 进度条
        self.progress = ctk.CTkProgressBar(self.main_frame)
        self.progress.pack(padx=10, pady=10, fill="x")
        self.progress.set(0)

        # 状态标签
        self.status_label = ctk.CTkLabel(
            self.main_frame, 
            text="准备就绪", 
            text_color="green"
        )
        self.status_label.pack(padx=10, pady=10)

    def update_models(self, api_name):
        """更新模型下拉框"""
        models = config_manager.get_models(api_name)
        self.model_select.configure(values=models)
        if models:
            self.model_select.set(models[0])

    def select_files(self):
        """选择字幕文件"""
        filetypes = [("Subtitle Files", "*.srt *.txt")]
        files = filedialog.askopenfilenames(filetypes=filetypes)
        
        # 清空之前的列表
        self.file_listbox.delete(0, tk.END)
        self.file_paths.clear()
        
        # 添加新选择的文件
        for file in files:
            self.file_listbox.insert(tk.END, os.path.basename(file))
            self.file_paths.append(file)

    def show_add_api_dialog(self):
        """显示添加API对话框"""
        dialog = ctk.CTkToplevel(self.master)
        dialog.title("添加新API")
        dialog.geometry("400x500")

        # API名称
        ctk.CTkLabel(dialog, text="API名称:").pack(pady=5)
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.pack(pady=5)

        # 基础URL
        ctk.CTkLabel(dialog, text="基础URL:").pack(pady=5)
        url_entry = ctk.CTkEntry(dialog, width=300)
        url_entry.pack(pady=5)

        # API类型
        ctk.CTkLabel(dialog, text="API类型:").pack(pady=5)
        api_type_select = ctk.CTkComboBox(
            dialog, 
            values=["openai", "azure", "custom"],
            width=300
        )
        api_type_select.pack(pady=5)

        # 模型列表
        ctk.CTkLabel(dialog, text="模型(逗号分隔):").pack(pady=5)
        models_entry = ctk.CTkEntry(dialog, width=300)
        models_entry.pack(pady=5)

        def save_api():
            try:
                name = name_entry.get()
                url = url_entry.get()
                api_type = api_type_select.get()
                models = [m.strip() for m in models_entry.get().split(',')]

                config_manager.add_api(name, url, api_type, models)
                
                # 更新API选择下拉框
                apis = [api['name'] for api in config_manager.get_apis()]
                self.api_select.configure(values=apis)
                
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", str(e))

        save_button = ctk.CTkButton(dialog, text="保存", command=save_api)
        save_button.pack(pady=10)

    def start_translation(self):
        """开始翻译过程"""
        # 检查是否选择了文件
        if not self.file_paths:
            messagebox.showwarning("警告", "请先选择字幕文件")
            return

        # 检查API Key
        api_key = self.api_key_entry.get()
        if not api_key:
            messagebox.showwarning("警告", "请输入API Key")
            return

        # 多线程执行翻译
        translation_thread = threading.Thread(
            target=self.run_translation, 
            daemon=True
        )
        translation_thread.start()

    def run_translation(self):
        """翻译执行逻辑"""
        try:
            # 获取选择的API配置
            api_name = self.api_select.get()
            api_config = next(
                (api for api in config_manager.get_apis() if api['name'] == api_name), 
                None
            )
            
            if not api_config:
                raise ValueError("未找到选定的API配置")

            # 准备翻译配置
            translator_config = {
                'base_url': api_config['base_url'],
                'api_key': self.api_key_entry.get(),
                'api_type': api_config['api_type'],
                'model': self.model_select.get()
            }

            # 创建翻译器
            translator = Translator(translator_config)
            
            # 获取并发数和温度
            try:
                max_workers = int(self.concurrent_workers.get())
                temperature = float(self.temperature.get())
            except ValueError:
                messagebox.showwarning("警告", "并发数和温度必须是数字")
                return

            # 创建字幕翻译器
            subtitle_translator = SmartSubtitleTranslator(
                translator=translator, 
                max_workers=max_workers
            )

            # 准备处理文件
            total_files = len(self.file_paths)
            analysis_reports = []

            # 遍历文件并翻译
            for index, file_path in enumerate(self.file_paths, 1):
                try:
                    # 更新进度
                    self.progress.set(index / total_files)
                    self.status_label.configure(text=f"正在处理 {os.path.basename(file_path)}")

                    # 处理字幕
                    output_path, analysis_path = subtitle_translator.process_subtitle_file(
                        file_path,
                        self.target_lang.get()
                    )
                    
                    # 收集分析报告
                    with open(analysis_path, 'r', encoding='utf-8') as f:
                        analysis_reports.append({
                            'file': os.path.basename(file_path),
                            'report': f.read()
                        })

                except Exception as e:
                    print(f"处理 {file_path} 时出错: {e}")
                    traceback.print_exc()
                    messagebox.showwarning("警告", f"处理 {os.path.basename(file_path)} 时出错: {e}")

            # 完成处理
            self.progress.set(1)
            self.status_label.configure(text="翻译完成", text_color="green")
            
            # 显示分析报告
            self.show_analysis_reports(analysis_reports)

        except Exception as e:
            self.progress.set(0)
            self.status_label.configure(text="翻译失败", text_color="red")
            messagebox.showerror("错误", str(e))
            traceback.print_exc()

    def show_analysis_reports(self, reports):
        """显示多个文件的分析报告"""
        dialog = ctk.CTkToplevel(self.master)
        dialog.title("内容分析报告")
        dialog.geometry("800x600")

        # 创建笔记本（选项卡）控件
        notebook = ctk.CTkTabview(dialog)
        notebook.pack(padx=10, pady=10, fill="both", expand=True)

        # 为每个文件创建一个选项卡
        for report in reports:
            tab = notebook.add(report['file'])
            text_widget = ctk.CTkTextbox(tab, width=760, height=500)
            text_widget.pack(padx=10, pady=10)
            text_widget.insert('1.0', report['report'])
            text_widget.configure(state='disabled')

        # 关闭按钮
        close_button = ctk.CTkButton(
            dialog, 
            text="关闭", 
            command=dialog.destroy
        )
        close_button.pack(pady=10)

def run_app():
    root = ctk.CTk()
    app = TranslatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()
