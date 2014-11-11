class window.TopicFormCtrl
    @$inject: ['$scope', '$state', 'TopicsFactory', 'Page', 'User', 'constants.events']

    constructor: (@scope, @state, @TopicFactory, @Page, @User, @EVENTS)->
        @form_mode = undefined
        # handles loading for the different form panels
        @scope.loading   =
            main: false
            privacy: false

        @scope.submitted = no
        @scope.submit = @submit
        @scope.isPublic         = @isPublic
        @scope.isPrivate        = @isPrivate
        @scope.shouldShowForm   = @isEditing
        @scope.isEditing        = @isEditing
        @scope.isCreating       = @isCreating
        @scope.hideErrors       = @hideErrors
        @scope.canChangePrivacy = @canChangePrivacy
        @scope.changePrivacy    = @changePrivacy

        @scope.$watch 'topic', @onTopicUpdated, yes

    isEditing: => @state.is("user-topic-edit")

    isCreating: => @state.includes("user-topic-create")

    onTopicUpdated: (old_val, new_val) =>
        @hideErrors()
        @scope.$broadcast @EVENTS.topic.user_updated, old_val, new_val

    hideErrors: =>
        unless @scope.loading
            @scope.submitted = no

    assertModeInitialized: =>
        return if @form_mode?
        throw new Error("TopicFormCtrl children must set the form mode (create or edit)")

    submit: (form, panel='main')=>
        @assertModeInitialized()
        @scope.submitted = yes
        return unless form.$valid
        if @isEditing()
            @edit(panel)
        if @isCreating()
            @create(panel)

    canChangePrivacy: => @User.profile.plan != 'free'

    isPublic: =>  !!@scope.topic.public

    isPrivate: => !@isPublic()

    changePrivacy: (form)=>
        @scope.topic.public = !!!@scope.topic.public
        @submit(form, 'privacy')

