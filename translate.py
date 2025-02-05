import openai
import argparse
import os
import re
from pathlib import Path
from tqdm import tqdm
import logging
import json
from datetime import datetime


def setup_logging(debug_mode=False):
    """設定 logging 配置"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"translation_log_{timestamp}.log")

    level = logging.DEBUG if debug_mode else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return log_file


def debug_print_block(
    block_num, subtitle_number, timestamp, text, translated_text=None
):
    """輸出字幕區塊的除錯資訊"""
    debug_info = {
        "區塊編號": block_num,
        "字幕序號": subtitle_number,
        "時間戳": timestamp,
        "原文": text,
        "譯文": translated_text,
    }
    logging.debug(
        f"字幕區塊資訊:\n{json.dumps(debug_info, ensure_ascii=False, indent=2)}"
    )


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
        if not text.strip():
            logging.warning("收到空文本進行翻譯")
            return ""

        logging.debug(f"準備翻譯文本: {text}")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
            temperature=0.1,
        )
        translated = response.choices.message.content.strip()
        logging.debug(f"翻譯結果: {translated}")
        return translated
    except Exception as e:
        logging.error(f"翻譯過程發生錯誤: {str(e)}")
        return text


def translate_srt(input_file, output_file, debug_mode=False):
    """翻譯 SRT 文件"""
    logging.info(f"開始處理檔案: {input_file}")

    try:
        # 讀取檔案
        encodings = ["utf-8", "utf-8-sig", "shift-jis", "euc-jp"]
        content = None
        used_encoding = None

        for encoding in encodings:
            try:
                with open(input_file, "r", encoding=encoding) as file:
                    content = file.readlines()
                used_encoding = encoding
                logging.info(f"使用 {encoding} 編碼成功讀取檔案")
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            raise ValueError("無法讀取輸入文件，請檢查文件編碼")

        logging.info(f"最終使用的編碼: {used_encoding}")  # 使用 used_encoding 變數

        translated_blocks = []  # **修改**: 移到迴圈外
        current_block = {"number": None, "timestamp": None, "text": []}
        block_count = 0

        for line in tqdm(content, desc="處理字幕"):
            line = line.strip()

            # If a new subtitle number is found and there's an ongoing block, flush it.
            if is_subtitle_number(line):
                if current_block["number"] is not None:
                    block_count += 1
                    if current_block["text"]:
                        text_to_translate = " ".join(current_block["text"])
                        translated_text = translate_text(text_to_translate)
                        block_content = (
                            f"{current_block['number']}\n"
                            f"{current_block['timestamp']}\n"
                            f"{translated_text}"
                        )
                        translated_blocks.append(block_content)
                        debug_print_block(
                            block_count,
                            current_block["number"],
                            current_block["timestamp"],
                            text_to_translate,
                            translated_text,
                        )
                    current_block = {"number": None, "timestamp": None, "text": []}
                current_block["number"] = line
                logging.debug(f"找到字幕序號: {line}")
            elif is_timestamp(line):
                current_block["timestamp"] = line
                logging.debug(f"找到時間戳: {line}")
            elif not line:
                if current_block["number"]:
                    block_count += 1
                    if current_block["text"]:
                        text_to_translate = " ".join(current_block["text"])
                        translated_text = translate_text(text_to_translate)
                        block_content = (
                            f"{current_block['number']}\n"
                            f"{current_block['timestamp']}\n"
                            f"{translated_text}"
                        )
                        translated_blocks.append(block_content)
                        debug_print_block(
                            block_count,
                            current_block["number"],
                            current_block["timestamp"],
                            text_to_translate,
                            translated_text,
                        )
                    current_block = {"number": None, "timestamp": None, "text": []}
            else:
                current_block["text"].append(line)
                logging.debug(f"找到字幕文本行: {line}")

        # 處理最後一個區塊
        if current_block["number"]:  # 只需檢查序號是否存在
            block_count += 1
            if current_block["text"]:
                text_to_translate = " ".join(current_block["text"])
                translated_text = translate_text(text_to_translate)
                block_content = (
                    f"{current_block['number']}\n"
                    f"{current_block['timestamp']}\n"
                    f"{translated_text}"
                )
                translated_blocks.append(block_content)

                debug_print_block(
                    block_count,
                    current_block["number"],
                    current_block["timestamp"],
                    text_to_translate,
                    translated_text,
                )

        # 寫入翻譯結果
        with open(output_file, "w", encoding="utf-8") as file:
            file.write("\n\n".join(translated_blocks) + "\n")  # 確保以空行結尾
        logging.info(f"翻譯完成，已寫入檔案: {output_file}")

    except Exception as e:
        logging.error(f"處理過程發生錯誤: {str(e)}", exc_info=True)
        raise


def verify_translation(input_file, output_file, num_lines=15):
    """驗證翻譯結果"""
    logging.info("開始驗證翻譯結果")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            input_lines = f.readlines()[:num_lines]
        with open(output_file, "r", encoding="utf-8") as f:
            output_lines = f.readlines()[:num_lines]

        logging.info("原文:")
        for line in input_lines:
            logging.info(line.strip())
        logging.info("\n翻譯:")
        for line in output_lines:
            logging.info(line.strip())

    except Exception as e:
        logging.error(f"驗證過程發生錯誤: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="將日文 SRT 字幕檔翻譯成中文")
    parser.add_argument("input_file", type=str, help="輸入的 SRT 檔案路徑")
    parser.add_argument("output_file", type=str, help="翻譯後的 SRT 檔案儲存路徑")
    parser.add_argument("--debug", action="store_true", help="啟用除錯模式")
    parser.add_argument("--verify", action="store_true", help="驗證翻譯結果")

    args = parser.parse_args()

    # 設定日誌
    log_file = setup_logging(args.debug)
    logging.info(f"日誌檔案位置: {log_file}")

    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("未找到 OpenAI API 金鑰，請設定 OPENAI_API_KEY 環境變數")

        if not os.path.exists(args.input_file):
            raise FileNotFoundError(f"找不到輸入檔案: {args.input_file}")

        translate_srt(args.input_file, args.output_file, args.debug)

        if args.verify:
            verify_translation(args.input_file, args.output_file)

        logging.info("處理完成！")
    except Exception as e:
        logging.error(f"程式執行時發生錯誤: {str(e)}")
        exit(1)
