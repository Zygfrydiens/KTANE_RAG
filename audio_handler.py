import pyaudio
import wave
import os
import math
import struct
import time

Threshold = 10

SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
swidth = 2
Max_Seconds = 10
TimeoutSignal=((RATE / chunk * Max_Seconds) + 2)
silence = True
FileNameTmp = './12-33.wav'
Time=0
all =[]
TIMEOUT_LENGTH = 1
f_name_directory= "./"

def rms(frame):
    count = len(frame) / swidth
    format = "%dh" % (count)
    shorts = struct.unpack(format, frame)

    sum_squares = 0.0
    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n * n
    rms = math.pow(sum_squares / count, 0.5)

    return rms * 1000



class Recorder:
    def __init__(self, callback_on_record=None, timeout_seconds=1, output_dir="./audio/",
                 audio_level_average_frame_window=3):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  frames_per_buffer=chunk)
        self.timeout_seconds = timeout_seconds
        self.output_dir = output_dir
        self.clip_number = 1
        self.callback_on_record = callback_on_record
        self.audio_level_average_frame_window = audio_level_average_frame_window

    def _wait_for_sound(self):
        while True:
            input = self.stream.read(chunk)
            rms_val = rms(input)
            if rms_val > Threshold:
                return input

    def get_recording_filename(self):
        return os.path.join(self.output_dir, "%s.wav"%self.clip_number)
    def _record_until_silent(self, seed_data):
        audio_data = []
        audio_levels = []
        audio_data.append(seed_data)
        silent_start = time.time()
        while time.time() - silent_start < self.timeout_seconds:
            data = self.stream.read(chunk)
            level = rms(data)
            audio_levels.append(level)
            window = min(self.audio_level_average_frame_window, len(audio_levels))
            avg = sum(audio_levels[-window:])/window
            if avg >= Threshold:
                silent_start = time.time()
            audio_data.append(data)
        print("saving recording")
        self.write(b''.join(audio_data))

    def write(self, recording):
        filename = self.get_recording_filename()
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()

    def run(self):
        while True:
            print("...listening for sounds")
            seed_data = self._wait_for_sound()
            print("recording audio clip")
            self._record_until_silent(seed_data)
            self.clip_number += 1

    def listen_and_record(self):
        print("...listening for sounds")
        seed_data = self._wait_for_sound()
        print("recording audio clip")
        self._record_until_silent(seed_data)
        if self.callback_on_record != None:
            self.callback_on_record(self.callback_on_record)
        filename = self.get_recording_filename()
        self.clip_number += 1
        return filename



if __name__ == "__main__":
    recorder = Recorder(None)
    recorder.run()