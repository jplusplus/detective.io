angular.module('detective.filter').filter "yesorno", ->
    (input) ->
        if input? and input then 'yes' else 'no'
