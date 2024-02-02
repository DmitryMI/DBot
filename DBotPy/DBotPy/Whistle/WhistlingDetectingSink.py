from discord.sinks import Sink
from discord.commands import context
from discord import VoiceChannel
import scipy.fft
import numpy as np
import logging
from discord.ext import commands
import asyncio
import discord


AMPLITURE_THRESHOULD = 100000
FREQUENCY_LEFT = 1500
FREQUENCY_RIGHT = 2000
WHISTLE_PUNISHMENT_SCORE = 3
WHISTLE_PUNISHMENT_DURATION = 10
WHISTLE_PUNISHMENT_SCORE_INC = 0.02
WHISTLE_PUNISHMENT_SCORE_DEC = 0.02


class WhistlingDetectingSink(Sink):
    def __init__(self, bot, ctx, *, filters=None):
        Sink.__init__(self, filters=filters)
        self.ctx = ctx
        self.bot = bot
        self.user_whistle_map = {}
        self.users_punished = []


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

        score_delta = -WHISTLE_PUNISHMENT_SCORE_DEC
        if frequency_sum > AMPLITURE_THRESHOULD:
            score_delta = WHISTLE_PUNISHMENT_SCORE_INC
        
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

    def whistle_updated(self, user, score):

        if score > 0:
            logging.info(f"{user}' score is {score}'")

        if score > WHISTLE_PUNISHMENT_SCORE:
            if user in self.users_punished:
                return

            self.users_punished.append(user)
            self.user_whistle_map[user] = 0

            task =  self.bot.loop.create_task(self.whistler_punishment_handler(self.ctx, user, score))
            task.add_done_callback(lambda task: self.background_tasks.remove(task))
            self.background_tasks.append(task)


    async def whistler_punishment_handler(self, ctx: commands.Context, user, score):

        members = await ctx.guild.query_members(user_ids=[user])
        # print(members)
        if not members:
            logging.error("Failed to load member with id {user}")

        member: discord.Member = members[0]

        await ctx.send(f"Whistler detected: {member.display_name}")

        await member.edit(mute=True)
        await asyncio.sleep(WHISTLE_PUNISHMENT_DURATION)
        self.users_punished.remove(user)

        await member.edit(mute=False)

        await ctx.send(f"Whistler {member.display_name}: punishment ended")