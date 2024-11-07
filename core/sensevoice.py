import warnings
warnings.filterwarnings("ignore")

import os
import sys
import torch
from typing import Dict
import librosa
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
import subprocess
import tempfile
import pandas as pd
import logging

# 导入 SenseVoice 相关库
from model import SenseVoiceSmall
from funasr.utils.postprocess_utils import rich_transcription_postprocess

# 添加项目根目录到系统路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# 导入其他自定义模块
from core.config_utils import load_key
from core.all_whisper_methods.demucs_vl import demucs_main
from core.all_whisper_methods.whisperXapi import (
    convert_video_to_audio, 
    split_audio, 
    save_results, 
    save_language
)
from core.all_whisper_methods.whisperXapi import (
    RAW_AUDIO_FILE, 
    BACKGROUND_AUDIO_FILE, 
    VOCAL_AUDIO_FILE, 
    AUDIO_DIR
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transcription.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 尝试从配置获取模型目录，如果失败则使用默认值
try:
    MODEL_DIR = load_key("model_dir")
except Exception as e:
    logger.warning(f"无法加载模型目录配置：{e}")
    MODEL_DIR = "iic/SenseVoiceSmall"

def transcribe_audio(
    audio_file: str, 
    start: float, 
    end: float, 
    language: str = "auto"
) -> Dict:
    """
    转录音频片段
    
    :param audio_file: 音频文件路径
    :param start: 开始时间
    :param end: 结束时间
    :param language: 语言，默认自动检测
    :return: 转录结果字典
    """
    try:
        # 选择设备
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"使用设备: {device}")

        # 加载 SenseVoice 模型
        m, kwargs = SenseVoiceSmall.from_pretrained(
            model=MODEL_DIR, 
            device=device
        )
        m.eval()

        # 使用上下文管理器创建临时音频文件
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
            temp_audio_path = temp_audio.name

        # 使用 ffmpeg 切割音频
        ffmpeg_cmd = (
            f'ffmpeg -y -i "{audio_file}" '
            f'-ss {start} -t {end-start} '
            '-vn -b:a 64k -ar 16000 -ac 1 '
            f'-metadata encoding=UTF-8 -f mp3 "{temp_audio_path}"'
        )
        
        subprocess.run(ffmpeg_cmd, shell=True, check=True, capture_output=True)

        # 使用进度条
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            transient=True
        ) as progress:
            task = progress.add_task("[cyan]转录中...", total=None)
            
            # 使用 SenseVoice 进行转录
            res = m.inference(
                data_in=temp_audio_path,
                language=language,
                use_itn=False,
                ban_emo_unk=False,
                **kwargs
            )
            progress.update(task, completed=True)

        # 删除临时文件
        os.unlink(temp_audio_path)

        # 处理转录结果
        processed_text = rich_transcription_postprocess(res[0][0]["text"])
        
        # 构造结果
        result = {
            'segments': [{
                'start': start,
                'end': end,
                'text': processed_text,
                'words': []  # SenseVoice 可能不提供逐词时间戳
            }]
        }

        return result

    except Exception as e:
        logger.error(f"音频转录错误: {e}")
        raise

def transcribe(
    video_file: str, 
    output_dir: str = "output", 
    language: str = "auto"
):
    """
    处理整个视频的转录
    
    :param video_file: 视频文件路径
    :param output_dir: 输出目录
    :param language: 语言，默认自动检测
    """
    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        log_dir = os.path.join(output_dir, "log")
        os.makedirs(log_dir, exist_ok=True)

        output_log = os.path.join(log_dir, "cleaned_chunks.xlsx")
        
        # 检查是否已存在转录结果
        if os.path.exists(output_log):
            rprint("[yellow]⚠️ 转录结果已存在，跳过转录步骤.[/yellow]")
            return
        
        # 视频转音频
        audio_file = convert_video_to_audio(video_file)

        # Demucs 人声分离
        vocal_audio_path = os.path.join(AUDIO_DIR, VOCAL_AUDIO_FILE)
        background_audio_path = os.path.join(AUDIO_DIR, BACKGROUND_AUDIO_FILE)
        
        if os.path.exists(background_audio_path):
            rprint(f"[yellow]⚠️ {background_audio_path} 已存在，跳过 Demucs 处理.[/yellow]")
        else:
            demucs_main(
                os.path.join(AUDIO_DIR, RAW_AUDIO_FILE),
                AUDIO_DIR,
                background_audio_path,
                vocal_audio_path
            )
            rprint("Demucs 处理完成，已保存人声和背景音频")
        
        # 使用人声音频
        audio_file = vocal_audio_path

        # 分割音频
        segments = split_audio(audio_file)
        
        # 转录音频
        all_results = []
        for start, end in segments:
            result = transcribe_audio(
                audio_file, 
                start, 
                end, 
                language=language
            )
            all_results.append(result)
        
        # 合并结果
        combined_result = {'segments': []}
        for result in all_results:
            combined_result['segments'].extend(result['segments'])
        
        # 创建 DataFrame
        df = pd.DataFrame([
            {
                'start': segment['start'], 
                'end': segment['end'], 
                'text': segment['text']
            } for segment in combined_result['segments']
        ])
        
        # 保存结果
        save_results(df, output_dir=output_dir)
        
        rprint("[green]✅ 转录完成[/green]")

    except Exception as e:
        logger.error(f"视频转录处理错误: {e}")
        rprint(f"[red]❌ 转录失败: {e}[/red]")
        raise

def find_video_files(directory=None):
    """
    查找视频文件
    
    :param directory: 搜索目录，默认为当前目录
    :return: 找到的第一个视频文件路径
    """
    if directory is None:
        directory = os.getcwd()
    
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov']
    
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                return os.path.join(root, file)
    
    raise FileNotFoundError("未找到视频文件")

if __name__ == "__main__":
    try:
        video_file = find_video_files()
        rprint(f"[green]📁 找到视频文件:[/green] {video_file}, [green]开始转录...[/green]")
        transcribe(video_file)
    except Exception as e:
        rprint(f"[red]❌ 处理失败: {e}[/red]")
