from discord.sinks import Sink
from discord.commands import context
from discord import VoiceChannel
import scipy.fft
import numpy as np

AMPLITURE_THRESHOULD = 100000
FREQUENCY_LEFT = 1500
FREQUENCY_RIGHT = 2000

class WhistlingDetectingSink(Sink):
    def __init__(self, ctx, whistler_updated_callback ,*, filters=None):
        Sink.__init__(self, filters=filters)
        self.ctx = ctx
        self.user_whistle_map = {}
        self.whistler_updated_callback = whistler_updated_callback

    def format_audio(self, audio):
        if self.vc.recording:
            raise Exception(
                "Audio may only be formatted after recording is finished."
            )
        

    def write(self, pcm_bytes, user):
        # Sink.write(self, pcm_bytes, user)

        pcm_data = np.frombuffer(pcm_bytes, np.int16)

        fft_result = scipy.fft.fft(pcm_data)

        if not fft_result.any():
            return

        # df = fs / BL
        # df = self.vc.SAMPLING_RATE / self.vc.SAMPLES_PER_FRAME
        frequency_step = self.vc.decoder.SAMPLING_RATE / self.vc.decoder.SAMPLES_PER_FRAME

        frequency_cutoff_left = round(FREQUENCY_LEFT / frequency_step)
        frequency_cutoff_right = round(FREQUENCY_RIGHT / frequency_step)

        frequency_sum = 0

        for i in range(frequency_cutoff_left, frequency_cutoff_right):
            frequency_sum += abs(fft_result[i].real)

        # print(f"Audio packet decoded: {user}, high_frequency_sum = {frequency_sum}")

        score_delta = -0.02
        if frequency_sum > AMPLITURE_THRESHOULD:
            score_delta = 0.02
        
        if user in self.user_whistle_map:
            score = self.user_whistle_map[user]
            score += score_delta
            if score < 0:
                score = 0
            self.user_whistle_map[user] = score
        else:
            score = 0
            self.user_whistle_map[user] = score

        self.whistler_updated_callback(self, user, score)
