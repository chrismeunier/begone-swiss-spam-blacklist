"""
Script to read all identified scam numbers from local.ch.
Saves them as a text file in the archive folder
"""

import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from helpers import (
    BASE_URL,
    HREF_PATTERN,
    ARCHIVE_PATH,
    TEXT_FILE,
    rename_to_today,
    copy_as_latest,
)

user_agent = UserAgent(platforms="desktop").random
failed_pages = []

def create_initial_text_file():
    """Called to scrape local.ch and get the complete list of spam numbers in a text file."""

    if (ARCHIVE_PATH / TEXT_FILE).exists():
        (ARCHIVE_PATH / TEXT_FILE).unlink()

    page = 1
    while read_write_current_page(page):
        page += 1
    # Retry if needed (but only once)
    for fail in failed_pages:
        read_write_current_page(fail)
    print(f"Read data from {page-1} pages.")


def read_write_current_page(page_number: int):
    URL = BASE_URL + str(page_number)
    print(f"url : {URL}")

    try:
        r = requests.get(URL, headers={"User-Agent": user_agent})
    except requests.exceptions.ConnectionError as err:
        print(f"URL failed to load {URL}\n\tWith error: {err}")
        failed_pages.append(page_number)
        return True # continue as usual

    url_read_correctly = r.status_code == requests.codes.ok
    print(f"page {page_number}, request {'OK' if url_read_correctly else 'not OK'}: {r.status_code}")
    if not url_read_correctly:
        return False

    soup = BeautifulSoup(r.content, "html.parser")

    search = soup.find_all("a", href=HREF_PATTERN)
    if not search:
        print("Empty page!\n")
        return False

    current_page_number_list = [
        # remove all whitespaces
        "".join(element.get_text().split())
        for element in search
    ]

    # Append the list contents to the text file
    with open(ARCHIVE_PATH / TEXT_FILE, "a+", encoding="utf-8") as output:
        for number in current_page_number_list:
            # Remove starting 0 and replace it with +41
            output.write("+41" + number[1:] + "\n")

    return url_read_correctly



def main():
    create_initial_text_file()
    copy_as_latest(rename_to_today(ARCHIVE_PATH, TEXT_FILE))


if __name__ == "__main__":
    main()
