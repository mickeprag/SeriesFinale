import QtQuick 1.1
import com.nokia.meego 1.0

Item {
    id: epListItem
    height: 88
    anchors.left: parent.left
    anchors.right: parent.right
    clip: true

    signal clicked
    signal pressAndHold
    signal watchToggled(bool watched)
    property alias title: title.text
    property alias subtitle: subtitle.text
    property alias iconSource: icon.source
    property variant episode: undefined

    states: [
        State {
            name: 'watched'; when: episode.isWatched
            PropertyChanges {
                target: epListItem;
                iconSource: 'image://theme/icon-m-common-done'
            }
        },
        State {
            when: !episode.isWatched
            PropertyChanges {
                target: epListItem;
                iconSource: 'image://theme/icon-m-common-aqua'
            }
        }
    ]

    BorderImage {
        id: background
        anchors.fill: parent
        visible: episodeMouseArea.pressed
        source: "image://theme/meegotouch-list-background-pressed-center"
    }

    Row {
        anchors.fill: parent
        anchors.leftMargin: 16
        spacing: 18

        Image {
            id: icon
            anchors.verticalCenter: parent.verticalCenter
            width: 64
            height: 64
            fillMode: "PreserveAspectFit"
            smooth: true
            source: episode.isWatched ? 'image://theme/icon-m-common-done' : 'image://theme/icon-m-common-aqua'
            visible: source != ''

            MouseArea {
                id: iconMouseArea
                anchors.fill: parent
                onClicked: {
                    episode.isWatched = !episode.isWatched
                    epListItem.watchToggled(episode.isWatched)
                }
                onPressAndHold: epListItem.pressAndHold()
            }
        }

        Column {
            id: column
            anchors.verticalCenter: parent.verticalCenter

            Label {
                id: title
                font.weight: Font.Bold
                font.pixelSize: 26
                color: theme.inverted ? "#ffffff" : "#282828"
                text: episode.title
            }

            Label {
                id: subtitle
                font.weight: Font.Light
                font.pixelSize: 22
                color: theme.inverted ? "#d2d2d2" : "#505050"
                text: episode.airDateText
                visible: text != ""
            }
        }
    }

    Image {
        source: "image://theme/icon-m-common-drilldown-arrow" + (theme.inverted ? "-inverse" : "")
        anchors.right: parent.right;
        anchors.verticalCenter: parent.verticalCenter
    }

    MouseArea {
        id: episodeMouseArea
        x: column.x
        y: 0
        width: parent.width
        height: parent.height
        onClicked: epListItem.clicked()
        onPressAndHold: epListItem.pressAndHold()
    }

}