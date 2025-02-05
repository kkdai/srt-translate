import openai
import argparse
import os
import re
from langdetect import detect
from pathlib import Path

# 設定 OpenAI API 客戶端
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def is_timestamp(line):
    """檢查是否為時間戳的格式"""
    timestamp_pattern = r"^\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}$"
    return bool(re.match(timestamp_pattern, line.strip()))


def is_subtitle_number(line):
    """檢查是否為字幕序號"""
    return line.strip().isdigit()


def detect_language(text):
    """檢測文本語言，特別處理日文"""
    try:
        lang = detect(text)
        return "ja" if lang in ["ja", "ko"] else lang  # 有時日文會被誤認為韓文
    except:
        return "ja"  # 預設為日文


def translate_text(text, source_language):
    """翻譯文本到中文"""
    try:
        # 如果文本是空的，直接返回
        if not text.strip():
            return ""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"將以下日文文本翻譯成繁體中文。"
                        "請注意：\n"
                        "1. 保持人名、地名等專有名詞的原始寫法\n"
                        "2. 保持標點符號的格式\n"
                        "3. 維持原始文本的語氣和風格\n"
                        "4. 保留括號內的原文\n"
                        "5. 確保翻譯的完整性和連貫性"
                    ),
                },
                {"role": "user", "content": text},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"翻譯錯誤: {str(e)}")
        return text


def ensure_directory_exists(file_path):
    """確保目標檔案的目錄存在"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print(f"已創建目錄: {directory}")
        except Exception as e:
            print(f"創建目錄時發生錯誤: {str(e)}")
            raise


def translate_srt(input_file, output_file):
    """翻譯 SRT 文件"""
    # 檢查輸出檔案路徑
    output_path = Path(output_file)
    if output_path.exists():
        print(f"檔案 {output_file} 已存在，將覆蓋原有檔案")
    else:
        print(f"將建立新檔案: {output_file}")
        # 確保目標目錄存在
        ensure_directory_exists(output_file)

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            content = file.read()
    except UnicodeDecodeError:
        encodings = ["utf-8-sig", "cp1252", "shift-jis", "euc-jp"]
        for encoding in encodings:
            try:
                with open(input_file, "r", encoding=encoding) as file:
                    content = file.read()
                print(f"成功使用 {encoding} 編碼讀取文件")
                break
            except UnicodeDecodeError:
                continue

    # 分割成字幕區塊
    subtitle_blocks = re.split(r"\n\s*\n", content.strip())
    translated_blocks = []
    current_text = []

    for block in subtitle_blocks:
        lines = block.split("\n")
        current_block = []
        subtitle_text = []

        for line in lines:
            line = line.strip()
            if is_subtitle_number(line):
                current_block.append(line)
            elif is_timestamp(line):
                current_block.append(line)
            elif line:  # 只有非空行才加入翻譯
                subtitle_text.append(line)

        # 合併並翻譯字幕文本
        if subtitle_text:
            text_to_translate = " ".join(subtitle_text)
            translated_text = translate_text(text_to_translate, "ja")
            current_block.append(translated_text)

        if current_block:
            translated_blocks.append("\n".join(current_block))

    try:
        # 寫入翻譯結果
        with open(output_file, "w", encoding="utf-8") as file:
            file.write("\n\n".join(translated_blocks) + "\n")
        print(f"翻譯結果已成功寫入檔案: {output_file}")
    except Exception as e:
        print(f"寫入檔案時發生錯誤: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="將日文 SRT 字幕檔翻譯成中文")
    parser.add_argument("input_file", type=str, help="輸入的 SRT 檔案路徑")
    parser.add_argument("output_file", type=str, help="翻譯後的 SRT 檔案儲存路徑")

    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("未找到 OpenAI API 金鑰，請設定 OPENAI_API_KEY 環境變數")

    try:
        if not os.path.exists(args.input_file):
            raise FileNotFoundError(f"找不到輸入檔案: {args.input_file}")

        translate_srt(args.input_file, args.output_file)
        print(f"翻譯完成！翻譯後的檔案已儲存為：{args.output_file}")
    except Exception as e:
        print(f"程式執行時發生錯誤: {str(e)}")
        exit(1)
