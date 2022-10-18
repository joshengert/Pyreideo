#Pyreideo CLI
#CLI Interface for downloading videos hosted on reddit
#Josh Engert, 2022

import requests
import ffmpeg
import os
import typer


app = typer.Typer()

def get_json(subreddit, listing, limit, timeframe):
    try:
        base_url = f'https://www.reddit.com/r/{subreddit}/{listing}.json?limit={limit}&t={timeframe}'
        request = requests.get(base_url, headers = {'User-agent': 'Pyreideo CLI'})
    except:
        print('An Error Occured')
    return request.json()


def get_json_from_url(url: str):
    try:
        url = url.rstrip(url[-1]) + '.json'
        request = requests.get(url, headers = {'User-agent': 'Pyreideo CLI'})
    except:
        print('An Error Occured')
    return request.json()


def get_post(r):
    posts = []
    for post in r['data']['children']:
        if post['data']['is_video']:
            if  'reddit_video' in post['data']['secure_media']:
                x = [post['data']['title'], post['data']['secure_media']['reddit_video']['fallback_url'], post['data']['secure_media']['reddit_video']['fallback_url'][0:32] + 'DASH_audio.mp4?source=fallback' ]
                posts.append(x)
    return posts

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


def audio_good(filename):
    audio = ffmpeg.probe(str(filename), select_streams='a')
    return audio["streams"] 


def download_and_merge(p, merge_audio: bool = True):
    x = 0
    if len(p) == 0:
        print('No video found')
        return
    remove_string = " %:/,.\\[]<>*?"


    while x < len(p):
        name = p[x][0][0:160].replace(' ', '_')
        for c in name:
            if c in remove_string:
                output_name = name.replace(c, "")
            else:
                output_name = name
        video = requests.get(p[x][1], headers = {'User-agent': 'Pyreideo CLI'})
        open('video' + str(x) + '.mp4', "wb").write(video.content)
        if merge_audio:
            audio = requests.get(p[x][2], headers = {'User-agent': 'Pyreideo CLI'})
            open('audio' + str(x) + '.mp4', "wb").write(audio.content)                
           

            
            if os.path.exists('downloaded') == False:
                os.mkdir('downloaded')
            try:
                input_video = ffmpeg.input('video' + str(x) + '.mp4')
                
                if audio_good('audio' + str(x) + '.mp4'):
                    input_audio = ffmpeg.input('audio' + str(x) + '.mp4')
                    ffmpeg.concat(input_video, input_audio, v=1, a=1).output('downloaded\\' + output_name + '.mp4').run()
                    os.remove('video' + str(x) + '.mp4')
                    os.remove('audio' + str(x) + '.mp4')
                else:
                    print('ALERT: ' + output_name + '.mp4 has no audio')
                    os.replace('video' + str(x) + '.mp4', 'downloaded\\' + output_name + '.mp4') 
                    os.remove('audio' + str(x) + '.mp4')
            except ffmpeg._run.Error:
                print('ffmpeg error, files downloaded but not merged.')
        else:
            os.replace('video' + str(x) + '.mp4', 'downloaded\\' + output_name + '.mp4')    
        x += 1


@app.command()
def scrape(subreddit: str, listing: str, limit: int, timeframe: str, merge_audio: bool = True):
    results = get_json(subreddit,listing,limit,timeframe)
    posts = get_post(results)
    download_and_merge(posts, merge_audio)


@app.command()
def url_dl(url: str, merge_audio: bool = True):
    info = get_json_from_url(url) 
    post = get_post_info(info)
    download_and_merge(post, merge_audio)


if __name__ == '__main__':
    app()
    