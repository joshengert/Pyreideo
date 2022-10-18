#Pyreideo CLI
#CLI Interface for downloading videos hosted on reddit
#Josh Engert, 2022

import requests
import subprocess
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


def download_and_merge(p, merge_audio: bool = True):
    x = 0
    while x < len(p):
        video = requests.get(p[x][1])
        open('video' + str(x) + '.mp4', "wb").write(video.content)
        if merge_audio:
            audio = requests.get(p[x][2])
            open('audio' + str(x) + '.mp4', "wb").write(audio.content)
            output_name = p[x][0][:10].replace(' ', '_')
            if os.path.exists('downloaded') == False:
                os.mkdir('downloaded')
            try:
                subprocess.run('ffmpeg -y -i video' + str(x) + '.mp4 -i audio' + str(x) + '.mp4 -c:v copy -c:a aac downloaded\\' + output_name + '.mp4')
                os.remove('video' + str(x) + '.mp4')
                os.remove('audio' + str(x) + '.mp4')
            except:
                print('ffmpeg error, files downloaded but not merged. Ensure ffmpeg is in the correct folder.')
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
    