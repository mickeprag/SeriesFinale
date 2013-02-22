import bb.cascades 1.0

NavigationPane {
    id: nav
    SeriesPage {
        id: seriesPage
        onShowSelected: {
            showPage.show = show
            nav.push(showPage);
        }
        actions: [
            ActionItem {
                title: "Add show"
                imageSource: "../assets/images/ic_add.png"
                ActionBar.placement: ActionBarPlacement.OnBar
                onTriggered: nav.push(addShow)
            },
            ActionItem {
                title: "Refresh all"
                imageSource: "../assets/images/ic_refresh.png"
                ActionBar.placement: ActionBarPlacement.OnBar
                onTriggered: series_manager.update_all_shows_episodes()
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
        }
    ]
    
    Menu.definition: MenuDefinition {
        settingsAction: SettingsActionItem {
            onTriggered: nav.push(settingsPage)
        }
        actions: [
            ActionItem {
                title: "About"
                imageSource: "../assets/images/ic_info.png"
                onTriggered: nav.push(aboutPage)
            }
        ]
    }
}
