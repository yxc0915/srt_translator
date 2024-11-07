import os
import re
import time
import random
import traceback
import concurrent.futures
from typing import List, Tuple, Optional

import tiktoken

class Subtitle:
    def __init__(self, index, timestamp_in, timestamp_out, text):
        self.index = index
        self.timestamp_in = timestamp_in
        self.timestamp_out = timestamp_out
        self.text = text

class SmartSubtitleTranslator:
    def __init__(self, translator, max_workers=5, max_tokens=2000, 
                 max_retries=3, retry_delay_base=1, custom_vocab=None):
        self.translator = translator
        self.max_workers = max_workers
        self.max_tokens = max_tokens
        self.max_retries = max_retries  # 最大重试次数
        self.retry_delay_base = retry_delay_base  # 基础重试延迟
        self.context_summary = None
        self.target_language = None
        self.source_language = None
        self.custom_vocab = custom_vocab or []  # 新增自定义词汇属性

    def count_tokens(self, text):
        try:
            tokenizer = tiktoken.get_encoding("cl100k_base")
            return len(tokenizer.encode(text))
        except ImportError:
            return len(text.split())

    def parse_subtitles(self, content):
        """解析SRT文件"""
        # 处理不同的换行符和编码问题
        content = content.replace('\r\n', '\n')
        
        pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)'
        matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
        
        subtitles = []
        for match in matches:
            index, timestamp_in, timestamp_out, text = match
            subtitles.append(Subtitle(
                index=index, 
                timestamp_in=timestamp_in, 
                timestamp_out=timestamp_out, 
                text=text.strip()
            ))
        
        return subtitles

    def analyze_content(self, full_text):
        """第一阶段：分析整体内容，生成上下文摘要"""
        # 如果文本太短，直接返回None
        if len(full_text.strip()) < 50:
            print("文本内容过短，无法进行分析")
            return None
    
        # 准备专用词汇部分
        vocab_section = "\n专用词汇列表（如有）：\n" + "\n".join(self.custom_vocab) if self.custom_vocab else ""
    
        analysis_prompt = f"""
        请以专业的角度分析以下字幕文本的整体内容，并提供详细且精准的分析报告：
    
        1. 内容类型（如：电视剧、纪录片、访谈、教育视频等）
        2. 主要主题和核心情节
        3. 关键人物或角色特点
        4. 特定的地点或场景，固定翻译（同时列出英文原文和译文）
        5. 特定的专有名词，方便后续固定翻译（同时列出英文原文和译文）
        6. 语言风格和语气特点
        7. 可能的目标受众
    
        {vocab_section}
    
        请用简洁、专业的语言总结这些信息，为后续翻译提供指导。
    
        文本内容（前2500字）：
        {full_text[:2500]}
        """
        
        try:
            context_summary = self.translator.translate(
                text=full_text[:2500],  # 只分析前2500字
                system_prompt=analysis_prompt,
                temperature=0.3
            )
            
            # 检查返回内容是否为空
            if not context_summary or context_summary.strip() == '':
                print("内容分析返回为空")
                return None
        
        return context_summary
    except Exception as e:
        print(f"内容分析失败: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None


    def translate_with_context(self, subtitles):
        """第二阶段：基于上下文进行批量翻译"""
        if not self.context_summary:
            print("警告：未进行内容分析，将使用默认翻译")
            self.context_summary = f"这是一个需要翻译的字幕文件。请保持原文的语气和风格。"
    
        # 创建一个用于存储已翻译结果的共享列表
        translated_texts = [None] * len(subtitles)
    
        def safe_translate_subtitle(subtitle, context_summary, subtitles, translated_texts):
            """
            安全的字幕翻译方法，支持部分并发翻译
            
            :param subtitle: 当前字幕对象
            :param context_summary: 上下文摘要
            :param subtitles: 所有字幕列表
            :param translated_texts: 共享的翻译结果列表
            :return: 翻译结果或错误信息
            """
            current_index = subtitles.index(subtitle)
            
            # 获取已翻译的前文（如果有）
            prev_context = []
            for i in range(max(0, current_index-10), current_index):
                if translated_texts[i] is not None:
                    prev_context.append(translated_texts[i])
                else:
                    prev_context.append(subtitles[i].text)
            
            # 获取未翻译的后文
            next_context = subtitles[current_index+1:min(len(subtitles), current_index+11)]
            next_text = "\n".join([s.text for s in next_context])
            
            max_retries = 3
            for retry in range(max_retries):
                try:
                    # 构建翻译提示
                    translation_prompt = f"""
                    你是一个专业的字幕翻译专家。以下是关于这个视频/内容的背景信息：
    
                    {context_summary}

                    专用词汇列表（请在翻译时特别注意）：
                    {"\n".join(self.custom_vocab) if self.custom_vocab else "无特殊词汇"}
    
                    翻译要求：
                    1. 仅翻译"待翻译文本"部分
                    2. 保持原文的语气和风格
                    3. 确保翻译自然流畅
                    4. 严格只返回翻译结果，不要添加任何其他内容
                    5. 我会为你在待翻译文本前后提供它的上下文，请你不要翻译它们
                    6. 程序会默认第一行为翻译结果，并自动截取第一行
    
                    已翻译上文（前10句）：
                    {"\n".join(prev_context)}
    
                    待翻译文本：{subtitle.text}
    
                    未翻译下文（后10句）：
                    {next_text}
    
                    请只返回待翻译文本的翻译结果。
                    """
                    
                    # 尝试翻译
                    translated_text = self.translator.translate(
                        text=subtitle.text,
                        system_prompt=translation_prompt,
                        temperature=0.7
                    )
                    
                    # 检查翻译结果
                    if not translated_text or translated_text.strip() == '':
                        raise ValueError("翻译结果为空")
                    
                    # 移除可能的额外描述
                    translated_text = translated_text.strip().split('\n')[0].strip()
                    
                    return translated_text
                
                except Exception as e:
                    # 记录错误
                    print(f"翻译字幕 {subtitle.index} 失败（第 {retry + 1} 次尝试）: {e}")
                    
                    # 最后一次重试仍失败
                    if retry == max_retries - 1:
                        # 根据错误类型选择不同的处理方式
                        if isinstance(e, ValueError):
                            # 如果是值错误（如空结果），返回原文并附加错误标记
                            return f"[翻译失败] {subtitle.text}"
                        else:
                            # 对于其他类型错误，返回原文并附加详细错误信息
                            return f"[翻译错误：{str(e)}] {subtitle.text}"
                    
                    # 重试间隔（指数退避）
                    time.sleep(2 ** retry)
            
            # 理论上不会执行到这里，但保险起见
            return f"[翻译失败] {subtitle.text}"
    
        # 使用线程池进行并发翻译
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 准备翻译任务
            translation_futures = [
                executor.submit(
                    safe_translate_subtitle, 
                    subtitle, 
                    self.context_summary, 
                    subtitles, 
                    translated_texts
                ) for subtitle in subtitles
            ]
            
            # 收集翻译结果
            for future in concurrent.futures.as_completed(translation_futures):
                try:
                    index = translation_futures.index(future)
                    translated_text = future.result()
                    translated_texts[index] = translated_text
                except Exception as e:
                    print(f"处理字幕翻译任务时发生异常: {e}")
                    # 如果任务本身抛出异常，返回原文
                    translated_texts[index] = "[处理失败]"
            
            return translated_texts

    def process_subtitle_file(self, file_path, target_language) -> Tuple[str, str]:
        """完整的字幕处理流程，增加全面的错误处理"""
        try:
            # 读取字幕文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析字幕
            subtitles = self.parse_subtitles(content)
            
            # 检查是否有可翻译的字幕
            if not subtitles:
                raise ValueError(f"文件 {file_path} 中没有可翻译的字幕")
            
            # 提取纯文本用于分析
            full_text = "\n".join([sub.text for sub in subtitles])
            
            # 设置目标语言
            self.target_language = target_language
            
            # 第一阶段：分析内容
            print("正在分析内容...")
            context_summary = self.analyze_content(full_text)
            
            # 如果内容分析失败，使用默认提示词
            if not context_summary:
                context_summary = f"这是一个需要翻译的字幕文件。请保持原文的语气和风格。"
            
            print(f"内容分析完成: \n{context_summary}\n")
            
            # 将上下文摘要保存为实例变量
            self.context_summary = context_summary
            
            # 第二阶段：翻译字幕
            print("开始并发翻译...")
            translated_texts = self.translate_with_context(subtitles)
            
            # 检查翻译结果
            if len(translated_texts) != len(subtitles):
                print(f"警告：翻译结果数量({len(translated_texts)})与原字幕数量({len(subtitles)})不符")
            
            # 重建字幕文件
            output_content = self.rebuild_subtitles(subtitles, translated_texts)
            
            # 保存翻译结果
            output_path = self._generate_output_path(file_path, target_language)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            
            # 保存分析报告
            analysis_path = self._generate_analysis_path(file_path)
            with open(analysis_path, 'w', encoding='utf-8') as f:
                f.write(f"内容分析报告:\n{context_summary}")
            
            # 检查是否有翻译失败的字幕
            failed_subtitles = [
                text for text in translated_texts 
                if text.startswith("[翻译失败]") or text.startswith("[翻译错误")
            ]
            
            if failed_subtitles:
                print(f"警告：{len(failed_subtitles)} 个字幕翻译失败")
            
            return output_path, analysis_path
        
        except Exception as e:
            print(f"处理字幕文件 {file_path} 时发生错误: {e}")
            raise

    def rebuild_subtitles(self, original_subtitles, translated_texts):
        """重建SRT文件"""
        rebuilt_content = []
        for (subtitle, translated_text) in zip(original_subtitles, translated_texts):
            subtitle_block = f"{subtitle.index}\n{subtitle.timestamp_in} --> {subtitle.timestamp_out}\n{translated_text}\n\n"
            rebuilt_content.append(subtitle_block)
        
        return "".join(rebuilt_content)

    def _generate_output_path(self, input_path, target_language):
        """生成输出文件路径"""
        base, ext = os.path.splitext(input_path)
        return f"{base}_translated_{target_language}{ext}"

    def _generate_analysis_path(self, input_path):
        """生成分析报告文件路径"""
        base, ext = os.path.splitext(input_path)
        return f"{base}_analysis.txt"
