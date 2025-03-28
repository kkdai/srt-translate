# SRT Translator

A tool for translating SRT subtitle files using the OpenAI API. This project consists of two main scripts that work together to provide an easy translation workflow.

## Features

- Automated translation pipeline with a simple runner script
- Support for multiple language pairs (Japanese to Chinese, English, Korean, etc.)
- Intelligent handling of various SRT file encodings (utf-8, utf-16, shift-jis, etc.)
- Preservation of subtitle timing and formatting
- Progress tracking during translation
- Detailed logging for troubleshooting

## Requirements

- Python 3.x
- OpenAI Python library
- tqdm for progress bars
- OpenAI API key configured in your environment

## Setup

1. Install the required dependencies:

```bash
pip install openai tqdm
```

2. Ensure your OpenAI API key is set up in your environment

## Usage

### Quick Translation

The easiest way to translate subtitles is by using the runner script:

```bash
python run_translation.py
```

This will translate the file `origin.srt` from Japanese to Traditional Chinese and save it as `target.srt` in the same directory.

### Advanced Usage

For more control over the translation process, you can use the main script directly:

```bash
python translate_subtitles.py input.srt output.srt [--source SOURCE_LANG] [--target TARGET_LANG] [--debug] [--verify]
```

Parameters:

- `input.srt`: Path to the original SRT file
- `output.srt`: Path where the translated file will be saved
- `--source`: Source language code (default: ja)
- `--target`: Target language code (default: zh-TW)
- `--debug`: Enable detailed logging
- `--verify`: Show sample comparisons after translation

### Supported Languages

The script supports numerous target languages, including:

- Chinese (zh-TW)
- English (en)
- Korean (ko)
- French (fr)
- German (de)
- Spanish (es)
- Portuguese (pt)
- Italian (it)
- Turkish (tr)
- Vietnamese (vi)
- Thai (th)
- Indonesian (id)
- Russian (ru)
- Arabic (ar)
- And many more

## How It Works

1. The script reads the source SRT file, trying multiple encodings if necessary
2. It parses the file into numbered blocks with timestamps and text
3. Each text block is sent to OpenAI's GPT-4o model for translation
4. The translated blocks are reassembled with the original numbering and timestamps
5. The final output is written to a new SRT file

## Logging

Logs are saved in the `logs` directory with timestamps for troubleshooting and verification. The log format includes the timestamp, logger name, log level, and message.

## Translation Process

The translation uses OpenAI's GPT-4o model with a specialized system prompt that instructs the model to:

- Preserve all formatting and line breaks
- Maintain numbers, timestamps, and special characters
- Produce natural and fluent translations in the target language

## License

This project is licensed under the MIT License.
