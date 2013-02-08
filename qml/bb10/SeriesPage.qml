import bb.cascades 1.0

Page {
    signal showSelected(variant show)
    property variant currentShow: 42
    
    content: Container {
        ListView {
            dataModel: seriesList
            listItemComponents: [
                ListItemComponent {
                    type: ""
                    StandardListItem {
                        title: ListItemData.showName
                        description: ListItemData.infoMarkup
                        status: "3"
                        imageSource: ListItemData.coverImage
                    }
                }
            ]
            onTriggered: {
                showSelected(dataModel.data(indexPath))
            }
        }
    }
}