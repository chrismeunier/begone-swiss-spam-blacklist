"""
Script to read all identified scam numbers from local.ch.
Extract patterns and label number subsets as call centers to block highly likely scam numbers.
Turn them into a xml file to be imported in the Begone app.
"""

import requests
import re
import plistlib
from bs4 import BeautifulSoup
from pathlib import Path  # for working locally
from datetime import datetime
import pandas as pd
from collections import Counter

BASE_URL = "https://www.local.ch/fr/numeros-telemarketing-identifies?page="
phone_number_href_pattern = re.compile(r"/telemarketer/*")

ROOT_PATH = Path(__file__).parent.parent
ARCHIVE_PATH = ROOT_PATH / "archive"
text_file = "spam_numbers.txt"


def main():
    # First time: scrape local.ch to a .txt file
    create_initial_text_file()
    # Following that: analyse it and extract patterns
    spam_patterns_txt_files_creation(ARCHIVE_PATH)
    # Then write the resulting file to a .xml formatted for Begone
    write_xml_file("swiss_spam_callers.xml")
    write_xml_file(
        "swiss_standalone_spam_callers.xml",
        ARCHIVE_PATH,
        "standalone_numbers*.txt",
        "Spam (local.ch)",
    )
    write_xml_file(
        "swiss_spam_patterns.xml",
        ARCHIVE_PATH,
        "pattern_numbers*.txt",
        "Spam (local.ch++)",
    )



# xml file creation from list of spam numbers formatted as "+411234567890"


def write_xml_file(
    xml_filename: str = "xml_test.xml",
    txt_file_path: Path = ARCHIVE_PATH,
    txt_file_glob: str = "spam_numbers*.txt",
    xml_entry_description: str = "Spam",
):

    most_recent_file = get_most_recent_txt_file(txt_file_path, txt_file_glob)

    with open(ROOT_PATH / xml_filename, "wb") as xml_file:

        with open(most_recent_file, "r", encoding="utf-8") as text_file:
            plist_body = [
                {
                    "title": xml_entry_description,
                    "addNational": "true",
                    "category": "0",
                    "number": spam_number.strip(),
                }
                for spam_number in text_file
            ]
            plistlib.dump(plist_body, xml_file)


def get_most_recent_txt_file(FOLDER: Path, filename_pattern: str = "spam_numbers*"):
    """Looks for files in FOLDER with filename_pattern in their name.
    Their name should end with a timestamp separated from the rest with an underscore.
    """
    text_files = list(FOLDER.glob(filename_pattern))
    return max(text_files, key=lambda f: f.stem.split("_")[-1])


# Web scraping and text file creation


def create_initial_text_file():
    """Called once to scrape local.ch and get the complete list of spam numbers in a text file."""

    page = 1
    while read_write_current_page(page):
        page += 1
    rename_to_today(ARCHIVE_PATH, text_file)


def read_write_current_page(page_number: int):
    URL = BASE_URL + str(page_number)
    print(f"url : {URL}")

    r = requests.get(URL)
    url_read_correctly = r.status_code == requests.codes.ok
    print(f"page {page_number} request success : {url_read_correctly}")
    if not url_read_correctly:
        return False

    soup = BeautifulSoup(r.content, "html.parser")

    search = soup.find_all("a", href=phone_number_href_pattern)
    if not search:
        print("Empty page!")
        return False

    current_page_number_list = [
        # remove all whitespaces
        "".join(element.get_text().split())
        for element in search
    ]

    # Append the list contents to the text file
    with open(ARCHIVE_PATH / text_file, "a+", encoding="utf-8") as output:
        for number in current_page_number_list:
            # Remove starting 0 and replace it with +41
            output.write("+41" + number[1:] + "\n")

    return url_read_correctly


def rename_to_today(folder: Path, filename: str):
    # Rename file with today timestamp
    date_stamp = datetime.today().strftime("%Y-%m-%d")
    source = folder / filename
    target = Path(source.parent, f"{source.stem}_{date_stamp}{source.suffix}")
    source.replace(target)


def spam_patterns_txt_files_creation(folder_path: Path):
    spam_text_file = get_most_recent_txt_file(folder_path)
    with open(spam_text_file, "r") as f:
        # Remove temporarily the +41
        spam_number_list = [line.strip()[3:] for line in f]

    df = pd.DataFrame({"base": spam_number_list})
    # Add columns with 2, 3 and 4 digits removed
    for removed_digits in range(2, 5):
        options = pow(10, removed_digits)
        df[f"minus_{removed_digits}"] = df["base"].str.slice(stop=-removed_digits)
        to_count = df[f"minus_{removed_digits}"]
        counter = Counter(to_count)
        df[f"count_{removed_digits}"] = [counter[str(x)] for x in to_count]
        df[f"spam_%_{removed_digits}"] = df[f"count_{removed_digits}"] / options * 100

    # Extract patterns for 4-digits:
    # When the proportion of spams blocked increases if using 4 instead of 2 digits in the pattern
    serie_4_over_2 = df["spam_%_2"] < df["spam_%_4"]
    minus_4_prefixes = df[serie_4_over_2].loc[:, "minus_4"].unique()
    # Idem for 3 digits:
    serie_3_over_2 = df["spam_%_2"] < df["spam_%_3"]
    minus_3_prefixes_temp = df[serie_3_over_2].loc[:, "minus_3"].unique()
    # Remove prefixes covered by 4-digit prefixes
    minus_3_prefixes = minus_3_prefixes_temp[
        [x[:-1] not in minus_4_prefixes for x in minus_3_prefixes_temp]
    ]
    # For prefixes with 2 digits we work with what we have left
    df_filtered = df[
        ~df["minus_4"].isin(minus_4_prefixes) & ~df["minus_3"].isin(minus_3_prefixes)
    ]
    CUT_OFF_PERCENT = 10.0
    minus_2_prefixes_temp = (
        df_filtered[df_filtered["spam_%_2"] >= CUT_OFF_PERCENT]
        .loc[:, "minus_2"]
        .unique()
    )
    minus_2_prefixes_temp2 = minus_2_prefixes_temp[
        [x[:-2] not in minus_4_prefixes for x in minus_2_prefixes_temp]
    ]
    minus_2_prefixes = minus_2_prefixes_temp2[
        [x[:-1] not in minus_3_prefixes for x in minus_2_prefixes_temp2]
    ]
    # We are left with the following numbers covered by no pattern:
    not_in_prefixes = (
        ~df["minus_4"].isin(minus_4_prefixes)
        & ~df["minus_3"].isin(minus_3_prefixes)
        & ~df["minus_2"].isin(minus_2_prefixes)
    )

    # Save the standalone numbers "not_in_prefixes"
    standalone_filename = "standalone_numbers.txt"
    standalone_numbers = df[not_in_prefixes]

    with open(folder_path / standalone_filename, "w", encoding="utf-8") as output:
        for number in standalone_numbers["base"]:
            # Re-add the +41
            output.write("+41" + number + "\n")
    rename_to_today(folder_path, standalone_filename)

    # Save the patterns
    pattern_filename = "pattern_numbers.txt"

    with open(folder_path / pattern_filename, "w", encoding="utf-8") as output:
        # Re-add the +41 and the trailing ####
        for pattern in minus_4_prefixes:
            output.write("+41" + pattern + 4 * "#" + "\n")
        for pattern in minus_3_prefixes:
            output.write("+41" + pattern + 3 * "#" + "\n")
        for pattern in minus_2_prefixes:
            output.write("+41" + pattern + 2 * "#" + "\n")

    rename_to_today(folder_path, pattern_filename)


if __name__ == "__main__":
    main()
