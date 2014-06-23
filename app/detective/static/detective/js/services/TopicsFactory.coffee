angular.module('detective.service').factory 'TopicsFactory', [
    '$q', '$rootScope', '$route', 'Common', 'User', 'UtilsFactory'
    ($q, $rootScope, $route, Common, User, UtilsFactory)->
        new class TopicsFactory
            constructor: ->
                $rootScope.$watch (-> User), @updateTopics, true

                @logger = UtilsFactory.loggerDecorator('TopicsFactory')
                @topics = []
                @topic  = {}

            updateTopics: => 
                @getTopics (data)=> 
                    @topics = data
                    if @topic_slug 
                        @topic = @getTopic @topic_slug

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