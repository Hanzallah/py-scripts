### GitHub Scraper
This script fetches the information on a particular GitHub user.

#### How to run?
```
usage: scrapper.py [-h] [--json] username

Fetch information about Github user.

positional arguments:
  username        GitHub username whose information is needed.

optional arguments:
  -h, --help  show this help message and exit
  --file      Output data to a file or print in console. Takes in {y, n}
```

* `python3 github_scraper.py {username}`