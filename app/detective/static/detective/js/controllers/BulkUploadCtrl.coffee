class BulkUploadCtrl
    # Injects dependancies
    @$inject: ['$scope', '$http', '$routeParams', 'Page', 'Common']

    constructor: (@scope, @http, @routeParams, @Page, @Common)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @Page.title "Bulk Upload", no
        @scope.add_file_field = @add_file_field
        @scope.select_topic   = @select_topic
        @scope.send           = @send
        @scope.file_fields    = ["file1"] # start with one file field
        # Get the first topic page
        @scope.topics = @Common.query type: "topic"

    send: =>
        form_data = new FormData($('form').get(0))
        $.ajax
            url         : "/api/#{@scope.topic_selected.slug}/v1/summary/bulk_upload/"
            type        : "POST"
            xhr         : $.ajaxSettings.xhr
            data        : form_data
            cache       : false
            contentType : false
            processData : false

    add_file_field: =>
        field_name = "file" + (@scope.file_fields.length + 1)
        @scope.file_fields.push(field_name)

    select_topic: (topic) =>
        @scope.topic_selected = topic

angular.module('detective').controller 'BulkUploadCtrl', BulkUploadCtrl

# EOF
