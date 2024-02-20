window.dashExtensions = Object.assign({}, window.dashExtensions, {
            default: {
                function0: function(e, ctx) {
                        ctx.setProps({
                                    latlng: {
                                        lat: `${e.target.getLatLng()["lat"], lng:`${e.target.getLatLng()["lng"]`})}
    }
});