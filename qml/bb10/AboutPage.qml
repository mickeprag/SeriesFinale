import bb.cascades 1.0

Page {
    id: aboutPage

    property string license: 'SeriesFinale is free software: you can redistribute it ' +
'and/or modify it under the terms of the GNU General Public License as published by ' +
'the Free Software Foundation, either version 3 of the License, or ' +
'(at your option) any later version.<br/><br/>' +

'SeriesFinale is distributed in the hope that it will be useful, ' +
'but WITHOUT ANY WARRANTY; without even the implied warranty of ' +
'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the ' +
'GNU General Public License for more details.<br/><br/>' +

'You should have received a copy of the GNU General Public License ' +
'along with SeriesFinale.  If not, see <a href="http://www.gnu.org/licenses/">http://www.gnu.org/licenses/</a>.'

    content: Container {
        background: nav.background
        topPadding: 30
        leftPadding: 15
        rightPadding: 15
        bottomPadding: 15
        Container {
            layout: StackLayout {
                orientation: LayoutOrientation.LeftToRight
            }
            ImageView {
                imageSource: "asset:///images/seriesfinale.png"
                preferredWidth: 150
                scalingMethod: ScalingMethod.AspectFit
                verticalAlignment: VerticalAlignment.Center
            }
            Container {
                layoutProperties: StackLayoutProperties {
                    spaceQuota: 1
                }
                verticalAlignment: VerticalAlignment.Center
                horizontalAlignment: HorizontalAlignment.Center
                Label {
                    text: 'SeriesFinale ' + series_manager.version
                    horizontalAlignment: HorizontalAlignment.Center
                    textStyle {
                        base: SystemDefaults.TextStyles.TitleText
                        fontWeight: FontWeight.Bold
                    }
                }
                Label {
                    text: 'BlackBerry 10 Edition'
                    horizontalAlignment: HorizontalAlignment.Center
                    textStyle {
                        base: SystemDefaults.TextStyles.TitleText
                        fontWeight: FontWeight.Bold
                    }
                }
            }
        }
        Label {
            text: "<strong>Developed by:</strong> Micke Prag<br />This port is based on the initial work made by Joaquim Rocha"
            multiline: true
            textFormat: TextFormat.Html
        }
        Divider {
        }
        ScrollView {
            scrollViewProperties.scrollMode: ScrollMode.Vertical
            scrollViewProperties.pinchToZoomEnabled: false
            layoutProperties: StackLayoutProperties {
                spaceQuota: 1
            }
            content: Container {
                Label {
                    text: 'SeriesFinale uses <a href="http://www.thetvdb.com">TheTVDB</a> API but is not endorsed or certified by TheTVDB. Please contribute to it if you can.'
                    multiline: true
                    textFormat: TextFormat.Html
                }
                Label {
                    text: license
                    multiline: true
                    textFormat: TextFormat.Html
                }
            }
        }
    }
}
