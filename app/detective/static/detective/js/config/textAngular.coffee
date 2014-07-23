angular.module('detective.config').config ['$provide', ($provide) =>
    $provide.decorator 'taOptions', ['$delegate', (taOptions) =>
        # Defining the toolbar
        taOptions.toolbar = [
            ['p', 'quote', 'ul', 'ol']
            ['bold', 'italics', 'underline', 'clear']
            ['insertLink', 'unlink']
        ]
        taOptions
    ]
]