# SRT Translator

This repository contains a Python script for translating SRT subtitle files from Japanese to Traditional Chinese using the OpenAI API.

## Features

- Reads SRT files with multiple encoding options (e.g., utf-8, shift-jis).
- Translates subtitle text using a GPT-4o-mini based model.
- Logs detailed information for debugging.
- Supports verification of translation by comparing original and translated files.

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
python translate.py input_file.srt output_file.srt [--debug] [--verify]
```

- **input_file.srt**: Path to the original SRT file.
- **output_file.srt**: Path where the translated file will be saved.
- **--debug**: Enable detailed logging for debugging purposes.
- **--verify**: Verify translation by comparing several lines from the original and translated files.

## Logging

Logs are generated in the `logs` directory with a timestamped filename. They provide detailed insights into the translation process, including block information and potential errors.

## Translation Process

- The script reads the SRT file using one of several encoding options.
- It identifies subtitle numbers, timestamps, and text blocks.
- Each block is sent to the OpenAI API for translation.
- Debug logging provides insights into each processed block.
- The translated content is saved with proper formatting to ensure compatibility with SRT viewers.

// ...existing code or details...

- Each block is sent to the OpenAI API for translation.

## License

This project is licensed under the MIT License.

- Debug logging provides insights into each processed block.
- The translated content is saved with proper formatting to ensure compatibility with SRT viewers.

// ...existing code or details...
