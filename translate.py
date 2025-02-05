import openai
import argparse
import os
import re
from langdetect import detect

# 設定 OpenAI API 金鑰
openai.api_key = os.getenv("OPENAI_API_KEY")


def is_timestamp(line):
    """檢查是否為時間戳的格式"""
    timestamp_pattern = r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$"
    return bool(re.match(timestamp_pattern, line.strip()))


def is_subtitle_number(line):
    """檢查是否為字幕序號"""
    return line.strip().isdigit()


def detect_language(text):
    """檢測文本語言"""
    try:
        return detect(text)
    except:
        return "en"  # 預設為英文


def translate_text(text, source_language):
    """翻譯文本到中文"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # 使用最新的模型
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"將以下文本從{source_language}翻譯成繁體中文。"
                        "請注意：\n"
                        "1. 保持專有名詞的原始英文\n"
                        "2. 保持標點符號的格式\n"
                        "3. 維持原始文本的語氣和風格\n"
                        "4. 不要翻譯括號內的技術註解或標記"
                    ),
                },
                {"role": "user", "content": text},
            ],
            temperature=0.3,  # 降低創意度以獲得更準確的翻譯
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"翻譯錯誤: {str(e)}")
        return text  # 如果翻譯失敗，返回原始文本


def translate_srt(input_file, output_file):
    """翻譯 SRT 文件"""
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        # 如果 UTF-8 讀取失敗，嘗試其他編碼
        encodings = ["cp1252", "shift-jis", "euc-jp", "big5"]
        for encoding in encodings:
            try:
                with open(input_file, "r", encoding=encoding) as file:
                    lines = file.readlines()
                break
            except UnicodeDecodeError:
                continue

    translated_lines = []
    current_text = []
    source_language = None

    for line in lines:
        line = line.strip()

        if not line:
            # 處理累積的文本
            if current_text:
                text_to_translate = " ".join(current_text)
                if not source_language:
                    source_language = detect_language(text_to_translate)
                translated_text = translate_text(text_to_translate, source_language)
                translated_lines.extend([translated_text, "", ""])
                current_text = []
            else:
                translated_lines.append("")
        elif is_subtitle_number(line):
            # 保留字幕序號
            translated_lines.append(line)
        elif is_timestamp(line):
            # 保留時間戳
            translated_lines.append(line)
        else:
            current_text.append(line)

    # 處理最後一段文本
    if current_text:
        text_to_translate = " ".join(current_text)
        translated_text = translate_text(text_to_translate, source_language)
        translated_lines.extend([translated_text, ""])

    # 寫入翻譯結果
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(translated_lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="將 SRT 字幕檔翻譯成中文")
    parser.add_argument("input_file", type=str, help="輸入的 SRT 檔案路徑")
    parser.add_argument("output_file", type=str, help="翻譯後的 SRT 檔案儲存路徑")

    args = parser.parse_args()

    if not openai.api_key:
        raise ValueError("未找到 OpenAI API 金鑰，請設定 OPENAI_API_KEY 環境變數")

    translate_srt(args.input_file, args.output_file)
    print(f"翻譯完成！翻譯後的檔案已儲存為：{args.output_file}")
