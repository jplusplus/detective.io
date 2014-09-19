angular.module('detective.config').config(['ngEmbedlyServiceProvider', (ngEmbedlyServiceProvider) ->
    ngEmbedlyServiceProvider.setKey '4475ffae967b47099b6c764c462d801b'
    #ngEmbedlyServiceProvider.setTemplate "<h1>[[title]]</h1><div ng-bind-html='html'></div>"
])