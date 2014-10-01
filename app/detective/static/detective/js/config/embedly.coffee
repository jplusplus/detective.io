angular.module('detective.config').config(['ngEmbedlyServiceProvider', (ngEmbedlyServiceProvider) ->
    ngEmbedlyServiceProvider.setKey '4475ffae967b47099b6c764c462d801b'
    ngEmbedlyServiceProvider.setTemplate "<a target='_blank' ng-href='[[ url ]]' ng-bind='url'></a><div ng-bind-html='html'></div>"
])