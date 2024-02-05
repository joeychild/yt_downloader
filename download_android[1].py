from pytube import Playlist, YouTube
import os
from youtube_search import YoutubeSearch

def download(url, directory, av = "audio"):
        if av == "video":
            return "downloaded " + os.path.basename(YouTube(url).streams.filter(progressive = True, 
                    file_extension = "mp4").first().download(output_path = directory))
        return "downloaded " + os.path.basename(YouTube(url).streams.filter(
                    only_audio=True).first().download(output_path = directory))

match input("search or url?: "):
    case "search":
        results = YoutubeSearch(input("search query: "), max_results=int(input("num of results:"))).to_dict()

        for i in range(len(results)):
            vid = results[i]
            print(f'{vid["title"]}\n{vid["duration"]} | {vid["channel"]} | {vid["views"]}')
        
        directory = '/storage/emulated/0/Documents/Pydroid3/playlist downloads/' + input("enter directory name: ")
        print(download("youtube.com" + results[int(input("enter video number: ")) - 1]["url_suffix"], directory, input("video or audio?: ")))

    case "url":
        while True:
            try:
                directory = '/storage/emulated/0/Documents/Pydroid3/playlist downloads/' + input("enter directory name: ")
                url = input("enter url or press enter to exit program: ").lower()
                if "playlist" in url:
                    av = input("video or audio?: ")
                    for video in Playlist(url):
                        print(download(video, directory, av))
                else:
                    print(download(url, directory, input("video or audio?: ")))
            except:
                break
print("have a great rest of your day :D")