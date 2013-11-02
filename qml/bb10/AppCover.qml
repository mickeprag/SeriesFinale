import bb.cascades 1.0

Container {
    id: base
    layout: DockLayout {}
    background: Color.Black
    ImageView {
        imageSource: show ? 'file://' + show.coverImage : ''
        scalingMethod: ScalingMethod.AspectFit
    }

    Container {
        horizontalAlignment: HorizontalAlignment.Center
        verticalAlignment: VerticalAlignment.Top

        Container {
            preferredWidth: 300
            background: Color.create("#121212")
            layout: StackLayout {}
            opacity: 0.75

            Label {
                horizontalAlignment: HorizontalAlignment.Center
                text: show ? show.showName : 'SeriesFinale'
                textStyle { base: tsd.style; fontSizeValue: 8 }
            }
            Label {
                 horizontalAlignment: HorizontalAlignment.Left
                 text: show ? show.nextShowMarkup : ''
                 visible: show ? true : false
                 textStyle { base: tsd.style; fontSizeValue: 6 }
             }
         }
    }
    attachedObjects: [
        TextStyleDefinition {
            id: tsd
            fontWeight: FontWeight.Normal
            fontSize: FontSize.PointValue
            fontFamily: "Slate Pro"
        }
    ]
}
