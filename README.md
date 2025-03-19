# Spam caller blacklist for Switzerland

Lists for blocking spam calls in Switzerland using the Begone app

On iOS it is possible to use the [app Begone](https://apps.apple.com/ch/app/begone-blocage-spam-appel/id1596818195) to block phone numbers.
It also offers the option to block whole ranges of numbers.

## Lists and sources

The lists were sourced from [local.ch](https://www.local.ch/en/verified-telemarketing-numbers).

- **swiss_spam_callers.xml**: This list is simply all numbers as listed on local.ch.
- **swiss_spam_patterns.xml**: This list is made of patterns covering phone number ranges where many spam numbers are observed. It will thus block many additional numbers that are very likely spam. This list should be paired with _swiss_standalone_spam_callers.xml_.
- **swiss_standalone_spam_callers.xml**: This is the list of numbers not covered by any pattern. It should be used in tandem with the pattern list.

## Usage

- Download the lists on your phone (recommended: patterns + standalone).
- Install the Begone app and follow its installation instructions.
- In Begone import new numbers from the downloaded files. Voilà!
