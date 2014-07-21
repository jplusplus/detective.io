class RelationshipPropertiesCtrl
    # Injects dependancies
    @$inject: ['$scope', '$modalInstance', "properties", "relationship"]
    constructor: (@scope, @modalInstance, @properties, @relationship)->
        # Cancel button just close the modal
        @scope.cancel = @close
        # This relationship may not have properties yet
        @scope.properties = @properties or {}
        @scope.relationship = @relationship

    @close: => do @modelInstance.close



angular.module('detective.controller').controller 'RelationshipPropertiesCtrl', RelationshipPropertiesCtrl