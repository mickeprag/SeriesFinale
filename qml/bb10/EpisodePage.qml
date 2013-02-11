import bb.cascades 1.0

Page {
    id: page
    property variant episode: undefined

    content: Container {
        Label {
            id: labelID
            text: episode? episode.title : ''
        }
        CheckBox {
            id: watched
            text: "Watched"
            onCheckedChanged: episode.isWatched = watched.checked
            property bool isWatched: episode.isWatched
            onIsWatchedChanged: watched.checked = episode.isWatched
        }
    }
}
