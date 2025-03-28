import subprocess
import os
from pathlib import Path


def main():
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()

    # Define file paths
    input_file = current_dir / "origin.srt"
    output_file = current_dir / "target.srt"

    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found!")
        return

    # Run the translation
    print(f"Starting translation from {input_file} to {output_file}...")
    print("This may take a few minutes depending on the file size.")

    try:
        subprocess.run(
            [
                "python",
                current_dir / "translate_subtitles.py",
                str(input_file),
                str(output_file),
                "--source",
                "ja",
                "--target",
                "zh-TW",  # "zh-TW", "en", "ko", "fr", "de", "es", "pt", "it", "tr", "vi", "th", "id", "ru", "ar", "hi", "bn", "mr", "ta", "te", "ml", "ur", "fa", "ps", "sw", "am", "yo", "ha", "ig", "ceb", "jv", "su", "ms", "tl", "hmn", "my", "km", "ne", "si", "sd", "gu", "pa", "or", "as", "bn", "ma", "kn", "sa
            ],
            check=True,
        )

        print(f"\nTranslation completed successfully!")
        print(f"Translated file saved to: {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error during translation: {e}")


if __name__ == "__main__":
    main()
