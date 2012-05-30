import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: page
    property variant show: undefined

    Dialog {
        id: showInfoDialog
        anchors.fill: parent
        anchors.verticalCenter: parent.verticalCenter

        content: Item {
            id: contents
            width: parent.width * .8
            height: page.height
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter

            Flickable {
                id: flickableContent
                width: parent.width
                height: parent.height
                contentHeight: showInfoDescription.height + titleItem.height
                contentWidth: width

                Item {
                    id: titleItem
                    width: parent.width
                    height: showNameText.height + 5

                    Text {
                        id: showNameText
                        text: show.showName
                        font.family: "Nokia Pure Text Light"
                        font.pixelSize: 26
                        font.weight: Font.Bold
                        color: 'white'
                        wrapMode: Text.WordWrap
                        width: parent.width - closeIcon.width - 10
                    }

                    Image {
                        id: closeIcon
                        source: "image://theme/icon-m-common-dialog-close"
                        anchors.right: parent.right;
                        anchors.verticalCenter: parent.verticalCenter

                        MouseArea {
                            anchors.fill: parent
                            onClicked: showInfoDialog.close()
                        }
                    }

                    Rectangle {
                        anchors.top: parent.bottom
                        width: parent.width
                        height: 1
                        color: 'white'
                    }
                }

                Image {
                    id: showCover
                    source: show.coverImage
                    height: 300
                    fillMode: "PreserveAspectFit"
                    smooth: true
                    anchors.top: titleItem.bottom
                    anchors.topMargin: 10
                    anchors.horizontalCenter: rootWindow.inPortrait ? parent.horizontalCenter : undefined
                    anchors.left: !rootWindow.inPortrait ? parent.left : undefined

                }

                Text {
                    id: showInfoDescription
                    width: parent.width
                    anchors.top: rootWindow.inPortrait ? showCover.bottom : showCover.top
                    anchors.right: parent.right
                    anchors.left: rootWindow.inPortrait ? parent.left : showCover.right
                    anchors.leftMargin: 10
                    text: show.showOverview
                    font.weight: Font.Light
                    font.pixelSize: 22
                    color: theme.inverted ? secondaryTextColor : "#505050"
                    wrapMode: Text.Wrap
                }
            }
            ScrollDecorator{ flickableItem: flickableContent }
            }

    }


        Header {
            id: header
            text: show.showName
            busy: show.busy
            hasRefreshAction: true
            onRefreshActionActivated: series_manager.update_show_episodes(show)
            textWidth: header.width - infoIcon.width * 2.5

            Item {
                id: infoIconItem
                height: parent.height
                width: infoIcon.width
                anchors.right: header.anchorPoint
                anchors.rightMargin: 20

                Image {
                    id: infoIcon
                    source: 'icons/info-icon.png'
                    fillMode: "PreserveAspectFit"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
            MouseArea {
                anchors.left: parent.left
                anchors.right: infoIconItem.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: parent.width - infoIcon.width - 20
                height: parent.height
                onClicked: showInfoDialog.open()
            }
        }

    ListView {
        id: listView
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        clip: true
        model: show.get_seasons_model()
        delegate: ListRowDelegate {
            id: delegate
            title: show.get_season_name(model.data)
            subtitle: show.get_season_info_markup(model.data)
            iconSource: show.get_season_image(model.data)
            Connections {
                target: show
                onInfoMarkupChanged: {
                    subtitle = show.get_season_info_markup(model.data)
                    markAllItem.text = show.is_completely_watched(model.data) ? 'Mark None' : 'Mark All'
                }
                onShowArtChanged: iconSource = show.get_season_image(model.data)
                onEpisodesListUpdated: listView.model = show.get_seasons_model()
            }

            Component {
                id: seasonPageComponent
                SeasonPage { show: page.show; season: model.data }
            }
            ContextMenu {
                id: contextMenu
                MenuLayout {
                    MenuItem {
                        id: markAllItem
                        text: show.is_completely_watched(model.data) ? 'Mark None' : 'Mark All'
                        onClicked: {
                            show.is_completely_watched(model.data) ? page.show.mark_all_episodes_as_not_watched(model.data) : page.show.mark_all_episodes_as_watched(model.data)
                            delegate.subtitle = show.get_season_info_markup(model.data);
                        }
                    }
                    MenuItem {
                        text: "Delete season";
                        onClicked: {
                            show.delete_season(model.data)
                            listView.model = show.get_seasons_model()
                        }
                    }
                }
            }
            onClicked: pageStack.push(seasonPageComponent.createObject(pageStack))
            onPressAndHold: contextMenu.open()
        }
    }
    ScrollDecorator{ flickableItem: listView }

    tools: ToolBarLayout {
        ToolIcon { iconId: "toolbar-back"; onClicked: { pageStack.pop() } }
    }

    states: [
        State {
            name: "inLandscape"
            when: !rootWindow.inPortrait
            AnchorChanges {
                target: showCover
                anchors.horizontalCenter: undefined
                anchors.left: showCover.parent.left
            }
            AnchorChanges {
                target: showInfoDescription
                anchors.left: showCover.right
            }
            PropertyChanges {
                target: flickableContent
                contentHeight: showCover.height < showInfoDescription.height ? showInfoDescription.height + titleItem.height : showCover.height + titleItem.height
            }
        },
        State {
            name: "inPortrait"
            when: rootWindow.inPortrait
            AnchorChanges {
                target: showCover
                anchors.left: undefined
                anchors.horizontalCenter: showCover.parent.horizontalCenter
            }
            AnchorChanges {
                target: showInfoDescription
                anchors.left: showInfoDescription.parent.left
                anchors.top: showCover.bottom
            }
            PropertyChanges {
                target: flickableContent
                contentHeight: showCover.height + showInfoDescription.height + titleItem.height
            }
        }
    ]
}
