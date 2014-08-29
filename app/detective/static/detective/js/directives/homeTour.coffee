angular.module('detective.directive').directive 'homeTour', ->
    restrict : 'A'
    compile: (scope, element, attr, ngModel) ->
        # Init scrollmagic controller
        controller = new ScrollMagic
            globalSceneOptions:
                triggerHook: 0
        # Quote settings
        QUOTE_DURATION = 600
        QUOTE_COUNT = 3
        # Build scene
        quotesScene = new ScrollScene(
                triggerElement: ".home__tour__quotes"
                duration: QUOTE_DURATION * (QUOTE_COUNT + QUOTE_COUNT-1)
            )
            .setPin(".home__tour__quotes", pinnedClass: "home__tour__screen--pined")
            .addTo(controller)

        showStyle =
            opacity: 1
            marginTop: 0
        hideStyle =
            opacity: 0
            marginTop: -50
        # Cascading quote appearance
        for n in [0.. QUOTE_COUNT - 1]
            tweening = new TimelineMax()
            # There is a quote before
            if n > 0
                # Hide the previous
                tweening.add TweenMax.to(".home__tour__quotes__single--n#{n - 1}", 0.5, hideStyle)
            # Show the current quote
            tweening.add TweenMax.to(".home__tour__quotes__single--n#{n}", 0.5, showStyle)
            # Early offset for the first element
            offset = if n is 0 then -QUOTE_DURATION/2 else (n + n-1) * QUOTE_DURATION
            # Create a scene
            new ScrollScene()
                .triggerElement(".home__tour__quotes")
                .duration(QUOTE_DURATION)
                .offset(offset)
                .setTween(tweening)
                .addTo(controller)
