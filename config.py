import os
import json
import hashlib
from typing import List, Dict, Any

class ConfigManager:
    DEFAULT_CONFIG_PATH = 'config.json'
    
    def __init__(self, config_path=None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        # 默认配置
        default_config = {
            "apis": [
                {
                    "name": "OpenAI",
                    "base_url": "https://api.openai.com/v1",
                    "api_type": "openai",
                    "models": ["gpt-3.5-turbo", "gpt-4"]
                },
                {
                    "name": "Azure OpenAI",
                    "base_url": "https://your-azure-endpoint.openai.azure.com/",
                    "api_type": "azure",
                    "models": ["gpt-3.5-turbo", "gpt-4"]
                }
            ],
            "default_settings": {
                "source_lang": "English",
                "target_lang": "Chinese",
                "max_tokens": 4096
            }
        }

        # 如果配置文件不存在，创建它
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            return default_config

        # 读取现有配置
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                
            # 合并默认配置和用户配置
            for key in default_config:
                if key not in user_config:
                    user_config[key] = default_config[key]
            
            return user_config
        except json.JSONDecodeError:
            return default_config

    def save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def add_api(self, name: str, base_url: str, api_type: str, models: List[str]):
        # 生成唯一ID
        api_id = hashlib.md5(f"{name}{base_url}".encode()).hexdigest()[:8]
        
        new_api = {
            "id": api_id,
            "name": name,
            "base_url": base_url,
            "api_type": api_type,
            "models": models
        }
        
        # 检查是否已存在
        for api in self.config['apis']:
            if api['name'] == name:
                raise ValueError(f"API {name} 已存在")
        
        self.config['apis'].append(new_api)
        self.save_config()
        return api_id

    def remove_api(self, name: str):
        self.config['apis'] = [
            api for api in self.config['apis'] 
            if api['name'] != name
        ]
        self.save_config()

    def get_apis(self) -> List[Dict[str, Any]]:
        return self.config['apis']

    def get_models(self, api_name: str) -> List[str]:
        for api in self.config['apis']:
            if api['name'] == api_name:
                return api['models']
        return []

# 全局配置管理器
config_manager = ConfigManager()
