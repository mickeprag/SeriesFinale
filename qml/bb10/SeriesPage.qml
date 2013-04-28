import bb.cascades 1.0

Page {
    signal showSelected(variant show)
    property variant currentShow: 42
    content: Container {
        background: nav.background
        layout: DockLayout {}
        Container {
            horizontalAlignment: HorizontalAlignment.Center
            visible: seriesList.length == 0
            ImageView {
                imageSource: "../assets/images/SeriesFinale_logo.png"
                verticalAlignment: VerticalAlignment.Center
                horizontalAlignment: HorizontalAlignment.Center
                scalingMethod: ScalingMethod.AspectFit
            }
            ImageView {
                imageSource: "../assets/images/SeriesFinale_intro.png"
                verticalAlignment: VerticalAlignment.Bottom
                horizontalAlignment: HorizontalAlignment.Center
                scalingMethod: ScalingMethod.AspectFit
                visible: !series_manager.busy
            }
            ActivityIndicator {
                running: true
                horizontalAlignment: HorizontalAlignment.Center
                visible: series_manager.busy
                preferredWidth: 100
            }
        }
        ListView {
            dataModel: seriesList
            function deleteShow(show) {
                series_manager.delete_show(show)
            }
            function updateShow(show) {
                series_manager.update_show_episodes(show)
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
                                ActionItem {
                                    title: "Refresh show"
                                    imageSource: "../assets/images/ic_refresh.png"
                                    onTriggered: itm.ListItem.view.updateShow(itm.ListItem.data)
                                }
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