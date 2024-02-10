#module imports
import customtkinter as ctk
import urllib.request
from youtube_search import YoutubeSearch
from PIL import Image
from pytube import YouTube, Playlist
from easygui import diropenbox
from time import sleep
import socket
import base64
import os

'''
TO-DO
Socket:
Client and server for server-to-client sending: https://pastebin.com/KADZpqkM, https://pastebin.com/LySsgEe4
File sending: https://thepythoncode.com/article/send-receive-files-using-sockets-python

HTTP:
HTTP Intro: https://dev.to/chhajedji/transfer-data-between-your-phone-and-computer-without-any-cable-28m5
HTTP Sending Files?: https://floatingoctothorpe.uk/2017/receiving-files-over-http-with-python.html
HTTP Directory: https://stackoverflow.com/questions/39801718/how-to-run-a-http-server-which-serves-a-specific-path
HTML File for HTTP Server: https://stackoverflow.com/questions/59071797/how-can-i-make-a-python-server-open-an-html-file-as-deafult-instead-of-directory

Convert videos: https://stackoverflow.com/questions/56248567/how-do-i-decode-encode-a-video-to-a-text-file-and-then-back-to-video

Paramiko:
Intro: https://stackoverflow.com/questions/68335/how-to-copy-a-file-to-a-remote-server-in-python-using-scp-or-ssh

Documentation: 
Socket: https://docs.python.org/3/library/socket.html#socket.socket.listen
HTTP: https://docs.python.org/3/library/http.server.html#http.server.SimpleHTTPRequestHandler
Paramiko: https://docs.paramiko.org/en/latest/
CTk: https://github.com/TomSchimansky/CustomTkinter/wiki/CTkButton

======================== CTK ==========================
Playing videos: https://stackoverflow.com/questions/7227162/way-to-play-video-files-in-tkinter
Easygui: https://stackoverflow.com/questions/49600464/easygui-fileopenbox-open-a-path-with-a-ex-c-users-user-atom
TO-DO
- Add video playback function
- Multiple downloads
- Display IP and indicate when device is connected
- loading screen
- Fix progress bar
- Audio or video
Fix image position to left
Invalid search terms?
query for playlists?
fix frame issue (colors off)
'''

#root window
window = ctk.CTk()
window.geometry("600x400")
window.title("YT Downloader")

#buttons frame
frame = ctk.CTkFrame(window, 600, 30)
frame.pack()

#scroll frame
scroll = ctk.CTkScrollableFrame(window, 600, 400)
scroll.pack()

#download functions (overloaded)
def download(url):
    YouTube(url).streams.filter(progressive = True, 
            file_extension = "mp4").first().download(diropenbox())
    
def download2(url, output_path):
    return YouTube(url).streams.filter(progressive = True, 
            file_extension = "mp4").first().download(output_path)

#download progress
dl_scrn = None
def dl_progress(name):
    global dl_scrn, progress_bar, prog_lbl
    if dl_scrn == None or not dl_scrn.winfo_exists():
        dl_scrn = ctk.CTkToplevel(opts)

        prog_lbl = ctk.CTkLabel(dl_scrn, text="Downloading " + name)
        prog_lbl.pack()

        progress_bar = ctk.CTkProgressBar(dl_scrn)
        progress_bar.set(0)
        progress_bar.pack()

        dl_scrn.focus()
    dl_scrn.focus()

#options menu
opts = None
def options(url):
    global opts
    if opts == None or not opts.winfo_exists():
        opts = ctk.CTkToplevel(window)

        label = ctk.CTkLabel(opts, text = "Choose an option")
        label.pack()

        f_opts = ctk.CTkFrame(opts)
        f_opts.pack()

        server_btn = ctk.CTkButton(f_opts, 30, 30, image = ctk.CTkImage(Image.open("icons/server.png"), size=(20,20)), text = "", command= lambda link = url : server(link))
        server_btn.pack(side = "left")
        
        download_btn = ctk.CTkButton(f_opts, 30, 30, image = ctk.CTkImage(Image.open("icons/folder.png"), size=(20,20)), text = "", command= lambda link = url: download(link))
        download_btn.pack(side = "left")

        opts.focus()
        opts.mainloop()
    opts.focus()
    
#server function
def server(url):
    #download video
    vid = download2(url, "/")

    #start and connect socket
    ssFT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.gethostbyname(socket.gethostname()))
    ssFT.bind((socket.gethostbyname(socket.gethostname()), 8756))
    ssFT.listen(1)
    conn, _ = ssFT.accept()
    print("connected")

    #clear and open video data file
    text_file = 'vid_data.txt'
    if os.path.exists(text_file):
        os.remove(text_file)
    
    with open(vid, "rb") as videoFile:
        #convert video to b64
        conn.send(os.path.basename(vid).encode())
        dl_progress(conn.recv(1024).decode())

        #save b64 to text file
        with open(text_file, 'ab+') as fa:
            vid_data = base64.b64encode(videoFile.read())
            fa.write(vid_data)
            fa.close()
        
        #send b64 file
        with open(text_file, 'rb') as fa:
            sent = 0
            while True:
                data = fa.read(102400)
                if not data:
                    break
                #progress bar
                sent += len(data)
                progress_bar.set(sent/len(vid_data))
                conn.send(data)
                #receive data for delay (data loss if this is not included)
                conn.recv(1024)
            fa.close()
    ssFT.close()

    #clear progress bar
    prog_lbl.configure(bg_color = "green", text = "Completed!")
    sleep(1)
    if dl_scrn != None and dl_scrn.winfo_exists():
        dl_scrn.destroy()
    #remove download
    os.remove(vid)

#search function
def find():
    global results

    #clear previous videos
    for widget in scroll.winfo_children():
        widget.destroy()

    #textbox empty
    if len(search.get("0.0", "end")) == 1:
        print("fail")
        return
    
    #search
    results = YoutubeSearch(search.get("0.0", "end"), max_results=num).to_dict()

    #video buttons
    for i in range(len(results)):
        global vid
        vid = results[i]
        urllib.request.urlretrieve(vid["thumbnails"][0], "icons/thumbnail.png") #thumbnails
        video = ctk.CTkButton(scroll, image=ctk.CTkImage(Image.open("icons/thumbnail.png"), size=(160,90)), 
                              width=500, height=100, 
                              text=f'{'\n'.join([vid["title"][i:i+50] for i in range(0, len(vid["title"]), 50)])}\n{vid["duration"]} | {vid["views"]}', 
                              anchor="w", command= lambda url = "youtube.com" + vid["url_suffix"] : options(url)) #buttons
        video.pack()

#settings function
def settings():
    global num
    dialog = ctk.CTkInputDialog(text="Number of Results:", title="Video Results")
    try:
        num = int(dialog.get_input())
    except:
        num = 5

#url downloading function
def url_download():
    dialog = ctk.CTkInputDialog(text = "Enter URL", title="URL Download")
    url = dialog.get_input()
    try:
        #file dialog only requests once for playlist (and different function is needed)
        if "playlist" in url:
            for video in Playlist(url):
                download2(video, diropenbox())
        else:
            print("options")
            options(video)
    except:
        #invalid url
        pass

#search box and accompanying buttons
search = ctk.CTkTextbox(frame, 200, 30, activate_scrollbars=False, wrap="none")
search.pack(side = "left")
s_btn = ctk.CTkButton(frame, 30, 30, image = ctk.CTkImage(Image.open("icons/search.png"), size = (20, 20)), text="", command=find)
s_btn.pack(side = "left")
set_btn = ctk.CTkButton(frame, 30, 30, image = ctk.CTkImage(Image.open("icons/settings.png"), size = (20, 20)), text="", command=settings)
set_btn.pack(side = "left")
url_btn = ctk.CTkButton(frame, 30, 30, text="URL", text_color="black", command = url_download)
url_btn.pack(side = "left")

#searches when enter is pressed
import keyboard
keyboard.on_press_key("\n", lambda _:enter())

#clears newline
def enter():
    keyboard.press("\b")
    find()

#num videos
num = 5

#sustain window
window.mainloop()

#slider
# def num(value):
#     label.configure(text = int(value))

#separate settings window (original)
    # global set_scrn, label, slider
    # if set_scrn == None or not set_scrn.winfo_exists():
    #     set_scrn = ctk.CTkToplevel(window)
    #     label = ctk.CTkLabel(set_scrn, text = "5")
    #     label.pack()
    #     slider = ctk.CTkSlider(set_scrn, from_=1, to=20, number_of_steps=19, command=num)
    #     slider.set(5)
    #     slider.pack()
    #     btn = ctk.CTkButton(set_scrn, text = "Confirm", command=set_scrn.destroy)
    #     btn.pack()
    #     set_scrn.mainloop()
    # set_scrn.focus()
