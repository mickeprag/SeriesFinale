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
from PySide.QtCore import qDebug, QObject, Slot, QThread, Signal, Property

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
            if show.thread() != self.thread():
                show.moveToThread(self.thread())
            if (show.parent() == None):
                #If we do not have a parent the item the ListView
                #will reparent the object which will not work.
                show.setParent(self)
        self._items.append(show)
        self.itemAdded.emit([len(self._items)-1])

    def clear(self):
        # Since the signal DataModel::itemChanged doesn't work in PyCascades we have to do it this way instead
        while len(self):
            del self[0]

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

    # For source compatibility with Qt
    def index(self, sourceRow, sourceColumn, sourceParent):
        return sourceRow

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
        del self._items[index]
        self.itemRemoved.emit([index])

    def __getitem__(self, key):
        return self._items[key]

class SortedList(bb.cascades.DataModel):
    def setSourceModel(self, model):
        self.model = model
        self._sortOrder = []
        model.itemAdded.connect(self._itemAdded)
        model.itemAdded.connect(self.lengthChanged)
        model.itemRemoved.connect(self._itemRemoved)
        model.itemRemoved.connect(self.lengthChanged)
        for index, data in enumerate(model):
            self._itemAdded([index])

    def childCount(self, indexPath = None):
        return len(self._sortOrder)
    lengthChanged = Signal()
    length = Property(int,childCount,notify=lengthChanged)

    @Slot(int,result=QObject)
    def data(self, indexPath):
        return self.model.data(self.mapToSource(indexPath))

    @Slot(int,result=str)
    def dataStr(self,indexPath):
        return self.model.dataStr(self.mapToSource(indexPath))

    def hasChildren(self, indexPath):
        return False

    def mapToSource(self, index):
        if type(index) == list:
            index = index[0]
        if index >= len(self._sortOrder):
            # Should not happen
            return 0
        return self._sortOrder[index]

    def sourceModel(self):
        return self.model

    @Slot(list)
    def _itemAdded(self, indexPath):
        index = indexPath[0]
        if not self.filterAcceptsRow(index, 0):
            return
        before = None
        left = index
        for i, right in enumerate(self._sortOrder):
            if self.lessThan(left, right):
                before = i
                break
        if before == None:
            self._sortOrder.append(index)
            self.itemAdded.emit([len(self._sortOrder)-1])
        else:
            self._sortOrder.insert(before, index)
            self.itemAdded.emit([before])

    @Slot(list)
    def _itemRemoved(self, indexPath):
        sourceIndex = indexPath[0]
        if sourceIndex not in self._sortOrder:
            return
        index = self._sortOrder.index(sourceIndex)
        del self._sortOrder[index]
        self.itemRemoved.emit([index])
        for i, item in enumerate(self._sortOrder):
            if item > sourceIndex:
                self._sortOrder[i] = self._sortOrder[i]-1

    def resort(self):
        pass
    def reapplyFilter(self):
        pass
    def filterAcceptsRow(self, sourceRow, sourceParent):
        return True
    def lessThan(self, left, right):
        return True

class SortedSeriesList(SortedList):
    def __init__(self, settings, parent=None):
        super(SortedSeriesList, self).__init__(parent=parent)
        self._settings = settings
        self.hideCompleted = self._settings.getConf(self._settings.HIDE_COMPLETED_SHOWS)
        self.sortOrder = self._settings.getConf(self._settings.SHOWS_SORT)

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
        return episode1 == most_recent

'''    def resort(self):
        self.sortOrder = self._settings.getConf(self._settings.SHOWS_SORT)
        self.hideCompleted = self._settings.getConf(self._settings.HIDE_COMPLETED_SHOWS)
        self.invalidate()

    def reapplyFilter(self):
        self.resort()
        #This seems to be needed for QML to reload the filter. invalidateFilter doesn't seem to work
        self.reset()'''


class SortedSeasonsList(SortedList):
    def __init__(self, list, settings, parent=None):
        super(SortedSeasonsList, self).__init__(parent=parent)
        self._settings = settings
        self.sortOrder = self._settings.getConf(self._settings.SEASONS_ORDER_CONF_NAME)
        self.setSourceModel(list)

    def lessThan(self, left, right):
        if (self.sortOrder == self._settings.DESCENDING_ORDER):
            return int(self.sourceModel().data(left)) > int(self.sourceModel().data(right))
        return int(self.sourceModel().data(left)) < int(self.sourceModel().data(right))

class SortedEpisodesList(SortedList):
    def __init__(self, list, settings, parent=None):
        super(SortedEpisodesList, self).__init__(parent=parent)
        self._settings = settings
        self.sortOrder = self._settings.getConf(self._settings.EPISODES_ORDER_CONF_NAME)
        self.setSourceModel(list)

    def lessThan(self, left, right):
        if (self.sortOrder == self._settings.DESCENDING_ORDER):
            return self.sourceModel().data(left).episode_number > self.sourceModel().data(right).episode_number
        return self.sourceModel().data(left).episode_number < self.sourceModel().data(right).episode_number
