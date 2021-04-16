"""
@author OriolFilter
@date 16/4/2021
"""

from __future__ import unicode_literals

import youtube_dl
import os
import threading


class ErrLinkInArchive(Exception):
    """
    Error raised up when the link to download is already in the archive file.
    """
    pass


class ErrNoConfig(Exception):
    """
    Error raised up when the manager lacks of a configuration.
    """
    pass


class ThreadingInstancesLessThan0(Exception):
    """
    Error raised up when the minimum instances given is smaller than 1.
    """
    pass


class Colors:
    # https://misc.flogisoft.com/_media/bash/colors_format/256-self.colored.sh-v2.png?w=200&tok=c16bb0
    # https://misc.flogisoft.com/bash/tip_colors_and_formatting#colors2
    def return_color(self, fcolor: int) -> str:
        return f"\033[38;5;{str(fcolor)}m"

    @property
    def WARN(self): return self.return_color(fcolor=160)

    @property
    def INFO(self): return self.return_color(fcolor=227)

    @property
    def SUCCESS(self): return self.return_color(fcolor=82)

    @property
    def LINK(self): return self.return_color(fcolor=81)

    # 57 lila, or 21 darkblue, 27 lighter blue, 81 cyan

    @property
    def DEFAULT(self): return self.return_color(fcolor=253)


class Config:
    def __init__(self, audio_only: bool = False, dl_link: list = None, dl_file: list = None, output: str = None,
                 archive: str = None, threading_instances: int = 0, quiet: bool = None):
        """
        Class store configuration for the manager.
        if none section:
            converts into empty list if not specified.
        if type section:
            forces vars into list.

        if output:
            makes sure there is a output path.
            if path given is a folder adds a default output name.
        else: means no output given so uses the current working directory.

        if archive:
            makes sure there is a output path.
            if path given is a folder adds a default file name.
        else: Pass

        audio_only
        for link:
            appends the links given to the download_links list.
        for file_path:
            appends the lines in the files given to the download_links list.
            (assumes all the lanes are empty or are links to download).

        if threading_instances:
            Raises error if the threading instances are less than 1.
            Updates config if threading specified.
            If threading not specified uses default value (1).
        """
        if not dl_link: dl_link = []
        if not dl_file: dl_file = []
        if type(dl_link) is str:
            dl_link = [dl_link]
        if type(dl_file) is str:
            dl_file = [dl_file]

        file_destination: str = None
        if output and os.path.isdir(output):
            # If folder
            if output[-1] != '/':
                output = f'{output}/'
            else:
                pass
            file_destination = f'{output}%(upload_date)s-%(title)s.%(ext)s'
        elif output:
            # If file
            file_destination = output
        else:
            file_destination = f'{os.getcwd()}/%(upload_date)s-%(title)s.%(ext)s'
        self.output: str = file_destination

        if archive and os.path.isdir(archive):
            # If folder
            if archive[-1] != '/':
                archive = f'{archive}/'
            else:
                pass
            archive_location = f'{archive}.list'
        elif archive:
            # If file
            archive_location = archive
        else:
            archive_location = None

        self.archive = archive_location

        self.audio_only: bool = audio_only

        for link in dl_link:
            self.link_list.append(link)
        for file_path in dl_file:
            with open(file_path, 'r') as file:
                # Assuming each line not empty is a link
                lines = [line for line in file.read().split('\n') if line != '']
                for line in lines:
                    self.link_list.append(line)

        if threading_instances and int(threading_instances) < 1:
            raise ThreadingInstancesLessThan0()
        elif threading_instances:
            self.threading_instances = int(threading_instances)
        else:
            self.threading_instances = self.threading_instances  # Pass
        if quiet is not None:
            self.quiet = quiet

    link_list = []
    output: str = None
    audio_only: bool = False
    archive: str = None
    threading_instances: int = 1
    quiet = False


class Manager:
    """
    Manager used to administrate the downloads.
    """
    thread_list: list = []
    config: Config = None
    colored = Colors()

    def __init__(self, config: Config):
        """
        Stores the given configuration.
        Initializes the
        If configuration exists stores the configuration.
        if doesn't Error from lack of configuration.

        :param config: Contains the manager configuration.
        """

        if config:
            self.config = config
        else:
            raise ErrNoConfig()

    def start_downloads(self):
        """
        if config.archive:
            Opens as append the archive file if given.

        while len(self.config.link_list):
            Generates different threading sessions that each one will start downloading a different link till
            the config.link_list it's empty.
            The ammount of threading sessions it's limited by the configuration, and can't be higher than the
            amount of items in the config.link_list list.

        Closes open archive file at the end.

        :return:
        """

        while len(self.thread_list) < self.config.threading_instances and \
                len(self.thread_list) < len(self.config.link_list):
            try:
                print(
                    f'{self.colored.DEFAULT}[!{self.colored.INFO}Info{self.colored.DEFAULT}] Creating Thread: nº{len(self.thread_list) + 1}')
                t = threading.Thread(target=self.__download_from_list)
                t.daemon = True
                print(
                    f'{self.colored.DEFAULT}[!{self.colored.SUCCESS}Success{self.colored.DEFAULT}] Successfully created thread: '
                    f'nº{len(self.thread_list) + 1}')
                self.thread_list.append(t)
            except:
                print(
                    f'{self.colored.DEFAULT}[!{self.colored.WARN}Warn{self.colored.DEFAULT}] Error creating the thread: '
                    f'nº{len(self.thread_list) + 1}')
        if len(self.thread_list) == self.config.threading_instances:
            print(
                f'{self.colored.DEFAULT}[!{self.colored.SUCCESS}Success{self.colored.DEFAULT}] Successfully created ALL thread ({len(self.thread_list)}/{self.config.threading_instances})')
        elif len(self.thread_list) < self.config.threading_instances and not len(self.thread_list) == 0:
            print(
                f'{self.colored.DEFAULT}[!{self.colored.INFO}Info{self.colored.DEFAULT}] Successfully created part of the desired threads({len(self.thread_list)}/{self.config.threading_instances})')
        else:
            print(
                f'{self.colored.DEFAULT}[!{self.colored.WARN}Warn{self.colored.DEFAULT}] Warning couldn\'t create ANY thread ({len(self.thread_list)}/{self.config.threading_instances})')

        for t in self.thread_list:
            print(
                f'{self.colored.DEFAULT}[!{self.colored.INFO}Info{self.colored.DEFAULT}] Staring Thread: nº{self.thread_list.index(t) + 1}')
            t.start()
            print(
                f'{self.colored.DEFAULT}[!{self.colored.SUCCESS}Success{self.colored.DEFAULT}] Started Thread: nº{self.thread_list.index(t) + 1}')

        [t.join() for t in self.thread_list]

        # while not len(self.thread_list) == 0:
        #     pass
        # Waits threads to finish
        # self.thread_list = [t for t in self.thread_list if t.is_alive()]

    def __download_from_list(self, index: int = 0):
        """
        Uses and removes the first entry from the link_list and proceed to download the file
        In case of already having the url in the archive it shows a info message

        Options, contains the download configuration for youtube-dl

        :return:
        """
        options = {
            'retries': 2,
            'format': ('bestvideo+bestaudio/best', 'bestaudio/best')[self.config.audio_only],
            'recodevideo': ('mp4', None)[self.config.audio_only],
            'outtmpl': self.config.output,
            'quiet': self.config.quiet
        }
        while self.config.link_list:
            link = self.config.link_list.pop(int(index))
            print(
                f'{self.colored.DEFAULT}[!{self.colored.INFO}Info{self.colored.DEFAULT}] Starting download for: {self.colored.LINK}{link}{self.colored.DEFAULT}')
            try:
                self.__download_file(link, options)
                if self.config.archive:
                    self.append_link_to_archive(link)
                    print(
                        f'{self.colored.DEFAULT}[!{self.colored.SUCCESS}Success{self.colored.DEFAULT}] Successfully downloaded: '
                        f'{self.colored.LINK}{link}{self.colored.DEFAULT}')
            except ErrLinkInArchive:
                print(
                    f'{self.colored.DEFAULT}[!{self.colored.WARN}Warn{self.colored.DEFAULT}] Error downloading {self.colored.LINK}{link}{self.colored.DEFAULT}, '
                    f'link already in the archive file')
            except Exception as e:
                print(
                    f'{self.colored.DEFAULT}[!{self.colored.WARN}Warn{self.colored.DEFAULT}] Unknown Error downloading {self.colored.LINK}{link}{self.colored.DEFAULT}\n'
                    f'printing error message {e}')

    def __download_file(self, link: str, options: dict):
        """
        Function used to download the file.
        :param link: url to download.
        :param options: options, contains the download configuration for youtube-dl.
        :return:
        """
        if link in self.archive_records:
            raise ErrLinkInArchive()
        else:
            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([link])

    @property
    def archive_records(self) -> list:
        """
        Returns a list that contains the lines of the archive file.
        In case of not having archive configured, it returns a empty list.
        Used to check if a link it's been downloaded already, checking if the link exist inside of the list.

        :return: list
        """
        if self.config.archive:
            archive_file = None
            try:
                archive_file = open(self.config.archive, "r+")
            except FileNotFoundError:
                file = open(self.config.archive, "w")
                file.close()
                archive_file = open(self.config.archive, "r+")
            finally:
                link_list = archive_file.read().split('\n')
                archive_file.close()
                return link_list
        else:
            return []

    def append_link_to_archive(self, link: str):
        """
        Append the given link to the archive file.
        :param link: link to append to he archive file.
        :return:
        """
        archive_file = open(self.config.archive, "a+")
        archive_file.write(f'{link}\n')
        archive_file.close()
