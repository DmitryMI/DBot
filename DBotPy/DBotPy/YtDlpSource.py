import discord
import asyncio
import yt_dlp
import os.path
import os
import logging

class YtDlpSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @staticmethod
    def get_ytdl_options(download_dir):
        ytdl_format_options = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
        }

        if download_dir:
            if download_dir[-1] != os.path.sep:
                download_dir += os.path.sep
            ytdl_format_options['outtmpl'] = download_dir + ytdl_format_options['outtmpl']

        return ytdl_format_options

    @staticmethod
    def get_ffmpeg_options():
        ffmpeg_options = {
            'options': '-vn',
        }
        return ffmpeg_options

    @staticmethod
    def get_dir_size(directory):
        total_size = 0
        for path, dirs, files in os.walk(directory):
           for f in files:
              fp = os.path.join(path, f)
              total_size += os.path.getsize(fp)
        return total_size

    @staticmethod
    def ensure_downloads_size_limits(downloads_dir, max_size):
        
        logging.info("Reducing downloads size")
        list_files = os.listdir(downloads_dir)

        if not list_files or len(list_files) == 1:
            return

        fdict = {}
        for f in list_files:
            fabs = os.path.join(downloads_dir, f)
            fdict[fabs] = os.path.getatime(fabs)

        fdict_sorted = sorted(fdict.items(), key=lambda x:x[1])

        for i in range(len(fdict_sorted)):
            try:
                oldest_file = fdict_sorted[i][0]
                if not os.path.exists(oldest_file):
                    continue

                logging.info(f"Reducing downloads size: {oldest_file} is the oldest file. Removing.")
                os.remove(oldest_file)

                size = YtDlpSource.get_dir_size(downloads_dir)
                if size <= max_size:
                    break

                break

            except Exception as err:
                logging.error(f"Error occured during reduction of downloads size: {str(err)}")


    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, downloads_dir = "Downloads", downloads_max_size = 32 * 1024*1024):

        # Make absolute path
        if downloads_dir:
            downloads_dir = os.path.abspath(downloads_dir)
        else:
            downloads_dir = os.path.abspath(os.getcwd())

        if os.path.normpath(os.path.dirname(__file__)) == os.path.normpath(downloads_dir):
            logging.error(f"Downloads directory {downloads_dir} is invalid!")
            raise Exception(f"Downloads directory {downloads_dir} is invalid!")

        ytdlp_options = YtDlpSource.get_ytdl_options(downloads_dir)
        ffmpeg_options = YtDlpSource.get_ffmpeg_options()

        ytdl = yt_dlp.YoutubeDL(ytdlp_options)

        loop = loop or asyncio.get_event_loop()

        if stream:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            if 'entries' in data:
                data = data['entries'][0]

            url = data['url']
            return cls(discord.FFmpegPCMAudio(url, **ffmpeg_options), data=data)

        else:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=True))

            if downloads_max_size != 0:
                downloads_size = YtDlpSource.get_dir_size(downloads_dir)

                logging.info(f"Current size of downloads: {downloads_size / 1024 / 1024 : 3.2f} Mb. Max size is {downloads_max_size / 1024 / 1024 : 3.2f} Mb")

                if downloads_size >= downloads_max_size:
                    YtDlpSource.ensure_downloads_size_limits(downloads_dir, downloads_max_size)

            if 'entries' in data:
                data = data['entries'][0]

            filename =  ytdl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)