angular.module('detective.service').factory 'UtilsFactory', [
    ()->
        new class UtilsFactory
            loggerDecorator: (loggerName)=>
                class WrappedLogger
                    constructor: (name)->
                        @loggerMame = name

                    wrappedMethod: (method_name, argsArray)=>
                        args = Array.prototype.slice.call(argsArray)
                        args.slice(0, 0, @loggerName)
                        console[method_name].apply(console, args)

                    log: =>
                        @wrappedMethod('log', arguments)

                    warn: =>
                        @wrappedMethod('warn', arguments)

                new WrappedLogger(loggerName)


                
]
