import os
import math
import inspect
import json
import getpass

class Settings():
    def get_settings(self):
        return [{
            name: getattr(self, name)
            for name, value in inspect.getmembers(type(self))
            if isinstance(value, property)
        }
    ]

    def save(self):
        new_settings = self.get_settings()
        with open("app/shared/CONFIG.json", 'r') as file:
            data = json.load(file)

            for setting in data["settings"]:
                if setting["type"] == self.type:
                    for option in setting.keys():
                        setting[option] = new_settings[0][option]
                    break

        with open("app/shared/CONFIG.json", 'w') as file:
            json.dump(data, file, indent=4)

    def load(self):
        with open("app/shared/CONFIG.json", 'r') as file:
            data = json.load(file)

            for setting in data["settings"]:
                if setting["type"] == self.type:
                    for option in setting.keys():
                        try:
                            setattr(self, option, setting[option]) 
                        except AttributeError:
                            pass
                    break

    def reset():
        user = UserSettings()
        aud = AudioRecordSettings()
        vid = ScreenRecordSettings()
        user.save()
        aud.save()
        vid.save()
                        
class UserSettings(Settings):
    def __init__(self):
        self._type = "user"
        self._deck = "Mitsuke-san"
        self._ANKI_MEDIA_FOLDER = f"C:/Users/{getpass.getuser()}/AppData/Roaming/Anki2/User 1/collection.media/" 

    @property
    def type(self):
        return self._type
    
    @property
    def deck(self):
        return self._deck
    
    @deck.setter
    def deck(self, new):
        # change later
        if type(new) == str:
            self._deck = new

    @property
    def ANKI_MEDIA_FOLDER(self):
        return self._ANKI_MEDIA_FOLDER
    
    @ANKI_MEDIA_FOLDER.setter
    def ANKI_MEDIA_FOLDER(self, new_path):
        if os.path.exists(new_path):
            self._ANKI_MEDIA_FOLDER = new_path
        else: raise FileNotFoundError("Specified file path does not exist")


class AudioRecordSettings(Settings):
    def __init__(self):
        self._type = "audio"
        self._sample_rate = 48000
        self._segment_duration = 30
        self._max_record_length = 86400

    @property
    def type(self):
        return self._type

    @property
    def sample_rate(self):
        return self._sample_rate
    
    @sample_rate.setter
    def sample_rate(self, new):
        rates = [16000, 44100, 48000]
        if new in rates: self._sample_rate = new

    @property
    def segment_duration(self):
        return self._segment_duration
    
    @segment_duration.setter
    def segment_duration(self, new):
        if new >= 10: self._segment_duration = new

    @property
    def max_record_length(self):
        return self._max_record_length
    
    @max_record_length.setter
    def max_record_length(self, new):
        if new >= 10: self._max_record_length = new

class ScreenRecordSettings(Settings):
    def __init__(self):
        self._type = "video"
        self._capture_interval = 1 # sec
        self._mem_limit = 30 # mb

    @property
    def type(self):
        return self._type

    @property
    def capture_interval(self):
        return self._capture_interval
    
    @capture_interval.setter
    def capture_interval(self, new):
        if new >= 1 and new <= 10:
            self._capture_interval = new

    @property
    def mem_limit(self):
        return self._mem_limit
    
    @mem_limit.setter
    def mem_limit(self, new):
        # new will be passed in mb
        if new > 0 and new <= 1024:
            self._mem_limit = new

user_settings = UserSettings()
audio_settings = AudioRecordSettings()
video_settings = ScreenRecordSettings()
user_settings.load()
audio_settings.load()
video_settings.load()
#DEBUG
audio_settings.max_record_length = 120
user_settings.deck = "test"