"""
Turn the spam lists (with and without patterns) into a xml file to be imported in the Begone app.
"""

import plistlib
from pathlib import Path
from helpers import (
    ROOT_PATH,
    XML_FILE,
    XML_PATTERNS_FILE,
    get_most_recent_txt_file,
    compare_and_update_files,
)


def write_xml_file(
    xml_filename: str,
    txt_file_glob: str = "spam_numbers*.txt",
    xml_entry_description: str = "Spam",
) -> Path:
    # xml file creation from list of spam numbers formatted as "+411234567890"
    most_recent_file = get_most_recent_txt_file(filename_pattern=txt_file_glob)
    print(f"File used: {most_recent_file}")

    with open(most_recent_file, "r", encoding="utf-8") as text_file:

        plist_body = [
            xml_entry_from_number(spam_number, xml_entry_description)
            for spam_number in text_file
        ]

    dump_plist(ROOT_PATH / xml_filename, plist_body)
    return ROOT_PATH / xml_filename


def dump_plist(xml_file: Path, plist_body: list):
    new_xml = xml_file.parent / (xml_file.stem + "_new" + xml_file.suffix)
    print(f"Writing in {new_xml}")
    with open(new_xml, "wb") as f:
        plistlib.dump(plist_body, f)


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
) -> Path:
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

    dump_plist(ROOT_PATH / xml_filename, plist_body)
    return ROOT_PATH / xml_filename


def main():
    # write the resulting files to a .xml formatted for Begone
    new_xml = write_xml_file(xml_filename=XML_FILE)
    compare_and_update_files(ROOT_PATH / XML_FILE, new_xml)
    new_xml = write_xml_file(
        xml_filename=XML_PATTERNS_FILE,
        txt_file_glob="pattern_numbers*.txt",
        xml_entry_description="Spam (local.ch++)",
    )
    new_xml = append_xml_file(
        xml_filename=new_xml.name,
        txt_file_glob="standalone_numbers*.txt",
        xml_entry_description="Spam (local.ch)",
    )
    compare_and_update_files(ROOT_PATH / XML_PATTERNS_FILE, new_xml)


if __name__ == "__main__":
    main()
