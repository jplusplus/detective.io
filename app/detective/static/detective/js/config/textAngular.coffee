angular.module('detective.config').config ['$provide', ($provide) =>
    $provide.decorator 'taOptions', ['$delegate', (taOptions) =>
        # Defining the toolbar
        taOptions.toolbar = [
            ['p', 'quote']
            ['bold', 'italics', 'underline']
            ['ul', 'ol']
            ['insertLink']
            ['clear']
        ]
        taOptions
    ]
]