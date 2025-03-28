import argparse
import re
import os
import logging
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import json
import codecs
from openai import OpenAI

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_filename = f"translation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_dir / log_filename), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI()


def read_srt_file(file_path):
    """Attempt to read an SRT file with various encodings."""
    encodings = ["utf-8", "utf-8-sig", "utf-16", "shift-jis", "euc-jp", "iso-2022-jp"]

    for encoding in encodings:
        try:
            with codecs.open(file_path, "r", encoding=encoding) as f:
                content = f.read()
            logger.info(f"Successfully read file with encoding: {encoding}")
            return content
        except UnicodeDecodeError:
            continue

    raise ValueError(
        f"Could not decode {file_path} with any of the attempted encodings."
    )


def parse_srt(content):
    """Parse SRT content into blocks."""
    pattern = r"(\d+)[\r\n]+(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})[\r\n]+([\s\S]*?)(?=[\r\n]+\d+[\r\n]+|$)"
    matches = re.findall(pattern, content)

    blocks = []
    for match in matches:
        subtitle_number = match[0]
        timestamp = match[1]
        text = match[2].strip()
        blocks.append((subtitle_number, timestamp, text))

    return blocks


def translate_text(text, source_language, target_language):
    """Translate text using OpenAI API."""
    system_message = f"""
    You are a professional translator specializing in {source_language} to {target_language} translations.
    You must preserve all formatting and line breaks from the original text.
    Translate only the text content; do not modify any numbers, timestamps, or special characters.
    Your translations should sound natural and fluent in {target_language}, particularly with Taiwan usage patterns.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": text},
            ],
            temperature=0.1,
        )
        translated_text = response.choices[0].message.content
        return translated_text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text  # Return original text if translation fails


def translate_srt(
    input_file, output_file, source_lang="ja", target_lang="zh-TW", debug=False
):
    """Translate an SRT file from source language to target language."""
    if debug:
        logger.setLevel(logging.DEBUG)

    # Read the input file
    logger.info(f"Reading input file: {input_file}")
    content = read_srt_file(input_file)

    # Parse SRT content
    logger.info("Parsing SRT content")
    blocks = parse_srt(content)
    logger.info(f"Found {len(blocks)} subtitle blocks")

    # Translate blocks
    translated_blocks = []
    for subtitle_number, timestamp, text in tqdm(blocks, desc="Translating subtitles"):
        logger.debug(f"Translating block {subtitle_number}")
        logger.debug(f"Original text: {text}")

        translated_text = translate_text(text, source_lang, target_lang)
        logger.debug(f"Translated text: {translated_text}")

        translated_blocks.append((subtitle_number, timestamp, translated_text))

    # Write translated content to output file
    logger.info(f"Writing translated content to: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        for subtitle_number, timestamp, text in translated_blocks:
            f.write(f"{subtitle_number}\n")
            f.write(f"{timestamp}\n")
            f.write(f"{text}\n\n")

    logger.info("Translation completed")


def verify_translation(input_file, output_file):
    """Verify translation by comparing sample lines from both files."""
    input_content = read_srt_file(input_file)
    output_content = read_srt_file(output_file)

    input_blocks = parse_srt(input_content)
    output_blocks = parse_srt(output_content)

    if len(input_blocks) != len(output_blocks):
        logger.warning(
            f"Block count mismatch: Input has {len(input_blocks)} blocks, Output has {len(output_blocks)} blocks"
        )

    sample_size = min(5, len(input_blocks))
    sample_indices = [
        0,
        len(input_blocks) // 4,
        len(input_blocks) // 2,
        3 * len(input_blocks) // 4,
        len(input_blocks) - 1,
    ]
    sample_indices = [
        i for i in sample_indices if i < len(input_blocks) and i < len(output_blocks)
    ]

    print("\nVerification Samples:")
    for idx in sample_indices[:sample_size]:
        print(f"\nBlock {input_blocks[idx][0]}:")
        print(f"Original: {input_blocks[idx][2]}")
        print(f"Translated: {output_blocks[idx][2]}")


def main():
    parser = argparse.ArgumentParser(
        description="Translate SRT subtitle files using OpenAI API"
    )
    parser.add_argument("input_file", help="Path to the original SRT file")
    parser.add_argument(
        "output_file", help="Path where the translated file will be saved"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable detailed logging for debugging"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify translation by comparing sample lines",
    )
    parser.add_argument(
        "--source", default="ja", help="Source language code (default: ja)"
    )
    parser.add_argument(
        "--target", default="zh-TW", help="Target language code (default: zh-TW)"
    )

    args = parser.parse_args()

    translate_srt(
        args.input_file, args.output_file, args.source, args.target, args.debug
    )

    if args.verify:
        verify_translation(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
