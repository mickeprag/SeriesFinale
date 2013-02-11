import bb.cascades 1.0

NavigationPane {
    id: nav
    SeriesPage {
        id: seriesPage
        onShowSelected: {
            showPage.show = show
            nav.push(showPage);
        }
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
                episodePage.episode = episode
                nav.push(episodePage)
            }
        },
        EpisodePage {
            id: episodePage
        }
    ]
    
    Menu.definition: MenuDefinition {
        actions: [
            ActionItem {
                title: "Refresh all"
                imageSource: "../assets/images/ic_refresh.png"
                onTriggered: series_manager.update_all_shows_episodes()
            }
        ]
    }
}
