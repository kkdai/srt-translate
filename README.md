# SRT Translator

A simple tool for translating SRT subtitle files from any source language to any target language using the OpenAI API.

This repository contains a Python script that supports multiple source and target languages for SRT subtitle translation. By default, it translates from Japanese (ja) to Traditional Chinese (zh-TW).

## Features

- Supports multiple SRT file encodings.
- Translates subtitle text using a GPT-4o-mini based model with configurable source and target languages.
- Detailed logging for debugging.
- Verification mode to compare original and translated files.

## Requirements

- Python 3.x
- OpenAI Python library
- tqdm  
- Other standard libraries (argparse, re, pathlib, logging, json, datetime)

## Setup

Install dependencies and configure your environment by setting the `OPENAI_API_KEY` variable:

```bash
pip install openai tqdm
```

## Usage

Run the script from the command line:

```bash
python translate.py input_file.srt output_file.srt [--debug] [--verify] [--source LANGUAGE_CODE] [--target LANGUAGE_CODE]
```

- **input_file.srt**: Path to the original SRT file.
- **output_file.srt**: Path where the translated file will be saved.
- **--debug**: Enable detailed logging for debugging purposes.
- **--verify**: Verify translation by comparing sample lines from the files.
- **--source**: Source language code (default: ja).
- **--target**: Target language code (default: zh-TW).

## Logging

Logs are generated in the `logs` directory with a timestamped filename, providing insights into the translation process.

## Translation Process

- Reads the SRT file using several encoding options.
- Identifies subtitle numbers, timestamps, and text blocks.
- Translates each block by sending it to the OpenAI API using the provided language options.
- Saves the translated content in proper SRT format.

## License

This project is licensed under the MIT License.
