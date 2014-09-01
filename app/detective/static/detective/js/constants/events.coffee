angular.module('detective.constants').constant 'constants.events',
    # topics' related events
    topic:
        # called when topic was succesfuly saved by API
        created: 'topic:created'
        # called when topic was succesfuly removed by API
        deleted: 'topic:deleted'
        # called when user changes value
        user_updated: 'topic:user_updated'
    # user & auth related events
    user:
        login: 'user:login'
        logout: 'user:logout'
        updated: 'user:updated'
    # topic creation related events
    skeleton:
        selected: 'skeleton:selected'
    # generic events
    trigger:
        scroll: 'trigger:scroll'