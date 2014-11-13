angular.module('detective.directive').directive 'homeTour', ["$window", ($window)->
    restrict : 'A'
    scope:
        tracker: "="
    link:
        post: (scope, element)->
            #  An event is fired to scroll to a given level
            scope.$on "tour:scrollTo", (ev, index)->
                if index > 1 and index <= FEATURE_COUNT+1
                    controller.scrollTo scenes[index].startPosition() + scenes[index].duration()
                else
                    controller.scrollTo scenes[index].startPosition() + 1
            # Constants
            FEATURE_DURATION = 300
            FEATURE_COUNT = 6
            FEATURE_SHOW = opacity: 1, marginTop: 0
            FEATURE_HIDE = opacity: 0, marginTop: 50
            # Entering closure function
            enter = (index)->->
                # Enter into an angular digest
                scope.$apply ->
                    # Update the parent scope attribute
                    angular.extend scope, tracker: index
            # Entering close for quote
            enterQuote = (index)->->
                $(".home__tour__feature-list__iphone__wrapper").animate
                    # 290 is the size of each step in this wrapper
                    scrollLeft: 290*index
            # Leaving closure function
            leave = (index)->->
                # Hide the selected quote
                TweenMax.fromTo(".home__tour__feature-list__single:eq(#{index})", 0.5, FEATURE_SHOW, FEATURE_HIDE)
            # Init scrollmagic controller
            controller = new ScrollMagic()
            # Activate scrolling animation
            controller.scrollTo (newScrollPos)->
                $("html, body").animate scrollTop: newScrollPos

            scenes = []

            # ──────────────────────────────────────────────────────────────────────
            # First screen
            # ──────────────────────────────────────────────────────────────────────
            scene = new ScrollScene()
                .triggerHook(0.5)
                .duration(600)
                .triggerElement(".home__tour__front")
                .addTo(controller)
                .on("enter", enter 0)

            scenes.push scene

            scene = new ScrollScene()
                .triggerHook(0.5)
                .duration(600)
                .triggerElement(".home__tour__features")
                .addTo(controller)
                .on("enter", enter 1)

            scenes.push scene

            # ──────────────────────────────────────────────────────────────────────
            # Features screens
            # ──────────────────────────────────────────────────────────────────────

            new ScrollScene()
                .triggerHook(0)
                .triggerElement(".home__tour__feature-list")
                .duration(FEATURE_DURATION * (FEATURE_COUNT-1) )
                .setPin(".home__tour__feature-list", pinnedClass: "home__tour__screen--pined")
                .addTo(controller)

            # Cascading quote appearance
            for n in [0.. FEATURE_COUNT - 1]
                # Create a scene
                scene = new ScrollScene()
                    .triggerHook(0)
                    .triggerElement(".home__tour__feature-list")
                    .duration(FEATURE_DURATION)
                    .offset((n-1) * FEATURE_DURATION)
                    .setTween(
                        TweenMax.to(".home__tour__feature-list__single:eq(#{n})", 0.5, FEATURE_SHOW)
                    )
                    .addTo(controller)
                    .on("enter", enter 2+n)
                    .on("enter", enterQuote n)
                    .on("leave", leave n)
                scenes.push scene


            # ──────────────────────────────────────────────────────────────────────
            # Quotes screen
            # ──────────────────────────────────────────────────────────────────────
            scene = new ScrollScene()
                .triggerHook(0.5)
                .triggerElement(".home__tour__quotes")
                .addTo(controller)
                .on("enter", enter FEATURE_COUNT+2)

            scenes.push scene

            # ──────────────────────────────────────────────────────────────────────
            # Get-ready screen
            # ──────────────────────────────────────────────────────────────────────
            scene = new ScrollScene()
                .triggerElement(".home__tour__get-ready")
                .triggerHook(0.5)
                .duration(600*4)
                .setTween(
                    TweenMax.fromTo ".home__tour__get-ready__ipad", 1, {top:  100}, {top:  -400}
                )
                .addTo(controller)
                .on("enter", enter FEATURE_COUNT+3)

            scenes.push scene

            # ──────────────────────────────────────────────────────────────────────
            # Pricing screen
            # ──────────────────────────────────────────────────────────────────────
            scene = new ScrollScene()
                .triggerHook(0.5)
                .triggerElement(".home__tour__pricing")
                .addTo(controller)
                .on("enter", enter FEATURE_COUNT+4)

            scenes.push scene

]