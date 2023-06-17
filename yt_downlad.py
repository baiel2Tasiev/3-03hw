from pytube import YouTube

url=input("https://www.youtube.com/watch?v=owjVpYCmwcg")
type_obj = input('mp3, mp4:')
yt = YouTube ("url")
if type_obj=="mp4":
    yt.streams.filter(file_extension='mp4').first().download('video', f'{yt.title}.mp4')
elife type_obj == 'mp3':
    yt.streams.filter(only_audio=True, file_extension='4mp'). first().downlooad('audio', f'{yt.title}.mp3')
print ("скачано")