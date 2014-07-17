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
                @getTopics (topics)=> @topics = @topics.concat topics
                # Update topic list when the user object changes
                $rootScope.$on "user:updated", @updateTopics, true

                $rootScope.$on '$stateChangeStart', @onStateChanged


            onStateChanged: (e, current, params)=>
                if params.topic and @topics 
                    @setCurrent @@getTopic params.topic

            updateTopics: =>
                @getTopics (data)=>
                    @topics = data
                    if @topic_slug
                        @topic = @setTopic @topic_slug

            setCurrent: (topic)=>
                if typeof topic is typeof {}
                    @topic = topic
                else
                    @topic = @getTopic topic 

                $rootScope.$broadcast @EVENTS.current_topic_updated

            updateCurrentLocation: (topic)=>
                #console.log topic

            getTopics: (cb)=>
                Common.query type: 'topic', cb

            getTopic: (slug)=>
                return unless slug and @topics
                _.findWhere @topics, slug: slug

            isTopic: (slug)=>
                if @topic_slug and !@topics
                    return @topic_slug is slug
                else
                    return false unless @topic?
                    @topic.slug is slug

            setTopic: (slug)=>
                topic = @getTopic slug
                @topic = topic if topic?



]