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

import gettext
import locale
import os
import re
import time
from xml.sax import saxutils

from PySide.QtCore import *
from .lib.PyCascades import CApplication
from PySide.QtCascades import bb

from .series import SeriesManager, Show, Episode
from .lib import constants
from .settings import Settings
from .asyncworker import AsyncWorker, AsyncItem

_ = gettext.gettext

class MainWindow(CApplication):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.toast = bb.system.SystemToast()
        self.toast.setPosition(bb.system.SystemUiPosition.TopCenter)

        # i18n
        '''languages = []
        lc, encoding = locale.getdefaultlocale()
        if lc:
            languages = [lc]
        languages += constants.DEFAULT_LANGUAGES
        gettext.bindtextdomain(constants.SF_COMPACT_NAME,
                               constants.LOCALE_DIR)
        gettext.textdomain(constants.SF_COMPACT_NAME)
        language = gettext.translation(constants.SF_COMPACT_NAME,
                                       constants.LOCALE_DIR,
                                       languages = languages,
                                       fallback = True)
        _ = language.gettext'''

        self.settings = Settings()
        self.settings.load(constants.SF_CONF_FILE)
        self.series_manager = SeriesManager()
        self.series_manager.updateShowEpisodesComplete.connect(self.updateShowEpisodesComplete)
        self.series_manager.updateShowsCallComplete.connect(self.updateShowsCallComplete)
        self.series_manager.beginAddShow.connect(self.beginAddShow)
        self.series_manager.endAddShow.connect(self.endAddShow)
        load_shows_item = AsyncItem(self.series_manager.load,
                                    (constants.SF_DB_FILE,),
                                    self._load_finished)

        self.request = AsyncWorker(True)
        self.request.queue.put(load_shows_item)
        self.request.start()

        self.bbm = BBMManager()
        self.activeFrame = ActiveFrame()

        self.setWindowTitle(constants.SF_NAME)
        settingsWrapper = SettingsWrapper(self)
        self.setSource(constants.QML_MAIN)
        self.rootContext().setContextProperty('bbm', self.bbm)
        self.rootContext().setContextProperty("series_manager", self.series_manager)
        self.rootContext().setContextProperty("seriesList", self.series_manager.sorted_series_list)
        self.rootContext().setContextProperty("settings", settingsWrapper)
        self.rootContext().setContextProperty("activeFrame", self.activeFrame)
        settingsWrapper.showsSortChanged.connect(self.series_manager.sorted_series_list.resort)
        settingsWrapper.hideCompletedShowsChanged.connect(self.series_manager.sorted_series_list.reapplyFilter)
        self.showFullScreen()
        bb.cascades.Application.instance().setCover(self.activeFrame)


    def closeEvent(self):
        self._exit_cb()

    @Slot(QObject)
    def updateShowEpisodesComplete(self, show):
        self.toast.setBody('Updated "%s"' % show.get_name())
        self.toast.show()

    @Slot()
    def updateShowsCallComplete(self):
        self.toast.setBody('Finished updating the shows')
        self.toast.show()

    @Slot(str)
    def beginAddShow(self, showName):
        self.toast.setBody('Adding show "%s"' % showName)
        self.toast.show()

    @Slot(str)
    def endAddShow(self, showName):
        self.toast.setBody('Show "%s" added' % showName)
        self.toast.show()

    def _settings_load_finished(self, dummy_arg, error):
        self.series_manager.sorted_series_list.resort()

    def _load_finished(self, dummy_arg, error):
        self.request = None
        self.series_manager.auto_save(True)

    @Slot()
    def _exit_cb(self):
        if self.request:
            self.request.stop()
        # If the shows list is empty but the user hasn't deleted
        # any, then we don't save in order to avoid overwriting
        # the current db (for the shows list might be empty due
        # to an error)
        if not self.series_manager.series_list and not self.series_manager.have_deleted:
            self.close()
            return
        self.series_manager.auto_save(False)

        save_shows_item = AsyncItem(self.series_manager.save,
                               (constants.SF_DB_FILE,))
        save_conf_item = AsyncItem(self.settings.save,
                               (constants.SF_CONF_FILE,),
                               self._save_finished_cb)
        async_worker = AsyncWorker(False)
        async_worker.queue.put(save_shows_item)
        async_worker.queue.put(save_conf_item)
        async_worker.start()

    def _save_finished_cb(self, dummy_arg, error):
        pass

class ActiveFrame(bb.cascades.SceneCover):
    def __init__(self,parent=None):
        super(ActiveFrame,self).__init__(parent)
        qml = bb.cascades.QmlDocument.create("asset:///AppCover.qml", True)
        self.qml = qml.instance()
        self.qml.setContextProperty('show', None)
        self.qml.load()
        self.mMainContainer = self.qml.createRootObject_Control()
        self.setContent(self.mMainContainer)

    @Slot(QObject)
    def setShow(self, show):
        self.qml.setContextProperty('show', show)

class BBMManager(QObject):
    def __init__(self, parent=None):
        super(BBMManager,self).__init__(parent)
        self.context = bb.platform.bbm.Context(QUuid('3be235e0-035a-478a-b0a1-ead2d2bebf35'))
        self.context.registrationStateUpdated.connect(self.processRegistrationStatus)
        self.messageService = None

    @Slot()
    def invite_to_download(self):
        if self.context.registrationState() == bb.platform.bbm.RegistrationState.Type.Allowed:
            if self.messageService is None:
                self.messageService = bb.platform.bbm.MessageService(self.context)
            self.messageService.sendDownloadInvitation()
        elif self.context.registrationState() == bb.platform.bbm.RegistrationState.Type.BlockedByUser:
            dialog = bb.system.SystemDialog('Yes', 'Later')
            dialog.setTitle('Could not invite to download')
            dialog.setBody('SeriesFinale requires access to BBM to be able to invite users. Do you want to connect SeriesFinale to BBM now?')
            dialog.exec_()
            if dialog.result() == bb.system.SystemUiResult.Type.ConfirmButtonSelection:
                invokeManager = bb.system.InvokeManager()
                request = bb.system.InvokeRequest()
                request.setTarget('sys.settings.target')
                request.setAction("bb.action.OPEN")
                request.setMimeType('settings/view')
                request.setUri(QUrl('settings://permissions'))
                reply = invokeManager.invoke(request)
        elif self.context.registrationState() == bb.platform.bbm.RegistrationState.Type.BlockedByRIM:
            self.showMessage('Disconnected by RIM. RIM is preventing this application from connecting to BBM.')
        elif self.context.registrationState() == bb.platform.bbm.RegistrationState.Type.MaxAppsReached:
            self.showMessage('Too many applications are connected to BBM. Uninstall one or more applications and try again.')
        elif self.context.registrationState() == bb.platform.bbm.RegistrationState.Type.NoDataConnection:
            self.showMessage('Check your Internet connection and try again.')
        elif self.context.registrationState() == bb.platform.bbm.RegistrationState.Type.NoDataConnection:
            self.showMessage('Connecting to BBM. Please wait.')
        else:
            self.showMessage('An unknown error occurred (%s)' % str(self.context.registrationState()))

    @Slot()
    def processRegistrationStatus(self, status):
        if status == bb.platform.bbm.RegistrationState.Type.Unregistered:
            self.context.requestRegisterApplication()

    def showMessage(self, message):
        dialog = bb.system.SystemDialog('OK')
        dialog.setTitle('Could not invite to download')
        dialog.setBody(message)
        dialog.exec_()

class SettingsWrapper(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._hideCompletedShows = self.getHideCompletedShows()

    addSpecialSeasonsChanged = Signal()
    def getAddSpecialSeasons(self):
        return Settings().getConf(Settings.ADD_SPECIAL_SEASONS)
    def setAddSpecialSeasons(self, add):
        Settings().setConf(Settings.ADD_SPECIAL_SEASONS, add)
        self.addSpecialSeasonsChanged.emit()
    addSpecialSeasons = Property(bool,getAddSpecialSeasons,setAddSpecialSeasons,notify=addSpecialSeasonsChanged)

    hideCompletedShowsChanged = Signal()
    def getHideCompletedShows(self):
        return Settings().getConf(Settings.HIDE_COMPLETED_SHOWS)
    def setHideCompletedShows(self, add):
        if self._hideCompletedShows == add:
            return
        Settings().setConf(Settings.HIDE_COMPLETED_SHOWS, add)
        self.hideCompletedShowsChanged.emit()
    hideCompletedShows = Property(bool,getHideCompletedShows,setHideCompletedShows,notify=hideCompletedShowsChanged)

    episodesOrderChanged = Signal()
    def getEpisodesOrder(self):
        return Settings().getConf(Settings.EPISODES_ORDER_CONF_NAME)
    def setEpisodesOrder(self, newOrder):
        Settings().setConf(Settings.EPISODES_ORDER_CONF_NAME, newOrder)
        self.episodesOrderChanged.emit()
    episodesOrder = Property(int,getEpisodesOrder,setEpisodesOrder,notify=episodesOrderChanged)

    showsSortChanged = Signal()
    def getShowsSort(self):
        return Settings().getConf(Settings.SHOWS_SORT)
    def setShowsSort(self, newOrder):
        Settings().setConf(Settings.SHOWS_SORT, newOrder)
        self.showsSortChanged.emit()
    showsSort = Property(int,getShowsSort,setShowsSort,notify=showsSortChanged)
