import bb.cascades 1.0

Page {
    id: page
    signal episodeSelected(variant episode)
    property variant show: undefined
    property string season: ''
    content: Container {
        ImageView {
            imageSource: show ? show.bannerImage : ''
        }
        ListView {
            dataModel: show && season != '' ? show.get_sorted_episode_list_by_season(season) : undefined
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
