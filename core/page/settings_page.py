import customtkinter as ctk
from tkinter import messagebox
from config import config_manager

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # 页面标题
        title_label = ctk.CTkLabel(
            self, 
            text="系统设置", 
            font=("Microsoft YaHei", 20, "bold")
        )
        title_label.pack(pady=(20, 10))

        # 主题设置
        theme_frame = ctk.CTkFrame(self)
        theme_frame.pack(pady=10, padx=50, fill="x")

        ctk.CTkLabel(
            theme_frame, 
            text="界面主题:", 
            font=("Microsoft YaHei", 14)
        ).pack(side="left", padx=10)

        self.theme_select = ctk.CTkComboBox(
            theme_frame, 
            values=["浅色", "深色", "系统默认"],
            width=200,
            command=self.change_theme
        )
        self.theme_select.pack(side="left", padx=10)
        self.theme_select.set("系统默认")

        # API管理
        api_frame = ctk.CTkFrame(self)
        api_frame.pack(pady=10, padx=50, fill="x")

        ctk.CTkLabel(
            api_frame, 
            text="API管理:", 
            font=("Microsoft YaHei", 14)
        ).pack(side="left", padx=10)

        add_api_button = ctk.CTkButton(
            api_frame, 
            text="添加新API", 
            command=self.show_add_api_dialog,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        add_api_button.pack(side="left", padx=10)

        # 已添加API列表
        api_list_frame = ctk.CTkFrame(self)
        api_list_frame.pack(pady=10, padx=50, fill="both", expand=True)

        ctk.CTkLabel(
            api_list_frame, 
            text="已添加API:", 
            font=("Microsoft YaHei", 14)
        ).pack(anchor="w", padx=10)

        self.api_listbox = ctk.CTkTextbox(
            api_list_frame, 
            height=200
        )
        self.api_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_api_list()

    def change_theme(self, theme):
        theme_map = {
            "浅色": "light",
            "深色": "dark",
            "系统默认": "system"
        }
        ctk.set_appearance_mode(theme_map[theme])

    def show_add_api_dialog(self):
        """显示添加API对话框"""
        dialog = ctk.CTkToplevel(self)
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
    
                # 检查必填项
                if not name or not url or not api_type:
                    messagebox.showerror("错误", "请填写所有必要信息")
                    return
    
                config_manager.add_api(name, url, api_type, models)
                
                # 刷新API列表
                self.refresh_api_list()
                
                dialog.destroy()
                messagebox.showinfo("成功", f"成功添加API: {name}")
            except Exception as e:
                messagebox.showerror("错误", str(e))
    
        # 保存按钮
        save_button = ctk.CTkButton(
            dialog, 
            text="保存", 
            command=save_api,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        save_button.pack(pady=10)
    
        # 添加一些额外的提示
        tip_label = ctk.CTkLabel(
            dialog, 
            text="提示：\n1. API名称需唯一\n2. 基础URL为API服务地址\n3. 模型间用逗号分隔",
            text_color="gray",
            wraplength=350
        )
        tip_label.pack(pady=5)


    def refresh_api_list(self):
        apis = config_manager.get_apis()
        self.api_listbox.delete("1.0", ctk.END)
        for api in apis:
            self.api_listbox.insert(ctk.END, 
                f"名称: {api['name']}\n"
                f"类型: {api['api_type']}\n"
                f"地址: {api['base_url']}\n"
                f"模型: {', '.join(api.get('models', []))}\n\n"
            )
        self.api_listbox.configure(state="disabled")
