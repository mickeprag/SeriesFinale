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

from PySide.QtCascades import bb
from PySide.QtCore import qDebug, QObject, Slot, QThread

import sys, traceback

class ListModel(bb.cascades.DataModel):
    def __init__(self, items = [], parent = None):
        super(ListModel, self).__init__(parent)
        self._items = items
        for item in items:
            if isinstance(item, QObject) and item.parent() == None:
                item.setParent(self)
        self._itemType = ''

    def append(self, show):
        if isinstance(show, QObject):
            if (show.parent() == None):
                #If we do not have a parent the item the ListView
                #will reparent the object which will not work.
                show.setParent(self)
        self._items.append(show)
        self.itemAdded.emit([len(self._items)-1])

    def clear(self):
        qDebug("Clearing")
        '''if not self._items:
            return
        self.beginRemoveRows(QtCore.QModelIndex(), 0, len(self._items)-1)
        self._items = []
        self.endRemoveRows()'''

    def childCount(self, indexPath):
        #qDebug("Return len %d" % len(self._items))
        return len(self._items)

    @Slot(int,result=str)
    def dataStr(self,indexPath):
        return str(self.data(indexPath))

    @Slot(int,result=QObject)
    def data(self, indexPath):
        #qDebug("ListModel.data(%s)" % str(indexPath))
        try:
            if type(indexPath) == list:
                obj = self._items[indexPath[0]]
            else:
                obj = self._items[indexPath]
            #qDebug("Returning %s" % str(obj))
            return obj
        except Exception as e:
            qDebug(str(e))
        finally:
            #qDebug("returned")
            pass

    def list(self):
        return self._items

    def hasChildren(self, indexPath):
        return False

    def itemType(self, indexPath):
        return self._itemType

    def setItemType(self, itemType):
        self._itemType = itemType

    def __len__(self):
        return len(self._items)

    def __delitem__(self, index):
        #TODO
        '''self.beginRemoveRows(QtCore.QModelIndex(), index, index)
        del self._items[index]
        self.endRemoveRows()'''
        pass

    def __getitem__(self, key):
        return self._items[key]

class SortedList(ListModel):
    def setSourceModel(self, model):
        qDebug("Set sourcemodel")
        self.model = model
        model.itemAdded.connect(self.itemAdded)

    def childCount(self, indexPath):
        return self.model.childCount(indexPath)

    @Slot(int,result=QObject)
    def data(self, indexPath):
        return self.model.data(indexPath)

    def childCount(self, indexPath):
        #qDebug("Return len %d" % len(self._items))
        return self.model.childCount(indexPath)

    def resort(self):
        pass
    def reapplyFilter(self):
        pass

class SortedSeriesList(SortedList):
    def __init__(self, settings, parent=None):
        super(SortedSeriesList, self).__init__(parent=parent)
        #self.setItemType('series')

'''    def __init__(self, settings, parent=None):
        QtGui.QSortFilterProxyModel.__init__(self, parent)
        self._settings = settings
        self.sortOrder = self._settings.getConf(self._settings.SHOWS_SORT)
        self.hideCompleted = self._settings.getConf(self._settings.HIDE_COMPLETED_SHOWS)
        self.setDynamicSortFilter(True)
        self.sort(0)

    def resort(self):
        self.sortOrder = self._settings.getConf(self._settings.SHOWS_SORT)
        self.hideCompleted = self._settings.getConf(self._settings.HIDE_COMPLETED_SHOWS)
        self.invalidate()

    def reapplyFilter(self):
        self.resort()
        #This seems to be needed for QML to reload the filter. invalidateFilter doesn't seem to work
        self.reset()

    def filterAcceptsRow(self, sourceRow, sourceParent):
        if not self.hideCompleted:
            return True

        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        show = self.sourceModel().data(index)
        return not show.is_completely_watched()

    def lessThan(self, left, right):
        leftData = self.sourceModel().data(left)
        rightData = self.sourceModel().data(right)
        if (self.sortOrder == self._settings.BY_TITLE):
            return str(leftData) < str(rightData)
        #Sort completed last
        if rightData.is_completely_watched():
            if leftData.is_completely_watched():
                #Both complete, sort by title
                return str(leftData) < str(rightData)
            return True
        elif leftData.is_completely_watched():
            return False
        leftEpisodes = leftData.get_episodes_info()
        rightEpisodes = rightData.get_episodes_info()
        episode1 = leftEpisodes['next_episode']
        episode2 = rightEpisodes['next_episode']
        if not episode1:
            if not episode2:
                return str(leftData) < str(rightData)
            return False
        if not episode2:
            if episode1:
                return True
        if (self.sortOrder == self._settings.OLDEST_EPISODE):
            return episode1.air_date < episode2.air_date
        most_recent = (episode1 or episode2).get_most_recent(episode2)
        if not most_recent:
            return str(leftData) < str(rightData)
        return episode1 == most_recent'''

class SortedSeasonsList(SortedList):
    def __init__(self, l, settings, parent=None):
        super(SortedSeasonsList, self).__init__(parent=parent)
        self._settings = settings
        self.sortOrder = self._settings.getConf(self._settings.SEASONS_ORDER_CONF_NAME)
        self.setSourceModel(l)
        self.setItemType('seasons')
        qDebug(str(l))

'''
    def __init__(self, list, settings, parent=None):
        QtGui.QSortFilterProxyModel.__init__(self, parent)
        self.setDynamicSortFilter(True)
        self.sort(0)
        self.setSourceModel(list)

    def lessThan(self, left, right):
        if (self.sortOrder == self._settings.DESCENDING_ORDER):
            return int(self.sourceModel().data(left)) > int(self.sourceModel().data(right))
        return int(self.sourceModel().data(left)) < int(self.sourceModel().data(right))
'''
class SortedEpisodesList(SortedList):
    pass
'''
    def __init__(self, list, settings, parent=None):
        QtGui.QSortFilterProxyModel.__init__(self, parent)
        self._settings = settings
        self.setDynamicSortFilter(True)
        self.sortOrder = self._settings.getConf(self._settings.EPISODES_ORDER_CONF_NAME)
        self.sort(0)
        self.setSourceModel(list)

    def lessThan(self, left, right):
        if (self.sortOrder == self._settings.DESCENDING_ORDER):
            return self.sourceModel().data(left).episode_number > self.sourceModel().data(right).episode_number
        return self.sourceModel().data(left).episode_number < self.sourceModel().data(right).episode_number
'''
