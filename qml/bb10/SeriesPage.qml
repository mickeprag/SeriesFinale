import bb.cascades 1.0

Page {
    signal showSelected(variant show)
    property variant currentShow: 42
    
    content: Container {
        ListView {
            dataModel: seriesList
            function deleteShow(show) {
                series_manager.delete_show(show)
            }
            listItemComponents: [
                ListItemComponent {
                    type: ""
                    SeriesListItem {
                        id: itm
                        title: ListItemData.showName
                        description: ListItemData.infoMarkup
                        imageSource: 'file://' + ListItemData.coverImage
                        busy: ListItemData.busy
                        contextActions: [
                            ActionSet {
                                title: ListItemData.showName
                                DeleteActionItem {
                                    title: "Delete show"
                                    onTriggered: itm.ListItem.view.deleteShow(itm.ListItem.data)
                                }
                            }
                        ]
                    }
                }
            ]
            onTriggered: {
                showSelected(dataModel.data(indexPath))
            }
        }
    }
}