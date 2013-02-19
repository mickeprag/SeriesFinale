import bb.cascades 1.0

Page {
    id: page
    content: Container {
        Label {
            text: "Sort shows by:"
            textStyle.fontSize: FontSize.XLarge
        }
        SegmentedControl {
            options: [
                Option {
                    text: "Title"
                    selected: settings.showsSort == 0
                },
                Option {
                    text: "Newest"
                    selected: settings.showsSort == 1
                },
                Option {
                    text: "Oldest"
                    selected: settings.showsSort == 2
                }
            ]
            onSelectedIndexChanged: settings.showsSort = selectedIndex
        }
        Label {
            text: "Episode sorting:"
            textStyle.fontSize: FontSize.XLarge
        }
        SegmentedControl {
            options: [
                Option {
                    text: "1-9"
                    selected: settings.episodesOrder == 0
                },
                Option {
                    text: "9-1"
                    selected: settings.episodesOrder == 1
                }
            ]
            onSelectedIndexChanged: settings.episodesOrder = selectedIndex
        }
        CheckBox {
            text: "Add special seasons:"
            onCheckedChanged: settings.addSpecialSeasons = checked
            property bool addSpecialSeasons: settings.addSpecialSeasons
            onAddSpecialSeasonsChanged: checked = settings.addSpecialSeasons
        }
        CheckBox {
            text: "Hide completely watched:"
            onCheckedChanged: settings.hideCompletedShows = checked
            property bool hideComplededShows: settings.hideCompletedShows
            onHideComplededShowsChanged: checked = settings.hideCompletedShows
            
        }
    }
}
