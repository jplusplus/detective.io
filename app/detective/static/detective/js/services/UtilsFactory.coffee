angular.module('detective.service').factory 'UtilsFactory', [
    ()->
        new class UtilsFactory
            isValidURL: (url)=>
                URL_PATTERN = /^(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?$/
                URL_PATTERN.test(url)


            loggerDecorator: (loggerName)=>
                class WrappedLogger
                    constructor: (name)->
                        @loggerName = name

                    wrappedMethod: (method_name, argsArray)=>
                        args = Array.prototype.slice.call(argsArray)
                        args = [ @loggerName ].concat args
                        console[method_name].apply(console, args)

                    log: =>
                        @wrappedMethod('log', arguments)

                    warn: =>
                        @wrappedMethod('warn', arguments)

                new WrappedLogger(loggerName)


                
]
