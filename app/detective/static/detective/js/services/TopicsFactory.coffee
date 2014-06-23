angular.module('detective.service').factory 'TopicsFactory', [
    '$q', '$rootScope', '$route', 'Common', 'User', 'UtilsFactory'
    ($q, $rootScope, $route, Common, User, UtilsFactory)->
        new class TopicsFactory
            constructor: ->

                @logger = UtilsFactory.loggerDecorator('TopicsFactory')
                @topics = []
                @topic  = {}


                $rootScope.$watch (=> $route.current), (current)=>
                    return unless current? and current.params?
                    @topic_slug = current.params.topic
                    @logger.log('topic_slug changed: ', @topic_slug)

                $rootScope.$watch (->User), @updateTopics, true

            updateTopics: => 
                @getTopics (data)=>     
                    @topics = data
                    if @topic_slug 
                        @topic = @getTopic @topic_slug

            getTopics: (cb)=>
                Common.query type: 'topic', cb

            getTopic: (slug)=>
                return unless slug 
                _.findWhere @topics, slug: slug

            isTopic: (slug)=>
                return false unless @topic?
                @topic.slug is slug 

            setTopic: (slug)=>
                topic = @getTopic slug 
                @topic = topic if topic?

                
    
]