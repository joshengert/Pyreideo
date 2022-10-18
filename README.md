# Pyreideo
 Python downloader for videos hosted on Reddit

# Get Started 
- Download the latest version of ffmpeg and place the contents of the bin folder in the same place as the pyreideo.py file
- open cmd and run from the command line

# Usage 
Scrape a subreddit with ````scrape````, or download a specific link with ````url-dl````

Url-dl requires a url the only argument:
````
$ python pyreideo.py url-dl https://www.reddit.com/r/MadeMeSmile/comments/ws03i5/the_rick_roll_still_going_strong/
````
Scrape requires a subreddit, the listing type(new, hot, top, etc), the number of posts to scrape, and the timeframe(day, month, year, alltime):
````
$ python pyreideo.py scrape videomemes top 10 month
````
To download without audio use ````--no-merge-audio````:
````
$ python pyreideo.py scrape videomemes top 50 alltime --no-merge-audio
````

# Requirements
 - ffmpeg (easiest to put the binaries in same folder as the script)
 - requests 
 - typer
 
