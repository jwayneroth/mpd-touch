

"""
==================================================================
**mpd_client.py**: controlling and monitoring mpd via python-mpd2.
==================================================================
"""

import sys, pygame
import time
import subprocess
import os
import glob
import random

#import python_mpd2
from PersistentMPDClient import PersistentMPDClient
from collections import deque
from .. mutagen import File
from .. import pygameui.callback as callback

import logging
logger = logging.getLogger('fmu_logger')

MPD_TYPE_ARTIST = 'artist'
MPD_TYPE_ALBUM = 'album'
MPD_TYPE_SONGS = 'title'

TEMP_PLAYLIST_NAME = '_pi-jukebox_temp'

reload(sys)
sys.setdefaultencoding('utf8')

class MPDNowPlaying(object):
    """ Song information
    """
    def __init__(self):
        self.playing_type = ''
        self.__now_playing = None
        self.title = ""  # Currently playing song name
        self.artist = ""  # Currently playing artist
        self.name = ""  # Currently playing radio name
        self.album = ""  # Album the currently playing song is on
        self.file = ""  # File with path relative to MPD music directory
        self.__time_current_sec = 0  # Currently playing song time (seconds)
        self.time_current = ""  # Currently playing song time (string format)
        self.__time_total_sec = 0  # Currently playing song duration (seconds)
        self.time_total = ""  # Currently playing song duration (string format)
        self.time_percentage = 0    # Currently playing song time as a percentage of the song duration
        self.music_directory = "/var/lib/mpd/music/"

    def now_playing_set(self, now_playing=None):

        if now_playing is not None:

            try:
                self.file = now_playing['file']
                if self.file[:7] == "http://":
                    self.playing_type = 'radio'
                else:
                    self.playing_type = 'file'
            except KeyError:
                self.file = ''
                self.playing_type = 'file'
                return

            if 'title' in now_playing:
                self.title = now_playing['title']  # Song title of current song
            else:
                self.title = os.path.splitext(os.path.basename(now_playing['file']))[0]

            if self.playing_type == 'file':

                if 'artist' in now_playing:
                    self.artist = now_playing['artist']  # Artist of current song
                else:
                    self.artist = ""

                if 'album' in now_playing:
                    self.album = now_playing['album']  # Album the current song is on
                else:
                    self.album = ""

                current_total = self.str_to_float(now_playing['time'])
                self.__time_total_sec = current_total
                self.time_total = self.make_time_string(current_total)  # Total time current

            elif self.playing_type == 'radio':

                if 'name' in now_playing:
                    self.album = now_playing['name']  # The radio station name
                else:
                    self.album = ""

                self.artist = ""

        elif now_playing is None:  # Changed to no current song
            self.__now_playing = None
            self.title = ""
            self.artist = ""
            self.album = ""
            self.name = ""
            self.file = ""
            self.time_percentage = 0
            self.__time_total_sec = 0
            self.time_total = self.make_time_string(0)  # Total time current

    def current_time_set(self, seconds):
        if self.__time_current_sec != seconds:  # Playing time current
            self.__time_current_sec = seconds
            self.time_current = self.make_time_string(seconds)
            if self.playing_type != 'radio':
                self.time_percentage = int(self.__time_current_sec / self.__time_total_sec * 100)
            else:
                self.time_percentage = 0
            return True
        else:
            return False

    def make_time_string(self, seconds):
        minutes = int(seconds / 60)
        seconds_left = int(round(seconds - (minutes * 60), 0))
        time_string = str(minutes) + ':'
        seconds_string = ''
        if seconds_left < 10:
            seconds_string = '0' + str(seconds_left)
        else:
            seconds_string = str(seconds_left)
        time_string += seconds_string
        return time_string

    def str_to_float(self, s):
        try:
            return float(s)
        except ValueError:
            return float(0)


class MPDController(object):
    """ Controls playback and volume
    """

    def __init__(self):
        self.host = 'localhost'
        self.port = 6600
        self.mpd_client = PersistentMPDClient(None, self.host, self.port); #python_mpd2.MPDClient()
        self.update_interval = 1800  # Interval between mpc status update calls (milliseconds)
        self.volume = 0  # Playback volume
        self.playlist_current = []  # Current playlist song title
        self.repeat = False         #
        self.random = False
        self.single = False
        self.consume = False
        self.updating_library = False
        self.__radio_mode = None
        self.now_playing = MPDNowPlaying()
        self.events = deque([])  # Queue of mpd events
        # Database search results
        self.searching_artist = ""  # Search path user goes through
        self.searching_album = ""
        self.list_albums = []
        self.list_artists = []
        self.list_songs = []
        self.list_query_results = []

        self.__music_directory = ""
        self.__song_status = {'album':'','artist':'','file':''}  # Dictionary containing currently playing song info
        self.__now_playing_changed = False
        self.__player_control = ''  # Indicates whether mpd is playing, pausing or has stopped playing music
        self.__muted = False          # Indicates whether muted
        self.__playlist_current_playing_index = 0
        self.__last_update_time = 0   # For checking last update time (milliseconds)
        self.__status = {}  # mps's current status output

        self.on_album_changed = callback.Signal()

    def dict_to_string(self, dict):
        print ', '.join("%s=%r" % (key,val) for (key,val) in dict.iteritems())

    def connect(self):
        """ Connects to mpd server.

            :return: Boolean indicating if successfully connected to mpd server.
        """

        self.mpd_client.connect(self.host, self.port)
        """
        try:
            self.mpd_client.connect(self.host, self.port)
        except Exception:
            return False
        """

        # Retrieve lists
        #self.artists_get()
        #self.albums_get()

        #try:
        #    self.songs_get()
        #except Exception:
        #    pass

        #self.__starts_with_radio()

        return True

    def __starts_with_radio(self):

        was_playing = False  # Indicates whether mpd was playing on start
        now_playing = MPDNowPlaying()

        #try:
        now_playing.now_playing_set(self.mpd_client.currentsong())  # Get currenly plating info
        #except python_mpd2.ConnectionError:
        #    self.mpd_client.connect(self.host, self.port)
        #    now_playing.now_playing_set(self.mpd_client.currentsong())

        if self.player_control_get() == 'play':
            was_playing = True

        if now_playing.playing_type == 'radio':

            logger.debug('playing radio')

            station_URL = now_playing.file  # If now playing is radio station temporarily store
            self.playlist_current_clear()  # Clear playlist

            try:
                self.__radio_mode = False
                self.mpd_client.load(TEMP_PLAYLIST_NAME)  # Try to load previously temporarily stored playlist
                self.playlist_current_get()  # Set playlist
                logger.debug('got playlist')
            except Exception:
                logger.debug('failed to get playlist')
                pass

            self.__radio_mode = True  # Turn on radio mode
            self.mpd_client.clear()  # Clear playlist
            self.mpd_client.addid(station_URL)  # Reload station

            if was_playing:
                logger.debug('was playing')
                self.mpd_client.play(0)  # Resume playing

    def disconnect(self):
        """ Closes the connection to the mpd server. """
        self.mpd_client.close()
        self.mpd_client.disconnect()

    def music_directory_set(self, path):
        self.now_playing.music_directory = path
        self.__music_directory = path

    """
        __parse_mpc_status
            Parses the mpd status and fills mpd event queue
            return: Boolean indicating if the status was changed
    """
    def __parse_mpc_status(self):

        #logger.debug('__parse_mpc_status')

        status_change = False

        # get song status
        song_status = self.mpd_client.currentsong()

        """
        try:
            song_status = self.mpd_client.currentsong()
        except python_mpd2.ConnectionError:
            self.mpd_client.connect(self.host, self.port)
            song_status = self.mpd_client.currentsong()
        except Exception:
            print 'status exception'
            return False
        """

        # any changes or first run
        if self.__song_status != song_status and len(song_status) > 0:

            #self.dict_to_string(song_status)

            # update now_playing properties
            self.now_playing.now_playing_set( song_status )

            if self.now_playing.playing_type == 'radio':
                if self.__radio_mode != True:
                    self.__radio_mode = True
                    status_change = True
                    print 'mpd_client::__parse_mpc_status: \t radio on'
                    self.events.append('radio_mode_on')
            else:
                if self.__radio_mode != False:
                    self.__radio_mode = False
                    status_change = True
                    print 'mpd_client::__parse_mpc_status: \t radio off'
                    self.events.append('radio_mode_off')

            #self.__now_playing_changed = True

            if 'album' in song_status:

                if 'album' in self.__song_status:

                    if song_status['album'] != self.__song_status['album']:
                        print 'mpd_client::__parse_mpc_status: \t album_change'
                        self.events.append('album_change')
                        status_change = True

                else:
                    print 'mpd_client::__parse_mpc_status: \t album_change'
                    self.events.append('album_change')
                    status_change = True

            else:
                if self.now_playing.album != '':
                    print 'mpd_client::__parse_mpc_status: \t album_change'
                    self.events.append('album_change')
                    status_change = True

            if 'title' in song_status:

                if 'title' in self.__song_status:

                    if song_status['title'] != self.__song_status['title']:
                        print 'mpd_client::__parse_mpc_status: \t title change'
                        self.events.append('title_change')
                        status_change = True

                else:
                    print 'mpd_client::__parse_mpc_status: \t title change'
                    self.events.append('title_change')
                    status_change = True

            else:
                if 'file' in self.__song_status and self.now_playing.title != os.path.splitext(os.path.basename(self.__song_status['file']))[0]:
                    print 'mpd_client::__parse_mpc_status: \t title change'
                    self.events.append('title_change')
                    status_change = True
                else:
                    pass

            #self.events.append('playing_time_percentage')

            self.__song_status = song_status

        # get general status
        status = self.mpd_client.status()
        """
        try:
            status = self.mpd_client.status()
        except Exception:
            print 'status exception'
            return status_change
        """

        if self.__status == status:
            #print 'no status change'
            return status_change

        # print self.dict_to_string(status)

        self.__status = status

        self.playback_options_get(status)

        if self.volume != int(status['volume']):  # Current volume

            print '\t volume: ' + str(self.volume) + '\t new: ' + status['volume']

            self.volume = int(status['volume'])
            self.events.append('volume')
            self.__muted = self.volume == 0

            status_change = True

        if self.__player_control != status['state']:
            self.__player_control = status['state']
            self.events.append('player_control')

            print 'player_control change: ' + str(status['state'])

            status_change = True

        if self.__player_control != 'stop':

            if self.__playlist_current_playing_index != int(status['song']):  # Current playlist index
                self.__playlist_current_playing_index = int(status['song'])

                #self.events.append('playing_index')
                #status_change = True

            #if self.now_playing.current_time_set(self.str_to_float(status['elapsed'])):
                #self.events.append('time_elapsed')
                #status_change = True

        else:

            if self.__playlist_current_playing_index != -1:
                self.__playlist_current_playing_index = -1

                #self.events.append('playing_index')
                #status_change = True

                #if self.now_playing.current_time_set(0):
                    #self.events.append('time_elapsed')

        return status_change

    def playback_options_get(self, status):
        if self.repeat != status['repeat'] == '1':
            self.repeat = status['repeat'] == '1'
            self.events.append('repeat')
        if self.random != status['random'] == '1':
            self.random = status['random'] == '1'
            self.events.append('random')
        if self.single != status['single'] == '1':
            self.single = status['single'] == '1'
            self.events.append('single')
        if self.consume != status['consume'] == '1':
            self.consume = status['consume'] == '1'
            self.events.append('consume')

    def str_to_float(self, s):
        try:
            return float(s)
        except ValueError:
            return float(0)

    def status_get(self):
        """ Updates mpc data, returns True when status data is updated. Wait at
            least 'update_interval' milliseconds before updating mpc status data.

            :return: Returns boolean whether updated or not.
        """
        #print 'mpd_client::status_get'
        gt = pygame.time.get_ticks()

        time_elapsed = gt - self.__last_update_time

        if gt > self.update_interval and time_elapsed < self.update_interval:
            return False

        self.__last_update_time = gt

        return self.__parse_mpc_status()   # Parse mpc status output

    def current_song_changed(self):
        if self.__now_playing_changed:
            self.__now_playing_changed = False
            return True
        else:
            return False

    def player_control_set(self, play_status):
        """ Controls playback

            :param play_status: Playback action ['play', 'pause', 'stop', 'next', 'previous'].
        """
        if play_status == 'play':
            if self.__player_control == 'pause':
                self.mpd_client.pause(0)
            else:
                self.mpd_client.play()
        elif play_status == 'pause':
            self.mpd_client.pause(1)
        elif play_status == 'stop':
            self.mpd_client.stop()
        elif play_status == 'next':
            self.mpd_client.next()
        elif play_status == 'previous':
            self.mpd_client.previous()

    def player_control_get(self):
        """ :return: Current playback mode. """
        self.status_get()
        return self.__player_control

    def play_playlist_item(self, index):
        """ Starts playing in playlist on item.

            :param index: Playlist item index
        """
        if self.__radio_mode:
            self.__radio_mode_set(False)
        #try:
            self.mpd_client.play(index - 1)
        #except python_mpd2.ConnectionError:
        #    self.mpd_client.connect(self.host, self.port)
        #    self.mpd_client.play(index - 1)

    def volume_set(self, percentage):
        """ Sets volume in absolute percentage.

            :param percentage: Percentage at which volume should be set.
        """
        if percentage < 0 or percentage > 100: return
        #try:
        self.mpd_client.setvol(percentage)
        #except python_mpd2.ConnectionError:
        #    self.mpd_client.connect(self.host, self.port)
        #    self.mpd_client.setvol(percentage)
        self.volume = percentage

    def volume_set_relative(self, percentage):
        """ Sets volume relatively to current volume.

            :param percentage: Percentage point volume increase.
        """
        if self.volume + percentage < 0:
            self.volume = 0
        elif self.volume + percentage > 100:
            self.volume = 100
        else:
            self.volume += percentage
        #try:
        self.mpd_client.setvol(self.volume)
        #except python_mpd2.ConnectionError:
        #    self.mpd_client.connect(self.host, self.port)
        #    self.mpd_client.setvol(self.volume)

    def volume_mute_switch(self):
        """ Switches volume muting on or off. """
        if self.__muted:
            #try:
            self.mpd_client.setvol(self.volume)
            #except python_mpd2.ConnectionError:
            #    self.mpd_client.connect(self.host, self.port)
            #    self.mpd_client.setvol(self.volume)
            self.__muted = False
        else:
            #try:
            self.mpd_client.setvol(0)
            #except python_mpd2.ConnectionError:
            #    self.mpd_client.connect(self.host, self.port)
            #    self.mpd_client.setvol(0)
            self.__muted = True

    def volume_mute_get(self):
        return self.__muted

    def random_switch(self):
        """ Switches random playing on or off. """
        self.random = not self.random
        if self.random:
            self.mpd_client.random(1)
        else:
            self.mpd_client.random(0)

    def repeat_switch(self):
        """ Switches repeat playing on or off. """
        self.repeat = not self.repeat
        if self.repeat:
            self.mpd_client.repeat(1)
        else:
            self.mpd_client.repeat(0)

    def single_switch(self):
        self.single = not self.single
        if self.consume:
            self.mpd_client.single(1)
        else:
            self.mpd_client.single(0)

    def consume_switch(self):
        """ Switches playlist consuming on or off. """
        self.consume = not self.consume
        if self.consume:
            self.mpd_client.consume(1)
        else:
            self.mpd_client.consume(0)

    def playlist_current_get(self):
        if not self.__radio_mode:
            self.playlist_current = []
            playlist_info = []
            track_no = 0
            #try:
            playlist_info = self.mpd_client.playlistinfo()
            #except python_mpd2.ConnectionError:
            #    self.mpd_client.connect(self.host, self.port)
            #    playlist_info = self.mpd_client.playlistinfo()
            for i in playlist_info:
                track_no += 1
                if 'title' in i:
                    self.playlist_current.append(str(track_no) + '. ' + i['title'])
                else:
                    self.playlist_current.append(str(track_no) + '. ' + os.path.splitext(os.path.basename(i['file']))[0])
        return self.playlist_current

    def playlist_current_playing_index_get(self):
        """
        :return: The track number playing on the current playlist.
        """
        if self.__radio_mode:
            return -1
        else:
            self.status_get()
            return self.__playlist_current_playing_index

    def playlist_current_playing_index_set(self, index):
        """ Starts playing item _index_ of the current playlist.

        :param index: The track number to be played
        :return: The current playing index
        """
        if self.__radio_mode:
            self.__radio_mode_set(False)
        if index > 0 and index <= self.playlist_current_count():
            #try:
            self.mpd_client.playid(index)
            #except python_mpd2.ConnectionError:
            #    self.mpd_client.connect(self.host, self.port)
            #    self.mpd_client.playid(index)
            self.__playlist_current_playing_index = index
        return self.__playlist_current_playing_index

    def playlist_current_count(self):
        """
        :return: The number of items in the current playlist
        """
        return len(self.playlist_current)

    def playlist_current_clear(self):
        """ Removes everything from the current playlist """
        #try:
        self.mpd_client.clear()
        #except python_mpd2.ConnectionError:
        #    self.mpd_client.connect(self.host, self.port)
        #    self.mpd_client.clear()
        if not self.__radio_mode:
            self.playlist_current = []

    def library_update(self):
        """ Updates the mpd library """
        #try:
        self.mpd_client.update()
        #except python_mpd2.ConnectionError:
        #    self.mpd_client.connect(self.host, self.port)
        #    self.mpd_client.update()

    def library_rescan(self):
        """ Rebuild library. """
        #try:
        self.mpd_client.rescan()
        #except:
        #    self.mpd_client.connect(self.host, self.port)
        #    self.mpd_client.rescan()

    def __search(self, tag_type):
        """ Searches all entries of a certain type.

        :param tag_type: ["artist"s, "album"s, song"title"s]
        :return: A list with search results.
        """
        #try:
        self.list_query_results = self.mpd_client.list(tag_type)
        #except:
        #    self.mpd_client.connect(self.host, self.port)
        #    self.list_query_results = self.mpd_client.list(tag_type)
        self.list_query_results.sort()
        return self.list_query_results

    def __search_first_letter(self, tag_type, first_letter):
        """ Searches all entries of a certain type matching a first letter

        :param tag_type: ["artist"s, "album"s, song"title"s]
        :param first_letter: The first letter
        :return: A list with search results.
        """
        temp_results = []
        for i in self.list_query_results:
            if i[:1].upper() == first_letter.upper():
                temp_results.append(i)
        self.list_query_results = temp_results
        return self.list_query_results

    def __search_partial(self, tag_type, part):
        """ Searches all entries of a certain type partially matching search string.

        :param tag_type: ["artist"s, "album"s, song"title"s]
        :param part: Search string.
        :return: A list with search results.
        """
        all_results = []
        #try:
        all_results = self.mpd_client.list(tag_type)
        #except python_mpd2.ConnectionError:
        #    self.mpd_client.connect(self.host, self.port)
        #    all_results = self.mpd_client.list(tag_type)
        self.list_query_results = []
        all_results.sort()
        for i in all_results:
            result = i.upper()
            if result.find(part.upper()) > -1:
                self.list_query_results.append(i)
        return self.list_query_results

    def __search_of_type(self, type_result, type_filter, name_filter):
        """ Searching one type depending on another type (very clear description isn't it?)

        :param type_result: The type of result-set generated ["artist"s, "album"s, song"title"s]
        :param type_filter: The type of filter used ["artist"s, "album"s, song"title"s]
        :param name_filter: The name used to filter
        :return:
        """
        if self.searching_artist == "" and self.searching_album == "":
            #try:
            self.list_query_results = self.mpd_client.list(type_result, type_filter, name_filter)
            #except python_mpd2.ConnectionError:
            #    self.mpd_client.connect(self.host, self.port)
            #    self.list_query_results = self.mpd_client.list(type_result, type_filter, name_filter)
        elif self.searching_artist != "" and self.searching_album == "":
            #try:
            self.list_query_results = self.mpd_client.list(type_result,
                                                           'artist',
                                                           self.searching_artist,
                                                           type_filter,
                                                           name_filter)
            #except python_mpd2.ConnectionError:
            #    self.mpd_client.connect(self.host, self.port)
            #    self.list_query_results = self.mpd_client.list(type_result, 'artist', self.searching_artist,
            #                                                  type_filter,
            #                                                   name_filter)
        elif self.searching_artist == "" and self.searching_album != "":
            #try:
            self.list_query_results = self.mpd_client.list(type_result, 'album', self.searching_album, type_filter,
                                                               name_filter)
            #except python_mpd2.ConnectionError:
            #    self.mpd_client.connect(self.host, self.port)
            #    self.list_query_results = self.mpd_client.list(type_result, 'album', self.searching_album, type_filter,
            #                                                  name_filter)
        elif self.searching_artist != "" and self.searching_album != "":
            #try:
            self.list_query_results = self.mpd_client.list(type_result, 'artist', self.searching_artist, 'album',
                                                               self.searching_album, type_filter, name_filter)
            #except python_mpd2.ConnectionError:
            #    self.mpd_client.connect(self.host, self.port)
            #    self.list_query_results = self.mpd_client.list(type_result, 'artist', self.searching_artist, 'album',
            #                                                  self.searching_album, type_filter, name_filter)
        self.list_query_results.sort()
        return self.list_query_results

    def artists_get(self, part=None, only_start=True):
        """ Retrieves all artist names or matching by first letter(s) or partial search string.

        :param part: Search string
        :param only_start: Only search as first letter(s).
        :return: A list of matching artist names.
        """
        self.searching_artist = ""
        self.searching_album = ""
        if part is None:
            if len(self.list_artists) == 0:
                self.list_artists = self.__search('artist')
            return self.list_artists
        elif only_start:
            self.list_query_results = self.__search_first_letter('artist', part)
        else:
            self.list_query_results = self.__search_partial('artist', part)
        return self.list_query_results

    def albums_get(self, part=None, only_start=True):
        """ Retrieves all album titles or matching by first letter(s) or partial search string.

        :param part: Search string.
        :param only_start: Only search as first letter(s).
        :return: A list of matching album titles.
        """
        self.searching_artist = ""
        self.searching_album = ""
        if part is None:
            if len(self.list_albums) == 0:
                self.list_albums = self.__search('album')
            return self.list_albums
        elif only_start:
            self.list_query_results = self.__search_first_letter('album', part)
        else:
            self.list_query_results = self.__search_partial('album', part)
        return self.list_query_results

    def songs_get(self, part=None, only_start=True):
        """ Retrieves all song titles or matching by first letter(s) or partial search string

        :param part: Search string
        :param only_start: Only search as first letter(s)
        :return: A list of matching song titles
        """
        self.searching_artist = ""
        self.searching_album = ""
        if part is None:
            if len(self.list_songs) == 0:
                self.list_songs = self.__search('title')
            return self.list_songs
        elif only_start:
            self.list_query_results = self.__search_first_letter('title', part)
        else:
            self.list_query_results = self.__search_partial('title', part)
        return self.list_query_results

    def artist_albums_get(self, artist_name):
        """ Retrieves artist's albums.

        :param artist_name: The name of the artist to retrieve the albums of.
        :return: A list of album titles.
        """
        self.searching_artist = artist_name
        return self.__search_of_type('album', 'artist', artist_name)

    def artist_songs_get(self, artist_name):
        """ Retrieves artist's songs.

        :param artist_name: The name of the artist to retrieve the songs of.
        :return: A list of song titles
        """
        self.searching_artist = artist_name
        return self.__search_of_type('title', 'artist', artist_name)

    def album_songs_get(self, album_name):
        """ Retrieves all song titles of an album.

        :param album_name: The name of the album
        :return: A list of song titles
        """
        self.searching_album = album_name
        return self.__search_of_type('title', 'album', album_name)

    def playlists_get(self, first_letter=None):
        """ Retrieves all playlists or those matching the first letter

        :param first_letter: Letter
        :return: A list of playlist names
        """
        result_list = []
        all_playlists = []
        #try:
        all_playlists = self.mpd_client.listplaylists()
        #except python_mpd2.ConnectionError:
        #    self.mpd_client.connect(self.host, self.port)
        #    all_playlists = self.mpd_client.listplaylists()
        if first_letter is None:
            for playlist in all_playlists:
                result_list.append(playlist['playlist'])
        else:
            for playlist in all_playlists:
                if playlist['playlist'][:1].upper() == first_letter.upper():
                    result_list.append(playlist['playlist'])
        return result_list

    def directory_list(self, path="", first_letter=None):
        """ Retrieves the contents of a directory
        :param path: Subpath
        :param first_letter: Retrieve all directories starting with letter
        """
        result_list = []
        directory_list = []
        path_entries = None
        #try:
        path_entries = self.mpd_client.lsinfo(path)
        #except python_mpd2.ConnectionError:
        #    self.mpd_client.connect(self.host, self.port)
        #    path_entries = self.mpd_client.lsinfo(path)
        for entry in path_entries:
            if 'directory' in entry:
                directory_list.append(('directory', entry['directory']))
            elif 'file' in entry:
                directory_list.append(('file', entry['file']))

        if first_letter is None:
            result_list = directory_list
        else:
            for entry in directory_list:
                if 'directory' in entry:
                    if entry['directory'][:1].upper() == first_letter.upper():
                        result_list.append(('directory', entry['directory']))
                elif 'file' in entry:
                    if entry['file'][:1].upper() == first_letter.upper():
                        result_list.append(('file', os.path.basename(entry['file'])))
        return result_list

    def directory_songs_get(self, path=""):
        """ Gets all files in the directory and from the directories below
        :param path: Directory which is searched recursively for files
        :return: list with files
        """
        contents_list = self.__directory_recurse_get(path)
        songs_list = []
        for entry in contents_list:
            if 'file' in entry:
                songs_list.append(entry)
        return songs_list

    def __directory_recurse_get(self, path=""):
        """
        :param path: Recurses through directories
        :return:
        """
        content_list = []
        #try:
        content_list = self.mpd_client.lsinfo(path)
        #except python_mpd2.ConnectionError:
        #    self.mpd_client.connect(self.host, self.port)
        #    content_list = self.mpd_client.lsinfo(path)
        for entry in content_list:
            if 'directory' in entry:
                content_list += self.__directory_recurse_get(entry['directory'])
                # elif 'file' in entry:
            #                content_list.append(('file', os.path.basename(entry['file'])))
        return content_list


    def playlist_add(self, tag_type, tag_name, play=False, clear_playlist=False):
        """ Adds songs to the current playlist

        :param tag_type: Kind of add you want to do ["artist", "album", song"title"].
        :param tag_name: The name of the tag_type.
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        if self.__radio_mode:
            self.__radio_mode_set(False)
        if clear_playlist:
            self.playlist_current_clear()
        i = self.playlist_current_count()
        if self.searching_artist == "" and self.searching_album == "":
            self.mpd_client.findadd(tag_type, tag_name)
        elif self.searching_artist != "" and self.searching_album == "":
            self.mpd_client.findadd('artist', self.searching_artist, tag_type, tag_name)
        elif self.searching_artist == "" and self.searching_album != "":
            self.mpd_client.findadd('album', self.searching_album, tag_type, tag_name)
        elif self.searching_artist != "" and self.searching_album != "":
            self.mpd_client.findadd('artist', self.searching_artist, 'album', self.searching_album, tag_type, tag_name)
        if play:
            self.play_playlist_item(i + 1)

    def playlist_add_artist(self, artist_name, play=False, clear_playlist=False):
        """ Adds all artist's songs to the current playlist

        :param artist_name: The name of the artist.
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        self.playlist_add('artist', artist_name, play, clear_playlist)

    def playlist_add_album(self, album_name, play=False, clear_playlist=False):
        """ Adds all album's songs to the current playlist

        :param album_name: The album name
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """

        self.playlist_add('album', album_name, play, clear_playlist)

    def playlist_add_song(self, song_name, play=False, clear_playlist=False):
        """ Adds a song to the current playlist

        :param song_name: The song's name
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        self.playlist_add('title', song_name, play, clear_playlist)

    def playlist_add_playlist(self, playlist_name, play=False, clear_playlist=False):
        """ Adds a playlist to the current playlist

        :param playlist_name: The playlist's name
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        if self.__radio_mode:
            self.__radio_mode_set(False)
        if clear_playlist:
            self.playlist_current_clear()
        i = self.playlist_current_count()
        #try:
        self.mpd_client.load(playlist_name)
        #except python_mpd2.ConnectionError:
        #    self.mpd_client.connect(self.host, self.port)
        #    self.mpd_client.load(playlist_name)
        if play:
            self.play_playlist_item(i + 1)

    def playlist_add_file(self, uri, play=False, clear_playlist=False):
        """ Adds file to the playlist
        :param uri: The file including path
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        if self.__radio_mode:
            self.__radio_mode_set(False)
        if clear_playlist:
            self.playlist_current_clear()
        i = self.playlist_current_count()
        #try:
        self.mpd_client.addid(uri)
        #except python_mpd2.ConnectionError:
        #    self.mpd_client.connect(self.host, self.port)
        #    self.mpd_client.addid(uri)
        if play:
            self.play_playlist_item(i + 1)

    def playlist_add_directory(self, path, play=False, clear_playlist=False):
        """ Adds all songs from the directory recursively to the playlist
        :param path: Directory
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        if self.__radio_mode:
            self.__radio_mode_set(False)
        if clear_playlist:
            self.playlist_current_clear()
        i = self.playlist_current_count()
        songs = self.directory_songs_get(path)
        for song in songs:
            #try:
            self.mpd_client.addid(song['file'])
            #except python_mpd2.ConnectionError:
            #    self.mpd_client.connect(self.host, self.port)
            #    self.mpd_client.addid(song['file'])
        if play:
            self.play_playlist_item(i + 1)

    def album_set(self,album):
        pass

    def radio_station_start(self, station_URL):
        self.playlist_current_get()
        self.__radio_mode = True
        #try:
        self.mpd_client.rm(TEMP_PLAYLIST_NAME)
        #except:
        #    pass
        self.mpd_client.save(TEMP_PLAYLIST_NAME)
        self.playlist_current_clear()
        #try:
        self.mpd_client.addid(station_URL)
        #except python_mpd2.ConnectionError:
        #    self.mpd_client.connect(self.host, self.port)
        #    self.mpd_client.addid(station_URL)
        self.mpd_client.play(0)

    def radio_mode_get(self):
        return self.__radio_mode

    def __radio_mode_set(self, radio_mode):
        if self.__radio_mode == True and radio_mode == False:
            try:
                self.playlist_current_clear()
                self.mpd_client.load(TEMP_PLAYLIST_NAME)
                self.mpd_client.rm(TEMP_PLAYLIST_NAME)
            except Exception:
                pass
        self.__radio_mode = radio_mode

mpd = MPDController()
