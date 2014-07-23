angular.module('detective.config').config ['$provide', ($provide) =>
    $provide.decorator 'taOptions', ['$delegate', (taOptions) =>
        # Defining the toolbar
        taOptions.toolbar = [
            ['quote', 'ul', 'ol']
            ['bold', 'italics', 'underline']
            ['insertLink', 'unlink']
        ]
        taOptions
    ]
]