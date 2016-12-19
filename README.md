# AllMusicScrapper

*Usage: python allmusic.py -a <artist-name>
*Example: python allmusic.py -a lady gaga

This will give you artist's name, brief description, bio and albums in the form of dictionary. For each album, detailed information(title, label, year, rating, rating_count and cover image's URL) will be given.
If you want to add additional data using spotify's API, enter a valid OAuth token in 'spotify_token.txt'. If the token is valid, you can get additional info including artist's spotify_id and album's spotify_id.


This scrapper has the following dependency.

*bs4
requests
*selenium
*phantomjs

Selenium and phantomjs were necessary to build javascript-enabled scrapper.

To install, run the following script in the command line.

```
pip install bs4
pip install requests[security]
pip install selenium==2.53
brew install phantomjs
```
