"""Helpers and constants for the other scripts"""

import re
import filecmp
from pathlib import Path
from datetime import datetime
from typing import Tuple
from random import shuffle


LOCAL_CH_URLS = [
    "https://www.local.ch/de/verifizierte-telefonmarketing-nummern?page=",
    "https://www.local.ch/fr/numeros-telemarketing-identifies?page=",
    "https://www.local.ch/en/verified-telemarketing-numbers?page=",
    "https://www.local.ch/it/numeri-telemarketing-identificati?page=",
]
shuffle(LOCAL_CH_URLS)
BASE_URL = LOCAL_CH_URLS.pop()
HREF_PATTERN = re.compile(r"/telemarketer/*")

ROOT_PATH = Path(__file__).parent.parent
ARCHIVE_PATH = ROOT_PATH / "archive"
TEXT_FILE = "spam_numbers.txt"
XML_FILE = "begone_autoblock.xml"
XML_PATTERNS_FILE = "begone_list.xml"

CUT_OFF_PERCENT = 10.0


def rename_to_today(folder: Path, filename: str) -> Path:
    # Rename file with today timestamp
    date_stamp = datetime.today().strftime("%Y-%m-%d")
    source = folder / filename
    target = Path(source.parent, f"{source.stem}_{date_stamp}{source.suffix}")
    source.replace(target)
    return target


def extract_timestamp(filename: str, sep="_") -> Tuple[str, str]:
    splitted = filename.split(sep)
    return splitted[-1], sep.join(splitted[:-1])


def copy_as_latest(filepath: Path):
    # Take a file and create a copy with "latest" instead of the timestamp
    name = extract_timestamp(filepath.stem)[1] + "_latest"
    target_path = Path(filepath.parent, name + filepath.suffix)
    target_path.write_text(filepath.read_text())


def get_most_recent_txt_file(
    FOLDER: Path = ARCHIVE_PATH, filename_pattern: str = "spam_numbers*"
):
    """Looks for files in FOLDER with filename_pattern in their name.
    Their name should end with a timestamp separated from the rest with an underscore.
    """
    text_files = list(FOLDER.glob(filename_pattern))
    return max(text_files, key=lambda f: f.stem.split("_")[-1])


def get_version_file(f: Path):
    return f.parent / (f.stem + ".version")


def update_version_file(f: Path):
    version_file = get_version_file(f)
    print(f"\tVersion file to update: {version_file}")

    with open(version_file, "r") as fv:
        version = fv.readline().strip().split(".")
        count = fv.readline().strip()
    major = int(version[0])
    minor = int(version[1])
    count = int(count)
    print(f"\tBefore: {major}.{minor}, {count}")
    # Increment
    version_up = ".".join([str(major), str(minor + 1)])
    count_up = str(count + 1)
    print(f"\tAfter: {version_up}, {count_up}")

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


def clean_archive_dir():
    # Keep the last file for each month and the "latest" file
    file_patterns = [
        "spam_numbers*.txt",
        "standalone_numbers*.txt",
        "pattern_numbers*.txt",
    ]

    for pattern in file_patterns:
        spam_files = ARCHIVE_PATH.glob(pattern)

        try:
            prev = spam_files.send(None)
        except StopIteration:
            return
        while True:
            try:
                next = spam_files.send(None)
                timestamp1 = extract_timestamp(prev.stem)[0]
                timestamp2 = extract_timestamp(next.stem)[0]
                same_month = timestamp1[5:7] == timestamp2[5:7]
                if timestamp1 < timestamp2 and same_month:
                    print(f"Deleting {prev.name}")
                    prev.unlink()

                prev = next
            except StopIteration:
                break


if __name__ == "__main__":
    pass
