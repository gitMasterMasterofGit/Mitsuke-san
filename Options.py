from enum import Enum
import math

class Options(Enum):

    class Audio():

        def __init__(self):
            self.segment_duration = 30
            self.silence_thresh = 3
            self.max_record_time = math.inf

        @property
        def segment_duration(self):
            return self.segment_duration
        
        @segment_duration.setter
        def segment_duration(self, val):
            if val > 0 and val < 120:
                self.segment_duration = val

        @property
        def silence_thresh(self):
            return self.silence_thresh
        
        @silence_thresh.setter
        def silence_thresh(self, val):
            self.silence_thresh = val
            if val < 0:
                self.silence_thresh = 0

        @property
        def max_record_length(self):
            return self.max_record_length
        
        @max_record_length.setter
        def max_record_length(self, val):
            self.max_record_length = val
            if val < 0:
                self.max_record_length = 0
    
