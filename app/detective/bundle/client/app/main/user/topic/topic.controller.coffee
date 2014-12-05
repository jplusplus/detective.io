class window.UserTopicCtrl
    # Public method to resolve
    @resolve:
        topic: ($rootScope, $stateParams, $state, $q, Common, Page, User)->
            notFound = ->
                do deferred.reject
                $state.go "404"
                deferred
            forbidden = ->
                do deferred.reject
                $state.go "403"
                deferred
            deferred = do $q.defer
            # Checks that the current topic and user exists together
            if $stateParams.topic? and $stateParams.username?
                # Activate loading mode
                Page.loading yes
                # Retreive the topic for this user
                params =
                    type: "topic"
                    slug: $stateParams.topic
                    author__username: $stateParams.username
                Common.get params, (data)=>
                    # Stop if it's an unkown topic
                    unless data.objects and data.objects.length
                        return do (if (do User.hasReadPermission) then notFound else forbidden)
                    topic = data.objects[0]
                    $state.transition.then (newState)->
                        if newState.owner and not (User.is_logged and User.owns(topic))
                            forbidden()

                    # Resolve the deffered result
                    deferred.resolve(topic)
            # Reject now
            else return notFound()
            # Return a deffered object
            deferred.promise
        individual: (Individual, $stateParams)=>
            Individual.get($stateParams).$promise
        forms: (Summary, $stateParams)=>
            Summary.cachedGet(topic: $stateParams.topic, username: $stateParams.username, id: "forms").$promise


    # Injects dependencies
    @$inject: ['$scope', '$rootScope', '$stateParams', 'Summary', '$location', '$timeout', '$filter', 'Page', 'QueryFactory', 'topic']

    constructor: (@scope, $rootScope, @stateParams, @Summary, @location, @timeout, @filter, @Page, @QueryFactory, topic)->
        @scope.getTypeCount = @getTypeCount
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Current individual scope
        @scope.topic    = @stateParams.topic
        @scope.username = @stateParams.username

        # Meta data about this topic
        @scope.meta = topic
        if topic.is_uploading
            # TMP, must do something better than that
            $rootScope.$broadcast 'http:error', 'Beware, a huge data upload is in progress on this topic.'

        # Set page's title
        @Page.title @scope.meta.title
        # Build template url
        @scope.templateUrl = "/partial/main/user/topic/topic-#{@scope.username}-#{@scope.topic}.html"
        # Countries info
        @scope.countries = @Summary.get id:"countries"
        # Types info
        @Summary.get id:"types", (d)=> @scope.types = d
        # Types info
        @Summary.get id:"forms", (d)=> @scope.forms = _.values(d)
        # Country where the user click
        @scope.selectedCountry = {}
        @scope.isSearchable = (f)-> f.rules? && f.rules.is_searchable
        @scope.shouldDisplayMap = => _.findWhere(@scope.meta.models, name: 'Country')?
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        @scope.$watch "selectedCountry", @selectCountry, true

    # ──────────────────────────────────────────────────────────────────────────
    # Class methods
    # ──────────────────────────────────────────────────────────────────────────
    selectCountry: (val, old)=>
        @location.path "/#{@scope.username}/#{@scope.topic}/country/#{val.id}" if val.id?

    getTypeCount: ()=>
        return '∞' unless @scope.types?
        tt = 0
        for type in arguments
            t   = @scope.types[type]
            tt += if t? and t.count? then t.count else 0
        tt

angular.module('detective').controller 'userTopicCtrl', UserTopicCtrl
