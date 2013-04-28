import bb.cascades 1.0

Page {
    signal showAdded(string showName)
    titleBar: TitleBar {
        title: "Add show"
    }

    content: Container {
        background: nav.background
        TextField {
            id: searchTextField
            hintText: "Search"
            input {
                submitKey: SubmitKey.Search
                flags: TextInputFlag.SpellCheck | TextInputFlag.PredictionOff
                onSubmitted: { 
                    console.log("Search", searchTextField.text)
                    series_manager.search_shows(searchTextField.text)
                }
            }
        }
        ListView {
            dataModel: series_manager.search_result_model()
            listItemComponents: [
                ListItemComponent {
                    StandardListItem {
                        title: ListItemData
                    }
                }
            ]
            onTriggered: {
                showAdded(dataModel.dataStr(indexPath))
                searchTextField.text = ''
            }
        }
    }
}
