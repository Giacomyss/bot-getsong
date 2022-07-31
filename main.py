import subprocess
from configparser import ConfigParser
import os
import requests
import subprocess
import time

config = ConfigParser()
config.read('config.cfg')

chat_id = config['credentials']['chat_id']
token = config['credentials']['token']
fs_music_root = config['filesystem']['music_root']

class GetSong:
    ''' GetSong
    '''
    def __init__(self):
        self.token = token
        self.chat_id = chat_id
        self.allowed_chat_id = [chat_id]

    def Get_Updates(self):
        ''' REST request toward bot to get updates '''
        # Create url
        url = f'https://api.telegram.org/bot{token}/getUpdates'

        # POST the message
        return requests.post(url).json()

    def Get_SongUrl(self, update):
        if not type(update) == dict:
            raise RuntimeError('instance Update failed to be parsed: object is not a dictionary')
        try:
            if not str(update['message']['from']['id']) in self.allowed_chat_id:
                raise RuntimeError('chat_id ' + str(update['message']['from']['id']) + ' not authorized')
            url = update['message']['text']
        except KeyError:
            msg = 'dictionary has fields ' + ', '.join(update.keys())
            raise KeyError('instance Update failed to be parsed: ' + msg)
        print("arrived url " + url.lower())
        return url if url[:5] == 'https' and url.lower().find('youtu.be') > 0 else ""

    def Send_Message(self, message = 'Here is my first message'):
        ''' REST request toward bot to send message '''
        # Create url
        url = f'https://api.telegram.org/bot{token}/sendMessage'

        # Create json link with message
        data = {'chat_id': chat_id, 'text': message}

        # POST the message
        requests.post(url, data)

    def Send_Song(self, filepath):
        ''' REST request toward bot to send an audio file '''
        print("Send_Song: " + filepath)
        if not os.path.exists(filepath):
            raise Exception("filepath {} doesn\'t exist".format(filepath))
        # Create url
        url = f'https://api.telegram.org/bot{token}/sendAudio'

        # Create json link with message
        data = {'chat_id': chat_id}
        files = {'audio': open(filepath, 'rb')}
        
        requests.post(url, data, files=files)

    def Download(self, url):
        cmd = 'youtube-dl --extract-audio --audio-format mp3 -o \'{}/%(title)s_%(id)s.mp3\' {}'.format(fs_music_root, url)
        os.system(cmd)

    def GetDownloadFilename(self, url):
        cmd = 'youtube-dl --get-filename -o \'{}/%(title)s_%(id)s.mp3\' {}'.format(fs_music_root, url)
        process_getfilename = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
        filepath = process_getfilename.read().decode("utf-8")
        return filepath.strip('\n')

if __name__ == "__main__":
    bot = GetSong()
    counter = 0
    while True:
        print("new iter")
        try:
            if not os.path.exists(fs_music_root):
                raise Exception("path {} does not exist".format(fs_music_root))
            result = bot.Get_Updates()

            if not result['ok']:
                print("Returned failure from GetUpdates call")
                continue

            if len(result['result']) > counter:
                print("Arrived new message")

                counter = len(result['result'])
                song_url = bot.Get_SongUrl(result['result'][-1])
                if len(song_url) > 0:
                    print("downloading file: " + bot.GetDownloadFilename(song_url))
                    bot.Download(song_url)
                    bot.Send_Song(bot.GetDownloadFilename(song_url))
        except Exception as e:
            bot.Send_Message(e)
        time.sleep(2)