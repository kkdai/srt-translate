import openai
import argparse
import os
import re
from langdetect import detect
from pathlib import Path
from tqdm import tqdm

# 設定 OpenAI API 客戶端
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def is_timestamp(line):
    """檢查是否為時間戳的格式"""
    timestamp_pattern = r"^\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}$"
    return bool(re.match(timestamp_pattern, line.strip()))


def is_subtitle_number(line):
    """檢查是否為字幕序號"""
    return line.strip().isdigit()


def translate_text(text, source_language="ja"):
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
                        "你是一個專業的日文到繁體中文翻譯。請遵循以下規則：\n"
                        "1. 準確翻譯日文內容為繁體中文\n"
                        "2. 保留所有英文字母、數字和專有名詞\n"
                        "3. 保持原始標點符號格式\n"
                        "4. LINE、Yahoo 等品牌名稱保持原樣\n"
                        "5. 確保翻譯的完整性和準確性"
                    ),
                },
                {"role": "user", "content": text},
            ],
            temperature=0.1,  # 降低創意度以獲得更準確的翻譯
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"\n翻譯錯誤: {str(e)}")
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
        ensure_directory_exists(output_file)

    # 讀取輸入文件
    encodings = ["utf-8", "utf-8-sig", "shift-jis", "euc-jp"]
    content = None

    for encoding in encodings:
        try:
            with open(input_file, "r", encoding=encoding) as file:
                content = file.readlines()
            print(f"成功使用 {encoding} 編碼讀取文件")
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        raise ValueError("無法讀取輸入文件，請檢查文件編碼")

    # 處理字幕
    current_block = []
    translated_blocks = []
    subtitle_text = None

    # 使用 tqdm 創建進度條
    progress_bar = tqdm(total=len(content), desc="翻譯進度", unit="行")

    for line in content:
        line = line.strip()
        if not line:  # 空行表示區塊結束
            if current_block:
                if subtitle_text:  # 如果有需要翻譯的文本
                    translated_text = translate_text(subtitle_text)
                    current_block.append(translated_text)
                translated_blocks.append("\n".join(current_block))
                current_block = []
                subtitle_text = None
        elif is_subtitle_number(line):
            current_block.append(line)
        elif is_timestamp(line):
            current_block.append(line)
        else:
            subtitle_text = line

        progress_bar.update(1)

    # 處理最後一個區塊
    if current_block and subtitle_text:
        translated_text = translate_text(subtitle_text)
        current_block.append(translated_text)
        translated_blocks.append("\n".join(current_block))

    progress_bar.close()

    # 寫入翻譯結果
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write("\n\n".join(translated_blocks) + "\n")
        print(f"\n翻譯結果已成功寫入檔案: {output_file}")
    except Exception as e:
        print(f"\n寫入檔案時發生錯誤: {str(e)}")
        raise


def verify_translation(input_file, output_file, num_lines=15):
    """驗證翻譯結果的前 N 行"""
    print(f"\n驗證前 {num_lines} 行翻譯結果:")
    print("-" * 50)

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            input_lines = f.readlines()[:num_lines]
        with open(output_file, "r", encoding="utf-8") as f:
            output_lines = f.readlines()[:num_lines]

        print("原文:")
        print("".join(input_lines))
        print("\n翻譯:")
        print("".join(output_lines))

    except Exception as e:
        print(f"驗證過程中發生錯誤: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="將日文 SRT 字幕檔翻譯成中文")
    parser.add_argument("input_file", type=str, help="輸入的 SRT 檔案路徑")
    parser.add_argument("output_file", type=str, help="翻譯後的 SRT 檔案儲存路徑")
    parser.add_argument("--verify", action="store_true", help="驗證翻譯結果")

    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("未找到 OpenAI API 金鑰，請設定 OPENAI_API_KEY 環境變數")

    try:
        if not os.path.exists(args.input_file):
            raise FileNotFoundError(f"找不到輸入檔案: {args.input_file}")

        print("開始翻譯處理...")
        translate_srt(args.input_file, args.output_file)

        if args.verify:
            verify_translation(args.input_file, args.output_file)

        print(f"翻譯完成！翻譯後的檔案已儲存為：{args.output_file}")
    except Exception as e:
        print(f"程式執行時發生錯誤: {str(e)}")
        exit(1)
