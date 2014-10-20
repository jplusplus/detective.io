class window.TopicFormCtrl
    @$inject: ['$scope', '$state', 'TopicsFactory', 'Page', 'User', 'constants.events']

    MODES:
        editing: 'edit'
        creating: 'create'

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

        @scope.formMode = =>
            @form_mode

        @scope.$watch 'topic', @onTopicUpdated, yes

    isEditing: =>
        @form_mode is @MODES.editing

    isCreating: =>
        @form_mode is @MODES.creating

    setCreatingMode: =>
        @form_mode = @MODES.creating

    setEditingMode: =>
        @form_mode = @MODES.editing

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

