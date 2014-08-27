class TopicFormCtrl
    @$inject: ['$scope', '$state', 'TopicsFactory', 'Page']

    MODES:
        editing: 'edit'
        creating: 'create'

    constructor: (@scope, @state, @TopicFactory, @Page)->
        @form_mode = undefined
        @scope.submit = @submit
        @scope.shouldShowForm = @isEditing
        @scope.isEditing = @isEditing
        @scope.isCreating = @isCreating
        @scope.formMode = =>
            @form_mode

    isEditing: =>
        @form_mode is @MODES.editing

    isCreating: =>
        @form_mode is @MODES.creating

    setCreatingMode: =>
        @form_mode = @MODES.creating

    setEditingMode: =>
        @form_mode = @MODES.editing

    assertModeInitialized: =>
        return if @form_mode?
        throw new Error("TopicFormCtrl children must set the form mode (create or edit)")

    submit: =>
        @assertModeInitialized()
        if @isEditing()
            @edit()
        if @isCreating()
            @create()
