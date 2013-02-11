import bb.cascades 1.0

Container {
    property alias title: titleLabel.text
    property alias description: descriptionLabel.text
    property alias imageSource: coverImage.imageSource
    property int width: 150
    
    preferredHeight: coverImage.height
    
    Container {
        layout: StackLayout {
            orientation: LayoutOrientation.LeftToRight
        }
        ImageView {
            id: coverImage
            verticalAlignment: VerticalAlignment.Center
            preferredWidth: width
            minWidth: width
            scalingMethod: ScalingMethod.AspectFit
        }
        Container {
            leftPadding: 25
            verticalAlignment: VerticalAlignment.Center
            layoutProperties: StackLayoutProperties {
                spaceQuota: 1
            }
            Label {
                id: titleLabel
                verticalAlignment: VerticalAlignment.Center
                textStyle {
                    base: SystemDefaults.TextStyles.TitleText
                    fontWeight: FontWeight.Bold
                }
            }
            Label {
                id: descriptionLabel
                textFormat: TextFormat.Html
                multiline: true
                textStyle {
                    base: SystemDefaults.TextStyles.TitleText
                    color: Color.Gray
                    fontSize: FontSize.Small
                }
                visible: text != ''
            }
        }
        ImageView {
            imageSource: "../assets/images/ic_next.png"
            verticalAlignment: VerticalAlignment.Center
        }
    }
    Divider {}
}
