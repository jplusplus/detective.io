class BulkUploadCtrl
    # Injects dependancies
    @$inject: ['$scope', '$http', '$routeParams', 'Page', 'Individual']

    constructor: (@scope, @http, @routeParams, @Page, @Individual)->
        @Page.title "Bulk Upload", no
        # ──────────────────────────────────────────────────────────────────────
        # Scope methods
        # ──────────────────────────────────────────────────────────────────────
        @scope.addFileField   = @addFileField
        @scope.selectTopic    = @selectTopic
        @scope.submit           = @submit
        @scope.onFileSelect   = @onFileSelect
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Get the current topic as default topic
        @scope.topic_selected = @routeParams.topic
        # start with one file field
        @scope.file_fields    = ["file1"]
        @scope.files          = {}

    # User submit the form
    submit: =>
        @scope.feedback = null
        # Parameters of your request (to build the url)
        params =
            topic: @scope.topic_selected
        # Send the data
        @scope.feedback = @Individual.bulk params, @scope.files

    # User choose a file
    onFileSelect: (files, field) =>
        # Queue the file
        @scope.files[field] = files

    # User ask for a new file field
    addFileField: =>
        field_name = "file" + (@scope.file_fields.length + 1)
        @scope.file_fields.push(field_name)

angular.module('detective').controller 'BulkUploadCtrl', BulkUploadCtrl

# EOF