angular.module('detective.service').factory 'TopicsFactory', [
    '$q', '$rootScope', '$state', 'Common', 'Topic', 'TopicSkeleton', 'User', 'UtilsFactory'
    ($q, $rootScope, $state, Common, Topic, TopicSkeleton, User, UtilsFactory)->
        new class TopicsFactory
            EVENTS:
                current_topic_updated: "topic:updated"

            constructor: ->
                do @reset

                # Update topic list when the user object changes
                $rootScope.$on "user:updated", @reset, true

                $rootScope.$on '$stateChangeStart', @onStateChanged

            post: Topic.post
            put:  Topic.put

            reset: =>
                # Topics list
                @topics = []
                @skeletons = TopicSkeleton.get()
                # Active topic
                @topic = {}

            onStateChanged: (e, current, params)=>
                if params.topic and @topics
                    (@getTopic params.topic).then (topic) =>
                        @setCurrent topic
                else
                    @topic = {}
                    $rootScope.$broadcast @EVENTS.current_topic_updated


            setCurrent: (topic)=>
                return unless topic?
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
                if @topic? and @topic.slug?
                    return @topic.slug is slug
                no
]