# 字幕翻译助手 (Srt Translator)

## 项目简介

这是一个基于 Python 的跨平台字幕翻译工具，支持多种 AI 翻译 API，提供简单易用的图形界面。
![2d96908fd590a718606775e2d8b92d33](https://github.com/user-attachments/assets/f8f86a6a-b269-43ea-8b11-fb47d022c499)


## 功能特点

- 支持多种字幕文件格式（.srt, .txt）
- 可配置多个 AI 翻译 API
- 灵活的语言选择
- 现代化的图形用户界面
- 配置文件热更新
- 多线程翻译处理

## 项目结构

```
subtitle_translator/
│
├── app.py                 # 程序入口
├── config.py              # 配置管理
├── requirements.txt       # 依赖文件
│
├── core/
│   ├── __init__.py
│   ├── file_handler.py    # 文件处理模块
│   ├── translator.py      # AI翻译模块
│   ├── prompts.py         # 提示词模块
│   ├── subtitle_translator.py # 字幕翻译模块
│   └── ui.py              # 用户界面模块
│
└── output/                # 翻译输出目录
```

### 文件详细说明

1. `app.py`
   - 程序主入口
   - 启动用户界面

2. `config.py`
   - 配置管理器
   - 处理 API 配置的加载、保存和管理
   - 支持动态添加和更新 API 配置

3. `core/file_handler.py`
   - 处理文件读取和保存
   - 支持多种编码检测
   - 提供文件转换和保存方法

4. `core/translator.py`
   - AI 翻译核心模块
   - 支持多种 API 接口
   - 处理翻译请求和响应

5. `core/prompts.py`
   - 管理翻译提示词
   - 提供针对不同语言和场景的翻译指令

6. `core/ui.py`
   - 图形用户界面
   - 提供文件选择、API 配置、翻译设置等功能

## 部署步骤

### 1. 环境准备

#### 推荐 Python 版本
- Python 3.12+

#### 克隆项目
```bash
git clone https://github.com/yxc0915/srt_translator.git
cd srt_translator
```

### 2. 创建虚拟环境（可选但推荐）

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置 API

首次运行会自动生成 `config.json`，你可以：
- 在界面中直接添加 API
- 手动编辑 `config.json`

#### API 配置示例
```json
{
    "apis": [
        {
            "name": "OpenAI",
            "base_url": "https://api.openai.com/v1",
            "api_type": "openai",
            "models": ["gpt-3.5-turbo", "gpt-4"]
        }
    ]
}
```

### 5. 运行程序

```bash
python app.py
```

## 使用说明

1. 点击"浏览文件"选择字幕文件
2. 选择源语言和目标语言
3. 选择 API 和模型
4. 输入 API Key
5. 点击"开始翻译"

## 注意事项

- 确保网络连接正常
- 检查 API Key 的有效性
- 大文件可能需要较长翻译时间

## 常见问题

### 1. 如何添加新的 API？
- 在界面右侧 "+" 按钮
- 填写 API 名称、基础 URL 等信息

### 2. 支持哪些语言？
- 目前支持：英语、中文、日语、韩语、西班牙语、法语
- 可在代码中轻松扩展

## 贡献和支持

- 欢迎提交 Issue 和 Pull Request
- 如遇到问题，请附带详细的错误信息

## 许可证

[LICENSE]
