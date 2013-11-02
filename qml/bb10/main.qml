import bb.cascades 1.0

NavigationPane {
    id: nav
    property alias background: tile.imagePaint
    SeriesPage {
        id: seriesPage
        onShowSelected: {
            activeFrame.setShow(show)
            showPage.show = show
            nav.push(showPage);
        }
        actions: [
            ActionItem {
                title: "Add show"
                imageSource: "asset:///images/ic_add.png"
                ActionBar.placement: ActionBarPlacement.OnBar
                onTriggered: nav.push(addShow)
            },
            ActionItem {
                title: "Refresh all"
                imageSource: "asset:///images/ic_refresh.png"
                ActionBar.placement: ActionBarPlacement.OnBar
                onTriggered: series_manager.update_all_shows_episodes()
            },
            ActionItem {
                title: "Invite to Download"
                imageSource: "asset:///images/ic_bbm.png"
                ActionBar.placement: ActionBarPlacement.InOverflow
                onTriggered: bbm.invite_to_download()
            }
        ]
    }

    attachedObjects: [
        ShowPage {
            id: showPage
            onSeasonSelected: {
                seasonPage.season = season
                seasonPage.show = show
                nav.push(seasonPage)
            }
        },
        SeasonPage {
            id: seasonPage
            onEpisodeSelected: {
                episodePage.show = show
                episodePage.episode = episode
                nav.push(episodePage)
            }
        },
        EpisodePage {
            id: episodePage
        },

        SettingsPage {
            id: settingsPage
        },
        AboutPage {
            id: aboutPage
        },
        AddShow {
            id: addShow
            onShowAdded: {
                series_manager.get_complete_show(showName)
                nav.pop();
            }
        },
        ImagePaintDefinition {
            id: tile
            repeatPattern: RepeatPattern.XY
            imageSource: "asset:///images/SeriesFinale_bg.amd"
        }
    ]
    
    Menu.definition: MenuDefinition {
        settingsAction: SettingsActionItem {
            onTriggered: nav.push(settingsPage)
        }
        actions: [
            ActionItem {
                title: "About"
                imageSource: "asset:///images/ic_info.png"
                onTriggered: nav.push(aboutPage)
            }
        ]
    }
}
