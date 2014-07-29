angular.module('detective.service').factory 'TopicsFactory', [
    '$q', '$rootScope', '$state', 'Common', 'User', 'UtilsFactory'
    ($q, $rootScope, $state, Common, User, UtilsFactory)->
        new class TopicsFactory
            EVENTS:
                current_topic_updated: "topic:updated"

            constructor: ->
                # Topics list
                @topics = []
                # Active topic
                @topic  = {}
                # We get all topics here
                # and we update factory's topics
                # @getTopics (topics)=> @topics = @topics.concat topics
                # Update topic list when the user object changes
                $rootScope.$on "user:updated", =>
                    console.debug 'must update topics'
                , true

                $rootScope.$on '$stateChangeStart', @onStateChanged


            onStateChanged: (e, current, params)=>
                if params.topic and @topics
                    (@getTopic params.topic).then (topic) =>
                        @setCurrent topic

            setCurrent: (topic)=>
                if typeof topic is typeof {}
                    (@topics.push topic) unless (_.findWhere @topics, slug: topic.slug)
                    @topic = topic
                else
                    (@getTopic topic).then (topic) =>
                        @topic = topic

                $rootScope.$broadcast @EVENTS.current_topic_updated


            getTopic: (slug)=>
                return unless slug
                deferred = do $q.defer
                topic = _.findWhere @topics, slug: slug
                if not topic?
                    Common.query
                        type : 'topic'
                        slug : slug
                    .$promise.then (_topics) =>
                        if _topics.length > 0
                            @topics.push _topics[0]
                            deferred.resolve _topics[0]
                        else
                            do deferred.reject
                else
                    deferred.resolve topic
                deferred.promise

            isTopic: (slug)=>
                if @topic_slug and !@topics
                    return @topic_slug is slug
                else
                    return false unless @topic?
                    @topic.slug is slug
]