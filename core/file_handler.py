import os
import json
import chardet
import tkinter as tk
from tkinter import filedialog

class FileHandler:
    @staticmethod
    def detect_encoding(file_path):
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            return result['encoding']

    @staticmethod
    def read_file(file_path):
        encoding = FileHandler.detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()

    @staticmethod
    def save_json(data, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def save_translated_file(content, original_path, target_lang):
        filename = os.path.splitext(original_path)[0]
        output_path = f"{filename}_translated_{target_lang}.srt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return output_path

    @staticmethod
    def select_files():
        root = tk.Tk()
        root.withdraw()
        file_paths = filedialog.askopenfilenames(
            title="选择字幕文件",
            filetypes=[("Subtitle Files", "*.srt *.txt")]
        )
        return list(file_paths)
