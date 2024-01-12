window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(e, ctx) {
            ctx.setProps({
                data: 'Hello world!'
            })
        }
    }
});