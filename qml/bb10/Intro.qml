import bb.cascades 1.0

Container {
    layout: DockLayout {}
    verticalAlignment: VerticalAlignment.Fill
    horizontalAlignment: HorizontalAlignment.Fill
    ImageView {
        imageSource: "asset:///images/SeriesFinale_logo.png"
        verticalAlignment: VerticalAlignment.Top
        horizontalAlignment: HorizontalAlignment.Center
        scalingMethod: ScalingMethod.AspectFit
    }
    ActivityIndicator {
        running: true
        horizontalAlignment: HorizontalAlignment.Center
        verticalAlignment: VerticalAlignment.Center
        visible: series_manager.busy
        preferredWidth: 150
    }
    ImageView {
        imageSource: "asset:///images/SeriesFinale_intro.png"
        verticalAlignment: VerticalAlignment.Bottom
        horizontalAlignment: HorizontalAlignment.Center
        scalingMethod: ScalingMethod.AspectFit
        visible: !series_manager.busy
    }
}
