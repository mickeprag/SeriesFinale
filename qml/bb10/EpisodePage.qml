import bb.cascades 1.0

Page {
    id: page
    property variant episode: undefined
    titleBar: TitleBar {
        title: episode? episode.title : ''
    }

    content: Container {
        bottomPadding: 15
        leftPadding: 15
        rightPadding: 15
        Container {
            layout: StackLayout {
                orientation: LayoutOrientation.LeftToRight
            }
            ImageView {
                imageSource: episode ? 'file:///' + episode.coverImage : ''
                scalingMethod: ScalingMethod.AspectFit
            }
            Container {
                Label {
                    text: '<b>Air date:</b><br />' + (episode ? episode.airDateText : '')
                    textFormat: TextFormat.Html
                    multiline: true
                }
                Label {
                    text: '<b>Rating:</b><br />' + (episode ? episode.episodeRating : '')
                    textFormat: TextFormat.Html
                    multiline: true
                }
            }
        }
        Divider {
        }
        Label {
            text: episode ? episode.overviewText : ''
            multiline: true
            layoutProperties: StackLayoutProperties {
                spaceQuota: 1
            }
        }
        CheckBox {
            id: watched
            text: "Watched"
            onCheckedChanged: episode.isWatched = watched.checked
            property bool isWatched: episode ? episode.isWatched : false
            onIsWatchedChanged: watched.checked = episode.isWatched
            bottomMargin: 10.0
        }
    }
}
