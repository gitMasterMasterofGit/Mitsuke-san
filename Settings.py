from enum import Enum
from abc import ABC, abstractmethod
import os
import math
import inspect
import json

class Settings():
    def get_settings(settings_obj):
        return [{
            name: getattr(settings_obj, name)
            for name, value in inspect.getmembers(type(settings_obj))
            if isinstance(value, property)
        }
    ]

class UserSettings(Settings):
    def __init__(self):
        self._ANKI_MEDIA_FOLDER = ""

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
        self._sample_rate = 48000
        self._segment_duration = 30
        self._max_record_length = math.inf

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
        self._capture_interval = 1

    @property
    def capture_interval(self):
        return self._capture_interval
    
    @capture_interval.setter
    def capture_interval(self, new):
        if new >= 1 and new <= 10:
            self._capture_interval = new


set = UserSettings()

print(Settings.get_settings(set))