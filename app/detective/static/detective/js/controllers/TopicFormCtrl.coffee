class window.TopicFormCtrl
    @$inject: ['$scope', '$state', 'TopicsFactory', 'Page']

    MODES:
        editing: 'edit'
        creating: 'create'

    constructor: (@scope, @state, @TopicFactory, @Page)->
        @form_mode = undefined
        @scope.submitted = no
        @scope.submit = @submit
        @scope.shouldShowForm = @isEditing
        @scope.isEditing = @isEditing
        @scope.isCreating = @isCreating
        @scope.hideErrors = @hideErrors

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

    onTopicUpdated: =>
        @hideErrors()
        @scope.$broadcast 'topic:updated'

    hideErrors: =>
        unless @scope.loading
            @scope.submitted = no

    assertModeInitialized: =>
        return if @form_mode?
        throw new Error("TopicFormCtrl children must set the form mode (create or edit)")

    submit: (form)=>
        @assertModeInitialized()
        @scope.submitted = yes
        return unless form.$valid
        if @isEditing()
            @edit()
        if @isCreating()
            @create()
