import requests
import json
import tiktoken
import traceback

class Translator:
    def __init__(self, config):
        self.config = config
        self.base_url = config.get('base_url')
        self.api_key = config.get('api_key')
        self.api_type = config.get('api_type', 'openai')
        self.model = config.get('model', 'gpt-3.5-turbo')
        
        # 初始化分词器
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            print("Warning: tiktoken not installed. Token counting disabled.")
            self.tokenizer = None

    def count_tokens(self, text):
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        return len(text.split())  # 简单的备选方案

    def translate(self, text, source_lang=None, target_lang=None, system_prompt=None, temperature=0.7):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 如果文本为空，直接返回
        if not text or text.strip() == '':
            return ''

        # 构建消息列表
        messages = []
        
        # 添加系统提示词
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 添加用户消息
        messages.append({"role": "user", "content": text})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions", 
                headers=headers, 
                json=payload
            )
            
            # 打印完整的响应内容，帮助诊断问题
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
            
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            translated_text = result['choices'][0]['message']['content'].strip()
            
            return translated_text
        
        except requests.RequestException as e:
            print(f"Translation error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            print(f"Response content: {e.response.text if hasattr(e, 'response') else 'No response'}")
            raise
        except json.JSONDecodeError as e:
            print(f"JSON Decode error: {e}")
            print(f"Response content: {response.text}")
            raise
