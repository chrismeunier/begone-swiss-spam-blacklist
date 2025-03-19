"""Helpers and constants for the other scripts"""

import re
from pathlib import Path
from datetime import datetime

BASE_URL = "https://www.local.ch/fr/numeros-telemarketing-identifies?page="
HREF_PATTERN = re.compile(r"/telemarketer/*")

ROOT_PATH = Path(__file__).parent.parent
ARCHIVE_PATH = ROOT_PATH / "archive"
TEXT_FILE = "spam_numbers.txt"
XML_FILE = "swiss_spam_callers.xml"
XML_PATTERNS_FILE = "swiss_spam_patterns.xml"

CUT_OFF_PERCENT = 10.0


def rename_to_today(folder: Path, filename: str):
    # Rename file with today timestamp
    date_stamp = datetime.today().strftime("%Y-%m-%d")
    source = folder / filename
    target = Path(source.parent, f"{source.stem}_{date_stamp}{source.suffix}")
    source.replace(target)


def get_most_recent_txt_file(FOLDER: Path = ARCHIVE_PATH, filename_pattern: str = "spam_numbers*"):
    """Looks for files in FOLDER with filename_pattern in their name.
    Their name should end with a timestamp separated from the rest with an underscore.
    """
    text_files = list(FOLDER.glob(filename_pattern))
    return max(text_files, key=lambda f: f.stem.split("_")[-1])


if __name__ == "__main__":
    pass
