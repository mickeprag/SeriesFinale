import bb.cascades 1.0

Page {
    id: page
    property variant episode: undefined
    property variant show: undefined
    titleBar: TitleBar {
        title: episode? episode.title : ''
    }

    content: Container {
        background: nav.background
        Container {
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
                    Header {
                        title: 'Air date:'
                    }
                    Label {
                        text: (episode ? episode.airDateText : '')
                    }
                    Header {
                        title: 'Rating:'
                    }
                    Label {
                        text: (episode ? episode.episodeRating : '')
                    }
                }
            }
            Divider {
            }
            ScrollView {
                scrollViewProperties.scrollMode: ScrollMode.Vertical
                scrollViewProperties.pinchToZoomEnabled: false
                layoutProperties: StackLayoutProperties {
                    spaceQuota: 1
                }
                content: Label {
                    text: episode ? episode.overviewText : ''
                    multiline: true
                    layoutProperties: StackLayoutProperties {
                        spaceQuota: 1
                    }
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

    actions: [
        ActionItem {
            title: "Previous"
            imageSource: "asset:///images/ic_up.png"
            ActionBar.placement: ActionBarPlacement.OnBar
            onTriggered: episode = show.get_previous_episode(episode)
        },
        ActionItem {
            title: "Next"
            imageSource: "asset:///images/ic_down.png"
            ActionBar.placement: ActionBarPlacement.OnBar
            onTriggered: episode = show.get_next_episode(episode)
        },
        InvokeActionItem {
            id: invoke
            title: "Show on IMDb"
            imageSource: "asset:///images/imdblogo_55x29.png"
            enabled: (episode ? episode.imdbId != '' : false)
            query {
                mimeType: "text/html"
                uri: "http://www.imdb.com/title/" + (episode ? episode.imdbId : '')
                onQueryChanged: invoke.query.updateQuery()
                invokeActionId: "bb.action.OPEN"
            }
            ActionBar.placement: ActionBarPlacement.OnBar
        }
    ]
}
