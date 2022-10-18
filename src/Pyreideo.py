#Pyreideo CLI
#CLI Interface for downloading videos hosted on reddit
#Josh Engert, 2022

import requests
import ffmpeg
import os
import typer


app = typer.Typer()

#Gets the json file for the posts with the specified parameters
def get_json(subreddit, listing, limit, timeframe):
    try:
        base_url = f'https://www.reddit.com/r/{subreddit}/{listing}.json?limit={limit}&t={timeframe}'
        request = requests.get(base_url, headers = {'User-agent': 'Pyreideo CLI'})
    except:
        print('An Error Occured')
    return request.json()

#Gets the json file from the url specified
def get_json_from_url(url: str):
    try:
        url = url.rstrip(url[-1]) + '.json'
        request = requests.get(url, headers = {'User-agent': 'Pyreideo CLI'})
    except:
        print('An Error Occured')
    return request.json()

#Gets a single post and adds it to the list of posts to iterate through and download
def get_post(r):
    posts = []
    for post in r['data']['children']:
        if post['data']['is_video']:
            if  'reddit_video' in post['data']['secure_media']:
                x = [post['data']['title'], post['data']['secure_media']['reddit_video']['fallback_url'], post['data']['secure_media']['reddit_video']['fallback_url'][0:32] + 'DASH_audio.mp4?source=fallback' ]
                posts.append(x)
    return posts

#Gets a posts title, video url and audio url
def get_post_info(r):
    info = []
    try:
        for post in r[0]['data']['children']:    
            if post['data']['is_video']:
                if  'reddit_video' in post['data']['secure_media']:
                    x = [post['data']['title'], post['data']['secure_media']['reddit_video']['fallback_url'], post['data']['secure_media']['reddit_video']['fallback_url'][0:32] + 'DASH_audio.mp4?source=fallback' ]
                    info.append(x)
            else:
                print("Video not hosted on reddit")    
    except(KeyError):
        print('Not a valid post, use the url from the comments page')

    return info

#Checks if the audio is a valid stream. Stops ffmpeg from throwing errors if videos have no audio
def audio_good(filename):
    audio = ffmpeg.probe(str(filename), select_streams='a')
    return audio["streams"] 

#Downloads and merges the audio files (if they exist)
def download_and_merge(p, merge_audio: bool = True):
    x = 0
    #Check we found videos to download
    if len(p) == 0:
        print('No video found')
        return
    #String to check against for naming downloaded files
    remove_string = " %:/,.\\[]<>*?"
    while x < len(p):
        #Renaming
        name = p[x][0][0:160].replace(' ', '_')
        for c in name:
            if c in remove_string:
                output_name = name.replace(c, "")
            else:
                output_name = name
        #Download the video and create a temporary video only file        
        video = requests.get(p[x][1], headers = {'User-agent': 'Pyreideo CLI'})
        open('video' + str(x) + '.mp4', "wb").write(video.content)
        

        if merge_audio:
            #Download audio and create temporary audio file
            audio = requests.get(p[x][2], headers = {'User-agent': 'Pyreideo CLI'})
            open('audio' + str(x) + '.mp4', "wb").write(audio.content)                

            #Check if the downloaded video folder exists, if not create one
            if os.path.exists('downloaded') == False:
                os.mkdir('downloaded')
            
            #Try to merge the audio and video files, then delete the remaining temporary files
            try:
                input_video = ffmpeg.input('video' + str(x) + '.mp4')
                #Checks for issues in audio before merging
                if audio_good('audio' + str(x) + '.mp4'):
                    input_audio = ffmpeg.input('audio' + str(x) + '.mp4')
                    ffmpeg.concat(input_video, input_audio, v=1, a=1).output('downloaded\\' + output_name + '.mp4').run()
                    os.remove('video' + str(x) + '.mp4')
                    os.remove('audio' + str(x) + '.mp4')
                #Tell user the video has no audio and move the video only file to downloaded folder
                else:
                    print('ALERT: ' + output_name + '.mp4 has no audio')
                    os.replace('video' + str(x) + '.mp4', 'downloaded\\' + output_name + '.mp4') 
                    os.remove('audio' + str(x) + '.mp4')
            #Ffmpeg error thrown
            except ffmpeg._run.Error:
                print('ffmpeg error, files downloaded but not merged.')
        #User specified no audio
        else:
            os.replace('video' + str(x) + '.mp4', 'downloaded\\' + output_name + '.mp4')    
        x += 1

#Scrape
@app.command()
def scrape(subreddit: str, listing: str, limit: int, timeframe: str, merge_audio: bool = True):
    results = get_json(subreddit,listing,limit,timeframe)
    posts = get_post(results)
    download_and_merge(posts, merge_audio)

#Url-dl
@app.command()
def url_dl(url: str, merge_audio: bool = True):
    info = get_json_from_url(url) 
    post = get_post_info(info)
    download_and_merge(post, merge_audio)

#Main
if __name__ == '__main__':
    app()
    