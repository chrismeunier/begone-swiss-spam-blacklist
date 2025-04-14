import local_ch_to_list, extract_patterns, scam_list_to_xml
from helpers import clean_archive_dir

def main():
    local_ch_to_list.main()
    extract_patterns.main()
    scam_list_to_xml.main()
    clean_archive_dir()


if __name__ == "__main__":
    main()
