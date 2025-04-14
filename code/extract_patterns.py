"""
Extract patterns from the spam list and label number subsets as call centers to block highly likely scam numbers missing from the source.
"""
import pandas as pd
from collections import Counter
from pathlib import Path
from helpers import (
    ARCHIVE_PATH,
    CUT_OFF_PERCENT,
    rename_to_today,
    get_most_recent_txt_file,
    copy_as_latest,
)


def spam_patterns_txt_files_creation(folder_path: Path):
    spam_text_file = get_most_recent_txt_file(folder_path)
    print(f"File used for pattern extraction: {spam_text_file}")
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
    # Here we use the defined percentage in helpers.py
    # to arbitrarily decide when there are enough spams
    # in a +41 123 45 ## range to label it as 100% spam.
    minus_2_prefixes_temp = (
        df_filtered[df_filtered["spam_%_2"] >= CUT_OFF_PERCENT]
        .loc[:, "minus_2"]
        .unique()
    )
    # Quickly remove prefixes covered by 3&4 digit prefixes
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
    copy_as_latest(rename_to_today(folder_path, standalone_filename))

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

    copy_as_latest(rename_to_today(folder_path, pattern_filename))


def main():
    spam_patterns_txt_files_creation(ARCHIVE_PATH)
    print("Patterns extracted!")

if __name__ == "__main__":
    main()
