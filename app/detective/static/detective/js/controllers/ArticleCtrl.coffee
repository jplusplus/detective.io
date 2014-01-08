class ArticleCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', 'Common', 'Page', '$location']

    constructor: (@scope,  @routeParams, @Common, @Page, @location)->
        # Enable loading mode
        @Page.loading yes
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Get the data from the database
        params =
            type       : "article"
            slug       : @routeParams.slug
            topic__slug: @routeParams.topic
        @Common.query params, (articles)=>
            # Disable loading mode
            @Page.loading no
            # Stop if it's an unkown topic or article
            return @location.path "/404" unless articles.length
            # Or take the article at the top of the list
            @scope.article = articles[0]

angular.module('detective').controller 'articleCtrl', ArticleCtrl