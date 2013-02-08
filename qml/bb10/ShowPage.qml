import bb.cascades 1.0

Page {
    id: page
    signal seasonSelected(string season)
    property variant show: undefined
    
    titleBar: TitleBar {
        title: show? show.showName : ''
    }
    content: Container {
        ListView {
            dataModel: show ? show.get_seasons_model() : undefined
            property alias show: page.show
                                                    
            listItemComponents: [
                ListItemComponent {
                    type: ""
                    StandardListItem {
                        title: ListItem.view.show.get_season_name(ListItem.data)
                        description: ''
                        status: "3"
                        imageSource: "../assets/images/placeholderimage.png"
                        //imageSource: ListItemData.coverImage
                    }
                }
            ]
            onTriggered: {
                seasonSelected(dataModel.dataStr(indexPath))
            }
        }
    }
}
