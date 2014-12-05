class window.ArticleCtrl
    # Injects dependencies
    @$inject: ['$scope', '$stateParams', '$state', 'Common', 'Page']

    constructor: (@scope,  @stateParams, @state, @Common, @Page)->
        # Enable loading mode
        @Page.loading yes
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Get the data from the database
        params =
            type       : "article"
            slug       : @stateParams.slug
            topic__slug: @stateParams.topic
        @Common.query params, (articles)=>
            # Disable loading mode
            @Page.loading no
            # Stop if it's an unkown topic or article
            return @state.go("404") unless articles.length
            # Or take the article at the top of the list
            @scope.article = articles[0]

angular.module('detective').controller 'articleCtrl', ArticleCtrl