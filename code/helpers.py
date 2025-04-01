"""Helpers and constants for the other scripts"""

import re
import filecmp
from pathlib import Path
from datetime import datetime

BASE_URL = "https://www.local.ch/fr/numeros-telemarketing-identifies?page="
HREF_PATTERN = re.compile(r"/telemarketer/*")

ROOT_PATH = Path(__file__).parent.parent
ARCHIVE_PATH = ROOT_PATH / "archive"
TEXT_FILE = "spam_numbers.txt"
XML_FILE = "begone_autoblock.xml"
XML_PATTERNS_FILE = "begone_list.xml"

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

def get_version_file(f: Path):
    return f.parent / (f.stem + ".version")

def update_version_file(f: Path):
    version_file = get_version_file(f)

    with open(version_file, "r") as fv:
        version = fv.readline().strip().split(".")
        count = fv.readline().strip()
    major = int(version[0])
    minor = int(version[1])
    count = int(count)
    # Increment
    version_up = ".".join([str(major), str(minor + 1)])
    count_up = str(count + 1)

    with open(version_file, "w") as fv_up:
        fv_up.write(version_up + "\n")
        fv_up.write(count_up)

def compare_and_update_files(f_old: Path, f_new: Path):
    if filecmp.cmp(f_old, f_new):
        f_new.unlink()
        print(f"No update to the list {f_old.stem}")
    else:
        f_new.replace(f_old)
        update_version_file(f_old)
        print(f"Updated {f_old.stem}")

if __name__ == "__main__":
    pass
