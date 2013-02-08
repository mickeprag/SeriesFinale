import bb.cascades 1.0

Page {
    id: page
    signal episodeSelected(variant episode)
    property variant show: undefined
    property string season: ''
    content: Container {
        Label {
            id: labelID
            text: show? show.showName + ' Season ' + season : ''
        }
        ListView {
            dataModel: show && season != '' ? show.get_sorted_episode_list_by_season(season) : undefined
            property alias show: page.show
                                                    
            listItemComponents: [
                ListItemComponent {
                    type: ""
                    StandardListItem {
                        title: ListItem.data.title
                        description: ''
                        status: "3"
                        imageSource: "../assets/images/placeholderimage.png"
                        //imageSource: ListItemData.coverImage
                    }
                }
            ]
            onTriggered: {
                episodeSelected(dataModel.data(indexPath))
            }
        }
    }
}
