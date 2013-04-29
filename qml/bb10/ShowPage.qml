import bb.cascades 1.0

Page {
    id: page
    signal seasonSelected(string season)
    property variant show: undefined
    onShowChanged: listView.dataModel = show.get_seasons_model()
    
    content: Container {
        background: nav.background
        Container {
            layout: DockLayout {
            }
            ImageView {
                id: banner
                imageSource: show ? show.bannerImage : ''
            }
            ActivityIndicator {
                verticalAlignment: VerticalAlignment.Center
                horizontalAlignment: HorizontalAlignment.Right
                running: true
                preferredHeight: 150
                visible: show ? show.busy : false
            }
        }
        ListView {
            id: listView
            property alias show: page.show
            function markAll(season) {
                show.mark_all_episodes_as_watched(season)
            }
            function markNone(season) {
                show.mark_all_episodes_as_not_watched(season)
            }

            listItemComponents: [
                ListItemComponent {
                    SeriesListItem {
                        id: itm
                        title: ListItem.view.show.get_season_name(ListItem.data)
                        description: ListItem.view.show.get_season_info_markup(ListItem.data)
                        width: 100
                        imageSource: 'file://' + ListItem.view.show.get_season_image(ListItem.data)
                        contextActions: [
                            ActionSet {
                                title: itm.ListItem.view.show.showName
                                subtitle: itm.ListItem.view.show.get_season_name(itm.ListItem.data)
                                ActionItem {
                                    title: "Mark all as watched"
                                    imageSource: "../assets/images/ic_select.png"
                                    onTriggered: itm.ListItem.view.markAll(itm.ListItem.data)
                                }
                                ActionItem {
                                    title: "Mark none as watched"
                                    imageSource: "../assets/images/ic_select_none.png"
                                    onTriggered: itm.ListItem.view.markNone(itm.ListItem.data)
                                }
                            }
                        ]
                    }
                }
            ]
            onTriggered: {
                seasonSelected(dataModel.dataStr(indexPath))
            }
        }
    }
    actions: [
        ActionItem {
            title: "Refresh"
            imageSource: "../assets/images/ic_refresh.png"
            ActionBar.placement: ActionBarPlacement.OnBar
            onTriggered: series_manager.update_show_episodes(show)
        }
    ]
}
