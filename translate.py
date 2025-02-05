import openai
import argparse
import os

# 从环境变量中获取 OpenAI API 密钥
openai.api_key = os.getenv("OPENAI_API_KEY")


def translate_text(text, source_language="zh", target_language="en"):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"You are a translator that translates text from {source_language} to {target_language}. Please use in Taiwan Chinese. 有專有英文名詞請維持英文。",
            },
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content.strip()


def translate_srt(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    translated_lines = []
    for line in lines:
        if line.strip() and not line[0].isdigit() and "-->" not in line:
            translated_line = translate_text(line.strip())
            translated_lines.append(translated_line + "\n")
        else:
            translated_lines.append(line)

    with open(output_file, "w", encoding="utf-8") as file:
        file.writelines(translated_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Translate a Japanese SRT file to Chinese."
    )
    parser.add_argument(
        "input_file", type=str, help="Path to the input Japanese SRT file."
    )
    parser.add_argument(
        "output_file", type=str, help="Path to save the translated Chinese SRT file."
    )

    args = parser.parse_args()

    if not openai.api_key:
        raise ValueError(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )

    translate_srt(args.input_file, args.output_file)
    print(f"Translation complete. Translated file saved as {args.output_file}.")
