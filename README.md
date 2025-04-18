# Spam caller blacklist for Switzerland

Lists for blocking spam calls in Switzerland using the Begone app

On iOS it is possible to use the [app Begone](https://apps.apple.com/ch/app/begone-blocage-spam-appel/id1596818195) to block phone numbers.
It also offers the option to block ranges of phone numbers.

## Lists and sources

The lists were sourced from [local.ch](https://www.local.ch/en/verified-telemarketing-numbers).

- **begone_autoblock.xml**: This list is simply all numbers as listed on local.ch.
- **begone_list.xml**: This list is made of patterns covering phone number ranges where many spam numbers are observed. It will thus block many additional numbers that are very likely spam. It also contains the numbers not covered by any pattern.

## Usage

- Install the Begone app and follow its installation instructions.
- In Begone go in the Community lists and install the list for Switzerland. Voilà!
- Keep it up to date from time to time, the list is updated at most once a week.

### Disclaimer

No guarantee whatsoever is given. Marketing calls may not be blocked by these lists for a variety of reasons: _local.ch_ not listing their number, usage of spoofing to fake a valid number, etc.

The chance that a valid number might be blocked by the patterns list exists too. If this happens you can add the number to the allowed numbers in Begone, and report it here of course.
