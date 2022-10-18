# Pyreideo
 Python downloader for video hosted on Reddit

# Usage 
Scrape a subreddit with ````scrape````, or download a specific link with ````url-dl````

url-dl:
````
$ python pyreideo.py url-dl https://www.reddit.com/r/MadeMeSmile/comments/ws03i5/the_rick_roll_still_going_strong/
````
scrape:
````
$ python pyreideo.py scrape videomemes top 10 month
````
# Requirements
 - ffmpeg (easiest to put the binaries in same folder as the script)
 - requests 
 - typer
 
