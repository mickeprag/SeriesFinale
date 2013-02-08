import bb.cascades 1.0

Page {
    id: page
    property variant episode: undefined

    content: Container {
        Label {
            id: labelID
            text: episode? episode.title : ''
        }
    }
}
