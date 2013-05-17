import bb.cascades 1.0

Container {
    property variant episode
    property bool loading: true
    Divider {}
    Container {
        layout: StackLayout {
            orientation: LayoutOrientation.LeftToRight
        }
        leftPadding: 35
        CheckBox {
            id: watched
            verticalAlignment: VerticalAlignment.Center
            rightMargin: 35
            onCheckedChanged: episode.isWatched = watched.checked
            property bool isWatched: episode.isWatched
            onIsWatchedChanged: watched.checked = episode.isWatched
        }
        Container {
            leftPadding: 25
            verticalAlignment: VerticalAlignment.Center
            layoutProperties: StackLayoutProperties {
                spaceQuota: 1
            }
            Label {
                text: episode.title
                verticalAlignment: VerticalAlignment.Center
                textStyle {
                    base: SystemDefaults.TextStyles.TitleText
                    fontWeight: FontWeight.Bold
                    color: {
                        if (episode.isWatched) {
                            return Color.Gray
                        } else if (episode.already_aired()) {
                            return Color.White
                        }
                        return Color.DarkGray
                    }
                }
            }
            Label {
                id: descriptionLabel
                text: episode.airDateText
                textFormat: TextFormat.Html
                multiline: true
                textStyle {
                    base: SystemDefaults.TextStyles.TitleText
                    color: Color.Gray
                    fontSize: FontSize.Small
                }
                visible: text != ''
            }
        }
        ImageView {
            imageSource: "asset:///images/ic_next.png"
            verticalAlignment: VerticalAlignment.Center
        }
    }
    Divider {}
}
