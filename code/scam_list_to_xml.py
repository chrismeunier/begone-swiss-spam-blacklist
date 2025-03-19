"""
Turn the spam lists (with and without patterns) into a xml file to be imported in the Begone app.
"""

import plistlib
from helpers import (
    ROOT_PATH,
    XML_FILE,
    XML_PATTERNS_FILE,
    get_most_recent_txt_file,
)


def write_xml_file(
    xml_filename: str,
    txt_file_glob: str = "spam_numbers*.txt",
    xml_entry_description: str = "Spam",
):
    # xml file creation from list of spam numbers formatted as "+411234567890"
    most_recent_file = get_most_recent_txt_file(filename_pattern=txt_file_glob)

    with open(most_recent_file, "r", encoding="utf-8") as text_file:

        plist_body = [
            xml_entry_from_number(spam_number, xml_entry_description)
            for spam_number in text_file
        ]

        dump_plist(xml_filename, plist_body)


def dump_plist(xml_filename: str, plist_body: list):
    with open(ROOT_PATH / xml_filename, "wb") as xml_file:
        plistlib.dump(plist_body, xml_file)


def xml_entry_from_number(number: str, title: str):
    return {
        "title": title,
        "addNational": "true",
        "category": "0",
        "number": number.strip(),
    }


def append_xml_file(
    xml_filename: str,
    txt_file_glob: str = "spam_numbers*.txt",
    xml_entry_description: str = "Spam",
):
    if not (ROOT_PATH / xml_filename).exists():
        raise FileNotFoundError

    with open(ROOT_PATH / xml_filename, "rb") as xml_file:
        plist_body: list = plistlib.load(xml_file, fmt=plistlib.FMT_XML)

    most_recent_file = get_most_recent_txt_file(filename_pattern=txt_file_glob)

    with open(most_recent_file, "r", encoding="utf-8") as text_file:
        new_plist_body = [
            xml_entry_from_number(spam_number, xml_entry_description)
            for spam_number in text_file
        ]
        plist_body.extend(new_plist_body)
        dump_plist(xml_filename, plist_body)


def main():
    # write the resulting files to a .xml formatted for Begone
    write_xml_file(xml_filename=XML_FILE)
    write_xml_file(
        xml_filename=XML_PATTERNS_FILE,
        txt_file_glob="pattern_numbers*.txt",
        xml_entry_description="Spam (local.ch++)",
    )
    append_xml_file(
        xml_filename=XML_PATTERNS_FILE,
        txt_file_glob="standalone_numbers*.txt",
        xml_entry_description="Spam (local.ch)",
    )


if __name__ == "__main__":
    main()
