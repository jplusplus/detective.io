angular.module('detective.directive').directive 'homeTour', ["$window", ($window)->
    restrict : 'A'
    scope:
        tracker: "="
    link:
        post: (scope, element)->
            #  An event is fired to scroll to a given level
            scope.$on "tour:scrollTo", (ev, index)->
                if index > 0 and index <= 3
                    controller.scrollTo scenes[index].startPosition() + scenes[index].duration()
                else
                    controller.scrollTo scenes[index].startPosition() + 1
            # Constants
            QUOTE_DURATION = 300
            QUOTE_COUNT = 3
            QUOTE_SHOW = opacity: 1, marginTop: 0
            QUOTE_HIDE = opacity: 0, marginTop: -50
            # Entering closure function
            enter = (index)->->
                # Enter into an angular digest
                scope.$apply ->
                    # Update the parent scope attribute
                    angular.extend scope, tracker: index
            # Leaving closure function
            leave = (index)->->
                # Hide the selected quote
                TweenMax.to(".home__tour__quotes__single--n#{index}", 0.5, QUOTE_HIDE)
            # Init scrollmagic controller
            controller = new ScrollMagic()
            # Activate scrolling animation
            controller.scrollTo (newScrollPos)->
                $("html, body").animate scrollTop: newScrollPos
            scenes = []
            # ──────────────────────────────────────────────────────────────────────
            # First screen
            # ──────────────────────────────────────────────────────────────────────
            scenes.push new ScrollScene()
                .triggerHook(0.5)
                .triggerElement(".home__tour__front")
                .addTo(controller)
                .on("enter", enter 0)

            new ScrollScene()
                .triggerHook(0.5)
                .triggerElement(".home__tour__features")
                .addTo(controller)
                .on("enter", enter 0)

            # ──────────────────────────────────────────────────────────────────────
            # Quotes screens
            # ──────────────────────────────────────────────────────────────────────

            new ScrollScene()
                .triggerHook(0)
                .triggerElement(".home__tour__quotes")
                .duration(QUOTE_DURATION * (QUOTE_COUNT-1) )
                .setPin(".home__tour__quotes", pinnedClass: "home__tour__screen--pined")
                .addTo(controller)

            # Cascading quote appearance
            for n in [0.. QUOTE_COUNT - 1]
                # Create a scene
                scenes.push new ScrollScene()
                    .triggerHook(0)
                    .triggerElement(".home__tour__quotes")
                    .duration(QUOTE_DURATION)
                    .offset((n-1) * QUOTE_DURATION)
                    .setTween(
                        TweenMax.to(".home__tour__quotes__single--n#{n}", 0.5, QUOTE_SHOW)
                    )
                    .addTo(controller)
                    .on("enter", enter 1+n)
                    .on("leave", leave n)

            # ──────────────────────────────────────────────────────────────────────
            # Get-ready screen
            # ──────────────────────────────────────────────────────────────────────
            scenes.push new ScrollScene()
                .triggerElement(".home__tour__get-ready")
                .triggerHook(0.5)
                .duration(600*4)
                .setTween(
                    TweenMax.fromTo ".home__tour__get-ready__ipad", 1, {top:  100}, {top:  -400}
                )
                .addTo(controller)
                .on("enter", enter QUOTE_COUNT+1)

            # ──────────────────────────────────────────────────────────────────────
            # Pricing screen
            # ──────────────────────────────────────────────────────────────────────
            scenes.push new ScrollScene()
                .triggerHook(0.5)
                .triggerElement(".home__tour__pricing")
                .addTo(controller)
                .on("enter", enter QUOTE_COUNT+2)

]