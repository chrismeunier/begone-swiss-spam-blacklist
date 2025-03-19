"""
Turn the spam lists (with and without patterns) into a xml file to be imported in the Begone app.
"""

import plistlib
from pathlib import Path
from helpers import (
    ROOT_PATH,
    ARCHIVE_PATH,
    get_most_recent_txt_file,
)


def write_xml_file(
    xml_filename: str = "xml_test.xml",
    txt_file_path: Path = ARCHIVE_PATH,
    txt_file_glob: str = "spam_numbers*.txt",
    xml_entry_description: str = "Spam",
):
    # xml file creation from list of spam numbers formatted as "+411234567890"
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


def main():
    # write the resulting files to a .xml formatted for Begone
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


if __name__ == "__main__":
    main()
