import bb.cascades 1.0

Page {
    id: page
    signal seasonSelected(string season)
    property variant show: undefined
    onShowChanged: listView.dataModel = show.get_seasons_model()
    
    content: Container {
        ImageView {
            imageSource: show ? show.bannerImage : ''
        }
        ListView {
            id: listView
            property alias show: page.show

            listItemComponents: [
                ListItemComponent {
                    SeriesListItem {
                        title: ListItem.view.show.get_season_name(ListItem.data)
                        description: ListItem.view.show.get_season_info_markup(ListItem.data)
                        width: 100
                        imageSource: 'file://' + ListItem.view.show.get_season_image(ListItem.data)
                    }
                }
            ]
            onTriggered: {
                seasonSelected(dataModel.dataStr(indexPath))
            }
        }
    }
}
