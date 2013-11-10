# -*- coding: utf-8 -*-

###########################################################################
#    SeriesFinale
#    Copyright (C) 2009 Joaquim Rocha <jrocha@igalia.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

import os
from .lib import thetvdbapi, serializer, constants
from .lib.util import image_downloader
from .lib.listmodel import *
from xml.etree import ElementTree as ET
from .asyncworker import AsyncWorker, AsyncItem
from .lib.constants import TVDB_API_KEY, DATA_DIR, DEFAULT_LANGUAGES, SF_LANG_FILE
from .settings import Settings
from datetime import datetime
from datetime import timedelta
from xml.sax import saxutils
import gettext
import locale
import logging
logging.basicConfig(level=logging.DEBUG)

_ = gettext.gettext

from PySide import QtCore, QtGui

class Show(QtCore.QObject):

    infoMarkupChanged = QtCore.Signal()
    showArtChanged = QtCore.Signal()
    episodesListUpdated = QtCore.Signal()
    def __init__(self, name, genre = None, overview = None, network = None,
                 rating = None, actors = [], episode_list = ListModel(), image = None,
                 thetvdb_id = -1, season_images = {}, id = -1, language = None,
                 downloading_show_image = False, downloading_season_image = False, imdb_id = ''):
        QtCore.QObject.__init__(self)
        self.id = id
        self.name = name
        self.genre = genre
        self.overview = overview
        self.network = network
        self.rating = rating
        self.actors = actors
        self.episode_list = episode_list
        self.thetvdb_id = thetvdb_id
        self.imdb_id = imdb_id
        self.language = language
        self.downloading_show_image = False
        self.downloading_season_image = downloading_season_image
        self._busy = False
        self._seasonsList = None
        self._sorted_episode_list_by_season = {}

    busyChanged = QtCore.Signal()
    def get_busy(self): return self._busy
    def set_busy(self, busy):
        self._busy = busy
        self.busyChanged.emit()
    busy = QtCore.Property(bool,get_busy,notify=busyChanged)

    coverImageChanged = QtCore.Signal()
    def have_cover_image(self):
        path = os.path.join(DATA_DIR, '%s.jpg' % self.get_poster_prefix())
        if os.path.exists(path):
            return True
        return False
    def cover_image(self):
        if not self.have_cover_image():
            return constants.PLACEHOLDER_IMAGE
        return os.path.join(DATA_DIR, '%s.jpg' % self.get_poster_prefix())
    def set_cover_image(self, new_path):
        self.coverImageChanged.emit()
    coverImage = QtCore.Property(str,cover_image,set_cover_image,notify=coverImageChanged)

    bannerImageChanged = QtCore.Signal()
    def have_banner_image(self):
        path = os.path.join(DATA_DIR, '%s_banner.jpg' % self.get_poster_prefix())
        if os.path.exists(path):
            return True
        return False
    def banner_image(self):
        if not self.have_banner_image():
            return constants.PLACEHOLDER_IMAGE
        return os.path.join(DATA_DIR, '%s_banner.jpg' % self.get_poster_prefix())
    def set_banner_image(self, new_path):
        self.bannerImageChanged.emit()
    bannerImage = QtCore.Property(str,banner_image,set_banner_image,notify=bannerImageChanged)

    imdbIdChanged = QtCore.Signal()
    def getImdbId(self):
        return self.imdb_id
    imdbId=QtCore.Property(str,getImdbId,notify=imdbIdChanged)

    nameChanged = QtCore.Signal()
    def get_name(self):
        return str(self.name)
    def set_name(self, name):
        self.name = name
        self.nameChanged.emit()
    showName = QtCore.Property(str,get_name,set_name,notify=nameChanged)

    overviewChanged = QtCore.Signal()
    def get_overview(self):
        return self.overview
    def set_overview(self, overview):
        self.overview = overview
        self.overviewChanged.emit()
    showOverview = QtCore.Property(str,get_overview,set_overview,notify=overviewChanged)

    def get_episodes_by_season(self, season_number):
        if season_number is None:
            return self.episode_list
        return [episode for episode in self.episode_list if episode.season_number == season_number]

    @QtCore.Slot(QtCore.QObject,result=QtCore.QObject)
    def get_next_episode(self, episode):
        return self._get_episode_by_offset(episode, 1)

    @QtCore.Slot(QtCore.QObject,result=QtCore.QObject)
    def get_previous_episode(self, episode):
        return self._get_episode_by_offset(episode, -1)

    def _get_episode_by_offset(self, episode, offset):
        episodes = [(ep.episode_number, ep) for ep in \
                    self.get_episodes_by_season(episode.season_number)]
        episodes.sort()
        number_of_episodes = len(episodes)
        for i in range(number_of_episodes):
            current_episode = episodes[i][1]
            if current_episode == episode:
                return episodes[(i + offset) % number_of_episodes][1]
        return episode

    @QtCore.Slot(result=QtCore.QObject)
    def get_seasons_model(self):
        if self._seasonsList == None:
            self._seasonsList = SortedSeasonsList(ListModel(self.get_seasons()), Settings(), self)
        return self._seasonsList

    def get_seasons(self):
        seasons = []
        for episode in self.episode_list:
            season_number = episode.season_number
            if season_number not in seasons:
                seasons.append(season_number)
        return seasons

    @QtCore.Slot(str,result=str)
    def get_season_image(self, season):
        path = os.path.join(DATA_DIR, '%s.jpg' % self.get_season_poster_prefix(season))
        if os.path.exists(path):
            return path
        return constants.PLACEHOLDER_IMAGE

    def have_season_image(self, season):
        return os.path.exists(os.path.join(DATA_DIR, '%s.jpg' % self.get_season_poster_prefix(season)))

    def have_all_season_images(self):
        for season in self.get_seasons():
            if not self.have_season_image(season):
                return False
        return True

    def get_episode_list_by_season(self, season):
        return [episode for episode in self.episode_list \
                  if episode.season_number == season]

    @QtCore.Slot(str,result=QtCore.QObject)
    def get_sorted_episode_list_by_season(self, season):
        if season not in self._sorted_episode_list_by_season:
            self._sorted_episode_list_by_season[season] = SortedEpisodesList(ListModel(self.get_episode_list_by_season(season)), Settings(), self)
        return self._sorted_episode_list_by_season[season]

    def update_episode_list(self, episode_list):
        add_special_seasons = Settings().getConf(Settings.ADD_SPECIAL_SEASONS)
        series_manager = SeriesManager()
        for episode in episode_list:
            exists = False
            for ep in self.episode_list:
                if ep == episode:
                    exists = True
                    ep.merge_episode(episode)
                    series_manager.changed = True
            if not exists:
                if not add_special_seasons and \
                   self.is_special_season(episode.season_number):
                    continue
                self.episode_list.append(episode)
                if episode.season_number in self._sorted_episode_list_by_season:
                    self._sorted_episode_list_by_season[episode.season_number].sourceModel().append(episode)
                series_manager.changed = True

    def delete_episode(self, episode):
        series_manager = SeriesManager()
        for i in range(len(self.episode_list)):
            if self.episode_list[i] == episode:
                del self.episode_list[i]
                series_manager.changed = True
                break

    @QtCore.Slot(str)
    def delete_season(self, season):
        dialog = bb.system.SystemDialog('Delete', 'Cancel')
        dialog.setTitle('Delete?')
        dialog.setBody('This will delete the selected season.')
        dialog.exec_()
        if dialog.result() != bb.system.SystemUiResult.Type.ConfirmButtonSelection:
            return
        episodes = self.get_episode_list_by_season(season)
        for episode in episodes:
            self.delete_episode(episode)
        if self._seasonsList is not None:
            model = self._seasonsList.sourceModel()
            i = model.list().index(season)
            if i:
                del model[i]
        self.infoMarkupChanged.emit()

    @QtCore.Slot(str)
    def mark_all_episodes_as_not_watched(self, season = None):
        self._mark_all_episodes(False, season)

    @QtCore.Slot(str)
    def mark_all_episodes_as_watched(self, season = None):
        self._mark_all_episodes(True, season)

    def _mark_all_episodes(self, watched, season = None):
        episodes = self.get_episodes_by_season(season)
        for episode in episodes:
            episode.isWatched = watched
        SeriesManager().updated()
        self.infoMarkupChanged.emit()

    @QtCore.Slot(str, result=bool)
    def is_completely_watched(self, season = None):
        episodes = self.get_episodes_by_season(season)
        for episode in episodes:
            if not episode.isWatched:
                return False
        return True

    def get_episodes_info(self, season = None):
        info = {}
        if season:
            episodes = self.get_episode_list_by_season(season)
        else:
            episodes = self.episode_list
        episodes_to_watch = [episode for episode in episodes \
                            if not episode.isWatched]
        info['episodes'] = episodes
        #Filter out only the aired episodes
        info['episodes_to_watch'] = [episode for episode in episodes_to_watch \
                            if episode.already_aired()]
        if season:
            sorted_episodes_to_watch = [('%02d'%int(episode.season_number), episode.episode_number, episode) \
                                         for episode in episodes_to_watch if episode.air_date]
        else:
            # Leave Extras for end
            sorted_episodes_to_watch = [('%02d'%int(episode.season_number), episode.episode_number, episode) \
                                         for episode in episodes_to_watch \
                                         if episode.season_number != '0' and episode.air_date]
            if not sorted_episodes_to_watch:
                sorted_episodes_to_watch = [('%02d'%int(episode.season_number), episode.episode_number, episode) \
                                             for episode in episodes_to_watch \
                                             if episode.season_number == '0' and episode.air_date]
        sorted_episodes_to_watch.sort()
        if sorted_episodes_to_watch:
            info['next_episode'] = sorted_episodes_to_watch[0][2]
        else:
            info['next_episode'] = None
        return info

    def __str__(self):
        return self.name

    def get_info_markup(self, info = None):
        seasons = len(self.get_seasons())
        if seasons:
            episodes_info = info or self.get_episodes_info()
            episodes_to_watch = episodes_info['episodes_to_watch']
            next_episode = episodes_info['next_episode']
            show_info = gettext.ngettext('%s season', '%s seasons', seasons) \
                         % seasons
            if self.is_completely_watched():
                show_info += '<br/>' + _('Completely watched')
            else:
                if episodes_to_watch:
                    n_episodes_to_watch = len(episodes_to_watch)
                    show_info += '<br/>' + gettext.ngettext('%s episode not watched',
                                                          '%s episodes not watched',
                                                          n_episodes_to_watch) \
                                                          % n_episodes_to_watch
                else:
                    show_info += '<br/>' + _('No episodes to watch')
                if next_episode:
                    next_air_date = next_episode.air_date
                    if next_air_date:
                        show_info += '<br/>' + _('<i>Next:</i> %s, %s') % \
                                     (next_episode.get_episode_show_number(), \
                                     next_episode.get_air_date_text())
                    else:
                        show_info += '<br/>' + _('<i>Next:</i> %s') % \
                                     next_episode.get_episode_show_number()
        else:
            show_info = ''
        return show_info
    infoMarkup = QtCore.Property(str,get_info_markup,notify=infoMarkupChanged)

    def get_next_show_markup(self):
        show_info = ''
        seasons = len(self.get_seasons())
        if seasons:
            episodes_info = self.get_episodes_info()
            #episodes_to_watch = episodes_info['episodes_to_watch']
            next_episode = episodes_info['next_episode']
            if self.is_completely_watched():
                show_info = _('Completely watched')
            elif next_episode:
                show_info = _('Next: %s') % next_episode.get_episode_show_number()
        return show_info
    nextShowMarkup = QtCore.Property(str,get_next_show_markup,notify=infoMarkupChanged)

    @QtCore.Slot(str,result=str)
    def get_season_name(self, season):
        if season == '0':
            return _('Special')
        else:
            return _('Season %s') % season

    @QtCore.Slot(str,result=str)
    def get_season_info_markup(self, season):
        info = self.get_episodes_info(season)
        episodes = info['episodes']
        episodes_to_watch = info['episodes_to_watch']
        next_episode = info['next_episode']
        season_info = ''
        if not episodes_to_watch:
            if next_episode:
                season_info = _('No episodes to watch')
            elif episodes:
                season_info = _('Completely watched')
        else:
            number_episodes_to_watch = len(episodes_to_watch)
            season_info = gettext.ngettext('%s episode not watched',
                                           '%s episodes not watched',
                                           number_episodes_to_watch) \
                                           % number_episodes_to_watch
            if next_episode:
                next_air_date = next_episode.air_date
                if next_air_date:
                    season_info += '<br/>' + _('<i>Next episode:</i> %s, %s') % \
                                   (next_episode.episode_number, \
                                    next_episode.get_air_date_text())
                else:
                    season_info += '<br/>' + _('<i>Next episode:</i> %s') % \
                                   next_episode.episode_number
        return season_info

    def get_poster_prefix(self):
        if self.thetvdb_id != -1:
            return str(self.thetvdb_id)
        return str(self.name)

    def get_season_poster_prefix(self, season = None):
        prefix = '%s_season_' % self.get_poster_prefix()
        if season:
            prefix = '%s%s' % (prefix, str(season))
        return prefix

    def is_special_season(self, season_number):
        try:
            season_number = int(season_number)
        except ValueError:
            return False
        return season_number == 0

class Episode(QtCore.QObject):

    def __init__(self, name, show, episode_number, season_number = '1',
                 overview = None, director = None, guest_stars = [],
                 rating = None, writer = None, watched = False,
                 air_date = '', id = -1, image = '', imdb_id = ''):
        QtCore.QObject.__init__(self)
        self.id = id
        self.name = name
        self.show = show
        self.image = image
        self.episode_number = episode_number
        self.season_number = season_number
        self.overview = overview
        self.director = director
        self.guest_stars = guest_stars
        self.rating = rating
        self.writer = writer
        self.imdb_id = imdb_id
        self.watched = watched
        try:
            self.air_date = datetime.strptime(air_date, '%Y-%m-%d').date()
        except:
            self.air_date = ''

    coverImageChanged = QtCore.Signal()
    def cover_image(self):
        path = os.path.join(DATA_DIR, '%s_episode_S%02dE%02d' % (self.show.thetvdb_id, int(self.season_number), int(self.episode_number)))
        path = os.path.abspath(path)
        if os.path.exists("%s.jpg" % path):
            return "%s.jpg" % path
        if self.image == '':
            return constants.PLACEHOLDER_IMAGE
        url = "http://www.thetvdb.com/banners/%s" % (self.image)
        image_file = image_downloader(url, path)
        return image_file
    coverImage = QtCore.Property(str,cover_image,notify=coverImageChanged)

    imdbIdChanged = QtCore.Signal()
    def getImdbId(self):
        return self.imdb_id
    imdbId=QtCore.Property(str,getImdbId,notify=imdbIdChanged)

    def get_episode_show_number(self):
        return '%sx%02d' % (self.season_number, int(self.episode_number))

    def __repr__(self):
        return self.get_title()

    ratingChanged = QtCore.Signal()
    def get_rating(self):
        try:
            return str(float(self.rating))
        except:
            return '0'
    episodeRating = QtCore.Property(str,get_rating,notify=ratingChanged)

    titleChanged = QtCore.Signal()
    def get_title(self):
        return _('Ep. %s: %s') % (self.get_episode_show_number(), self.name)
    title = QtCore.Property(str,get_title,notify=titleChanged)

    watchedChanged = QtCore.Signal()
    def get_watched(self): return self.watched
    def set_watched(self, watched):
        if (self.watched == watched):
            return
        self.watched = watched
        self.watchedChanged.emit()
        self.show.infoMarkupChanged.emit()
        series_manager = SeriesManager()
        series_manager.changed = True
        series_manager.sorted_series_list.resort(self.show)
    isWatched = QtCore.Property(bool,get_watched,set_watched,notify=watchedChanged)

    overviewChanged = QtCore.Signal()
    def get_overview(self):
        return self.overview
    def set_overview(self, overview):
        self.overview = overview
        self.overviewChanged.emit()
    overviewText = QtCore.Property(str,get_overview,set_overview,notify=overviewChanged)

    def __eq__(self, episode):
        if not episode:
            return False
        return self.show == episode.show and \
               self.episode_number == episode.episode_number and \
               self.season_number == episode.season_number

    def merge_episode(self, episode):
        self.name = episode.name or self.name
        self.show = episode.show or self.show
        self.episode_number = episode.episode_number or self.episode_number
        self.season_number = episode.season_number or self.season_number
        self.overview = episode.overview or self.overview
        self.director = episode.director or self.director
        self.guest_stars = episode.guest_stars or self.guest_stars
        self.rating = episode.rating or self.rating
        self.writer = episode.writer or self.writer
        self.watched = episode.watched or self.watched
        self.air_date = episode.air_date or self.air_date
        self.image = episode.image or self.image
        self.imdb_id = episode.imdb_id or self.imdb_id
        #TODO: Maybe we should check which really changed and only emit those signals?
        self.ratingChanged.emit()
        self.titleChanged.emit()
        self.airDateTextChanged.emit()
        self.watchedChanged.emit()
        self.imdbIdChanged.emit()
        self.coverImageChanged.emit()

    airDateTextChanged = QtCore.Signal()
    def get_air_date_text(self):
        if not self.air_date:
            return ''
        today = datetime.today().date()
        if today == self.air_date:
            return _('Today')
        if today + timedelta(days = 1) == self.air_date:
            return _('Tomorrow')
        if today - timedelta(days = 1) == self.air_date:
            return _('Yesterday')
        next_air_date_str = self.air_date.strftime('%d %b')
        if self.air_date.year != datetime.today().year:
            next_air_date_str += self.air_date.strftime(' %Y')
        return next_air_date_str
    airDateText = QtCore.Property(str,get_air_date_text,notify=airDateTextChanged)

    @QtCore.Slot(result=bool)
    def already_aired(self):
        if self.air_date and self.air_date <= datetime.today().date():
            return True
        return False

    def _get_episode_number(self):
        return self._episode_number

    def _set_episode_number(self, number):
        try:
            self._episode_number = int(number)
        except ValueError:
            self._episode_number = 1
        self.titleChanged.emit()

    def _get_air_date(self):
        return self._air_date

    def _set_air_date(self, new_air_date):
        if type(new_air_date) != str:
            self._air_date = new_air_date
            return
        for format in ['%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y',
                       '%m-%d-%Y', '%d %b %Y']:
            try:
                self._air_date = datetime.strptime(new_air_date, format).date()
            except ValueError:
                continue
            else:
                return
        self._air_date = None
        self.airDateTextChanged.emit()

    def get_info_markup(self):
        color = get_color(constants.SECONDARY_TEXT_COLOR)
        if not self.watched and self.already_aired():
            color = get_color(constants.ACTIVE_TEXT_COLOR)
        return '<span foreground="%s">%s\n%s</span>' % \
               (color, saxutils.escape(str(self)), self.get_air_date_text())

    def updated(self):
        SeriesManager().updated()

    episode_number = property(_get_episode_number, _set_episode_number)
    air_date = property(_get_air_date, _set_air_date)

    def get_most_recent(self, other_episode):
        if not other_episode:
            if self.already_aired():
                return self
            else:
                return None
        if other_episode.already_aired() and not self.already_aired():
            return other_episode
        if self.already_aired() and not other_episode.already_aired():
            return self
        if not self.already_aired() and not other_episode.already_aired():
            return None
        if self.air_date > other_episode.air_date:
            return self
        if self.air_date < other_episode.air_date:
            return other_episode
        return None

class SeriesManager(QtCore.QObject):

    GET_FULL_SHOW_COMPLETE_SIGNAL = 'get-full-show-complete'
    #UPDATE_SHOW_EPISODES_COMPLETE_SIGNAL = 'update-show-episodes-complete'
    updateShowEpisodesComplete = QtCore.Signal(QtCore.QObject)
    #UPDATE_SHOWS_CALL_COMPLETE_SIGNAL = 'update-shows-call-complete'
    updateShowsCallComplete = QtCore.Signal(QtCore.QObject)
    #SHOW_LIST_CHANGED_SIGNAL = 'show-list-changed'
    showListChanged = QtCore.Signal()

    beginAddShow = QtCore.Signal(str)
    endAddShow = QtCore.Signal(str)

   # __gsignals__ = {GET_FULL_SHOW_COMPLETE_SIGNAL: (gobject.SIGNAL_RUN_LAST,
   #                                                 gobject.TYPE_NONE,
   #                                                 (gobject.TYPE_PYOBJECT,
   #                                                  gobject.TYPE_PYOBJECT)),
   #                 UPDATE_SHOW_EPISODES_COMPLETE_SIGNAL: (gobject.SIGNAL_RUN_LAST,
   #                                                        gobject.TYPE_NONE,
   #                                                        (gobject.TYPE_PYOBJECT,
   #                                                         gobject.TYPE_PYOBJECT)),
   #                 UPDATE_SHOWS_CALL_COMPLETE_SIGNAL: (gobject.SIGNAL_RUN_LAST,
   #                                                    gobject.TYPE_NONE,
   #                                                    (gobject.TYPE_PYOBJECT,
   #                                                     gobject.TYPE_PYOBJECT)),
   #                 SHOW_LIST_CHANGED_SIGNAL: (gobject.SIGNAL_RUN_LAST,
   #                                            gobject.TYPE_NONE,
   #                                            ()),
   #                 UPDATED_SHOW_ART: (gobject.SIGNAL_RUN_LAST,
   #                                    gobject.TYPE_NONE,
   #                                    (gobject.TYPE_PYOBJECT,)),
   #                }

    _instance = None
    _instance_initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance

        s = super(SeriesManager, cls)
        cls._instance = super(SeriesManager, cls).__new__(cls, *args, **kwargs)
        s.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not SeriesManager._instance_initialized:
            SeriesManager._instance_initialized = True
            QtCore.QObject.__init__(self)

            self.series_list = ListModel()
            self.sorted_series_list = SortedSeriesList(Settings())
            self.sorted_series_list.setSourceModel(self.series_list)

            self.thetvdb = thetvdbapi.TheTVDB(TVDB_API_KEY)
            self.changed = False
            self.auto_save_id = None

            # Cached values
            self._cached_tvdb_shows = {}

            # Searching
            self.searching = False
            self.search_results = ListModel([])

            # Languages
            # self.languages = self.thetvdb.get_available_languages()
            self.languages = self._load_languages(SF_LANG_FILE)
            self.default_language = None

            self.have_deleted = False
            self.isUpdating = False
            self.isLoading = False
            self.filePicker = None

    versionChanged = QtCore.Signal()
    def get_version(self):
        return constants.SF_VERSION
    version = QtCore.Property(str,get_version,notify=versionChanged)

    busyChanged = QtCore.Signal()
    def get_busy(self):
        return self.isUpdating or self.isLoading
    busy = QtCore.Property(bool,get_busy,notify=busyChanged)

    def update_languages(self):
        self.languages = self.thetvdb.get_available_languages()
        self._save_languages(SF_LANG_FILE)
        return self.languages

    def get_languages(self):
        if self.languages is None:
            return self.update_languages()
        return self.languages

    def get_default_language(self):
        if self.default_language is None:
            #Get local supported languages
            local_languages = []
            lc, encoding = locale.getdefaultlocale()
            if lc:
                local_languages = [lc]
            local_languages += ['es_ES']
            local_languages += constants.DEFAULT_LANGUAGES
            #Find language
            self.default_language = 'en'
            for lang in local_languages:
                code = lang.split('_')[0]
                if self.get_languages().has_key(code):
                    self.default_language = code
                    break

        return self.default_language

    def _load_languages(self, file_path):
        if not os.path.exists(file_path):
            return None
        return serializer.deserialize(file_path)

    def _save_languages(self, file_path):
        dirname = os.path.dirname(file_path)
        if not (os.path.exists(dirname) and os.path.isdir(dirname)):
            os.mkdir(dirname)
        serialized = serializer.serialize(self.languages)
        save_file = open(file_path, 'w')
        save_file.write(serialized)
        save_file.close()

    searchingChanged = QtCore.Signal()
    def get_searching(self): return self.searching
    isSearching = QtCore.Property(bool,get_searching,notify=searchingChanged)

    @QtCore.Slot(result=str)
    def data_filename(self):
        return constants.SF_DB_FILE

    @QtCore.Slot(str)
    @QtCore.Slot(str,str)
    def search_shows(self, terms, language = "en"):
        if not terms:
            return []
        self.search_results.clear()
        self.searching = True
        self.searchingChanged.emit()
        async_worker = AsyncWorker(True)
        async_item = AsyncItem(self.thetvdb.get_matching_shows,
                               (terms, language,),
                               self._search_finished_callback)
        async_worker.queue.put(async_item)
        async_worker.start()

    @QtCore.Slot(result=QtCore.QObject)
    def search_result_model(self):
        return self.search_results

    def _search_finished_callback(self, tvdbshows, error):
        if not error:
            for show_id, show in tvdbshows:
                self._cached_tvdb_shows[show_id] = show
                self.search_results.append(show)
        self.searching = False
        self.searchingChanged.emit()

    @QtCore.Slot(QtCore.QObject)
    def update_show_episodes(self, show):
        return self.update_all_shows_episodes([show])

    @QtCore.Slot()
    def update_all_shows_episodes(self, show_list = []):
        self.isUpdating = True
        self.busyChanged.emit()
        show_list = show_list or self.series_list
        async_worker = AsyncWorker(False)
        update_images_worker = AsyncWorker(True)
        i = 0
        n_shows = len(show_list)
        for i in range(n_shows):
            show = show_list[i]
            show.set_busy(True)
            async_item = AsyncItem(self.thetvdb.get_show_and_episodes,
                                   (show.thetvdb_id, show.language,),
                                   self._set_show_episodes_complete_cb,
                                   (show, update_images_worker, i == n_shows - 1))
            async_worker.queue.put(async_item)
            async_item = AsyncItem(self._set_show_images,
                                   (show,),
                                   None,)
            update_images_worker.queue.put(async_item)
        async_worker.start()
        return async_worker

    def _set_show_episodes_complete_cb(self, show, images_worker, last_call, tvdbcompleteshow, error):
        if not error and tvdbcompleteshow:
            episode_list = [self._convert_thetvdbepisode_to_episode(tvdb_ep,show) \
                            for tvdb_ep in tvdbcompleteshow[1]]
            show.update_episode_list(episode_list)
            show.imdb_id = tvdbcompleteshow[0].imdb_id
        self.updateShowEpisodesComplete.emit(show)
        show.episodesListUpdated.emit()
        show.set_busy(False)
        if last_call:
            self.updateShowsCallComplete.emit(show)
            self.isUpdating = False
            self.busyChanged.emit()
            images_worker.start()

    def _search_show_to_update_callback(self, tvdbshows):
        if not tvdbshows:
            # FIXME: raise error
            return
        for show_id, show in tvdbshows:
            pass

    @QtCore.Slot(str)
    def get_complete_show(self, show_name, language = "en"):
        self.isUpdating = True
        self.busyChanged.emit()
        show_id = self._cached_tvdb_shows.get(show_name, None)
        for show_id, show_title in self._cached_tvdb_shows.items():
            if show_title == show_name:
                break
        if not show_id:
            return
        async_worker = AsyncWorker(False)
        async_item = AsyncItem(self._get_complete_show_from_id,
                               (show_id, language,),
                               self._get_complete_show_finished_cb)
        async_worker.queue.put(async_item)
        async_worker.start()
        self.beginAddShow.emit(show_name)

    def _get_complete_show_from_id(self, show_id, language):
        tvdb_show_episodes = self.thetvdb.get_show_and_episodes(show_id, language)
        if not tvdb_show_episodes:
            return None
        show = self._convert_thetvdbshow_to_show(tvdb_show_episodes[0])
        show.id = self._get_id_for_show()
        show.episode_list = ListModel([])
        for tvdb_ep in tvdb_show_episodes[1]:
            episode = self._convert_thetvdbepisode_to_episode(tvdb_ep,
                                                              show)
            add_special_seasons = Settings().getConf(Settings.ADD_SPECIAL_SEASONS)
            if not add_special_seasons and \
               show.is_special_season(episode.season_number):
                continue
            show.episode_list.append(episode)
        self.series_list.append(show)
        self.changed = True
        self.isUpdating = False
        self.busyChanged.emit()
        return show

    def _get_complete_show_finished_cb(self, show, error):
        #self.emit(self.GET_FULL_SHOW_COMPLETE_SIGNAL, show, error)
        logging.debug('GET_FULL_SHOW_COMPLETE_SIGNAL') #TODO
        async_worker = AsyncWorker(True)
        async_item = AsyncItem(self._set_show_images,
                               (show,),
                               None,)
        async_worker.queue.put(async_item)
        async_worker.start()
        self.endAddShow.emit(show.name)

    def get_show_by_id(self, show_id):
        for show in self.series_list:
            if show.id == show_id:
                return show
        return None

    def get_show_by_name(self, show_name):
        for show in self.series_list:
            if show.name == show_name:
                return show
        return None

    def _convert_thetvdbshow_to_show(self, thetvdb_show):
        show_obj = Show(thetvdb_show.name, season_images = {})
        show_obj.language = thetvdb_show.language
        show_obj.genre = thetvdb_show.genre
        show_obj.set_overview(thetvdb_show.overview)
        show_obj.network = thetvdb_show.network
        show_obj.rating = thetvdb_show.rating
        show_obj.actors = thetvdb_show.actors
        show_obj.thetvdb_id = thetvdb_show.id
        show_obj.imdb_id = thetvdb_show.imdb_id
        return show_obj

    def _convert_thetvdbepisode_to_episode(self, thetvdb_episode, show = None):
        episode_obj = Episode(thetvdb_episode.name, show, thetvdb_episode.episode_number)
        episode_obj.show = show
        episode_obj.season_number = thetvdb_episode.season_number
        episode_obj.overview = thetvdb_episode.overview
        episode_obj.director = thetvdb_episode.director
        episode_obj.guest_stars = thetvdb_episode.guest_stars
        episode_obj.rating = thetvdb_episode.rating
        episode_obj.writer = thetvdb_episode.writer
        episode_obj.air_date = thetvdb_episode.first_aired or ''
        episode_obj.image = thetvdb_episode.image or ''
        episode_obj.imdb_id = thetvdb_episode.imdb_id or ''
        return episode_obj

    def add_show(self, show):
        if show.id == -1:
            show.id = self._get_id_for_show()
        self.series_list.append(show)
        self.changed = True
        #self.emit(self.SHOW_LIST_CHANGED_SIGNAL)

    @QtCore.Slot(QtCore.QObject)
    def delete_show(self, show):
        dialog = bb.system.SystemDialog('Delete', 'Cancel')
        dialog.setTitle('Delete?')
        dialog.setBody('This will delete the selected show.')
        dialog.exec_()
        if dialog.result() != bb.system.SystemUiResult.Type.ConfirmButtonSelection:
            return
        for i in range(len(self.series_list)):
            if self.series_list[i] == show:
                del self.series_list[i]
                self.changed = True
                self.have_deleted = True
                #self.emit(self.SHOW_LIST_CHANGED_SIGNAL)
                break

    def _get_shows_from_id(self, id):
        return [show for show in self.series_list if show.id == id]

    def _get_id_for_show (self):
        id = 1
        for show in self.series_list:
            id = show.id
            if show.id >= id:
                id += 1
        return id

    def _set_show_images(self, show):
        thetvdb_id = show.thetvdb_id
        if thetvdb_id == -1:
            return
        seasons = show.get_seasons()
        # Check if the download is needed
        if show.have_all_season_images() and show.have_cover_image() and show.have_banner_image():
            #self.emit(self.UPDATED_SHOW_ART, show) #TODO
            show.showArtChanged.emit()
            return
        image_choices = self.thetvdb.get_show_image_choices(thetvdb_id)
        for image in image_choices:
            image_type = image[1]
            url = image[0]
            if image_type  == 'poster' and not show.have_cover_image():
                show.downloading_show_image = True
                #self.emit(self.UPDATED_SHOW_ART, show) #TODO
                show.showArtChanged.emit()
                target_file = os.path.join(DATA_DIR, show.get_poster_prefix())
                image_file = os.path.abspath(image_downloader(url, target_file))
                #scale if needed
                img = QtGui.QImage(image_file)
                if img.width() > 350:
                    newImg = img.scaledToWidth(350)
                    newImg.save(image_file)
                show.set_cover_image(image_file)
                QtCore.qDebug("T: %s" % image_file)
                show.downloading_show_image = False
                self.changed = True
                #self.emit(self.UPDATED_SHOW_ART, show) #TODO
                show.showArtChanged.emit()
            elif image_type == 'season':
                season = image[3]
                if season in seasons and not show.have_season_image(season):
                    show.downloading_season_image = True
                    #self.emit(self.UPDATED_SHOW_ART, show) #TODO
                    show.showArtChanged.emit()
                    target_file = os.path.join(DATA_DIR,
                                               show.get_season_poster_prefix(season))
                    try:
                        image_file = os.path.abspath(image_downloader(url,
                                                                      target_file))
                    except Exception as exception:
                        logging.debug(str(exception))
                    else:
                        #scale if needed
                        img = QtGui.QImage(image_file)
                        if img.width() > 100:
                            newImg = img.scaledToWidth(100)
                            newImg.save(image_file)
                    show.downloading_season_image = False
                    self.changed = True
                    #self.emit(self.UPDATED_SHOW_ART, show) #TODO
                    show.showArtChanged.emit()
            elif image_type == 'series':
                target_file = os.path.join(DATA_DIR, '%s_banner' % show.get_poster_prefix())
                image_file = os.path.abspath(image_downloader(url, target_file))
                show.set_banner_image(image_file)
            if show.have_cover_image() and show.have_banner_image() and show.have_all_season_images():
                break

    @QtCore.Slot()
    def import_backup(self):
        if self.filePicker == None:
            self.filePicker = bb.cascades.pickers.FilePicker()
            self.filePicker.setTitle("Select backup file")
            self.filePicker.fileSelected.connect(self.importfile_selected)
        self.filePicker.open()

    def importfile_selected(self, files):
        self.dialog = bb.system.SystemDialog('Continue', 'Cancel')
        self.dialog.setTitle('Import')
        self.dialog.setBody('Importing this file will clear all the current show in this application. Are you sure you want to continue?')
        self.dialog.exec_()
        self.dialog.deleteLater()
        if self.dialog.result() == bb.system.SystemUiResult.Type.ConfirmButtonSelection:
            self.series_list.clear()
            self.load(files[0])
            self.changed = True

    def save(self, save_file_path):
        if not self.changed:
            return True

        dirname = os.path.dirname(save_file_path)
        if not (os.path.exists(dirname) and os.path.isdir(dirname)):
            os.mkdir(dirname)
        serialized = serializer.serialize(self.series_list)
        save_file_path_tmp = save_file_path + ".tmp"
        save_file = open(save_file_path_tmp, 'w')
        save_file.write(serialized)
        save_file.close()
        os.rename(save_file_path_tmp, save_file_path)
        self.changed = False
        return True

    def timerEvent(self, event):
        if (event.timerId() == self.auto_save_id):
            self.save(constants.SF_DB_FILE)

    def load(self, file_path):
        if not os.path.exists(file_path):
            return
        self.isLoading = True
        self.busyChanged.emit()
        for serie in serializer.deserialize(file_path):
            self.series_list.append(serie)
        self.changed = False
        self.showListChanged.emit()
        self.isLoading = False
        self.busyChanged.emit()

    def updated(self):
        self.changed = True

    def auto_save(self, activate = True):
        if activate and not self.auto_save_id:
            self.auto_save_id = self.startTimer(constants.SAVE_TIMEOUT_MS)
        elif self.auto_save_id and not activate:
            self.killTimer(self.auto_save_id)
            self.auto_save_id = None
