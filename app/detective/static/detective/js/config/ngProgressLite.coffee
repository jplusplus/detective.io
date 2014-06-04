angular.module('detective.config').config ['ngProgressLiteProvider', (ngProgressLiteProvider)->
    console.log ngProgressLiteProvider.settings
    ngProgressLiteProvider.settings.speed       = 300
    ngProgressLiteProvider.settings.ease        = 'ease'
    ngProgressLiteProvider.settings.trickleRate = 0.1
]