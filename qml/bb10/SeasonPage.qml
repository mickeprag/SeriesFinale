import bb.cascades 1.0

Page {
    id: page
    signal episodeSelected(variant episode)
    property variant show: undefined
    property string season: ''
    onShowChanged: listView.dataModel = show.get_sorted_episode_list_by_season(season)
    onSeasonChanged: listView.dataModel = show.get_sorted_episode_list_by_season(season)
    content: Container {
        background: nav.background
        ImageView {
            imageSource: show ? show.bannerImage : ''
        }
        ListView {
            id: listView
            property alias show: page.show
            listItemComponents: [
                ListItemComponent {
                    EpisodeListItem {
                        episode: ListItem.data
                    }
                }
            ]
            onTriggered: {
                episodeSelected(dataModel.data(indexPath))
            }
        }
    }
}
