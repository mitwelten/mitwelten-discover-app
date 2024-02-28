if (!window.dash_clientside) {
  window.dash_clientside = {};
}

window.dash_clientside.browser_properties = {
  fetchWindowProps: function() {
    const returnObj = {
      pixelRatio:  window.devicePixelRatio,
      width: window.innerWidth,
      height: window.innerHeight,
    };
    return returnObj
  }
};

window.dash_clientside.test = {
  create_blob: async function(_click) {

    // check if the callback was triggered on initialization
    const arr = dash_clientside.callback_context.triggered;
    const init_call = arr.reduce((previous, current) => {
      return previous && current["value"] == null;
    }, true);
    if (init_call) {
      throw dash_clientside.PreventUpdate;
    }

    const api_url   = dash_clientside.callback_context.states_list[0]["value"]["url"];
    const data      = dash_clientside.callback_context.triggered_id;
    const file_name = data["object_name"].replace('%','.');
    const mime_type = data["type"];

    const cookie = document.cookie;

    // extract auth cookie
    let auth_token = "";
    const cname    = "auth=";
    const ca       = cookie.split(';');

    for(let i = 0; i <ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(cname) == 0) {
        auth_token = c.substring(cname.length, c.length);
      }

      const requestOptions = {
        method: 'GET',
        mode: "cors",
        headers: {Authorization: `Bearer ${auth_token}`},
        redirect: 'follow'
      };

      const result  = await fetch(`${api_url}/files/${file_name}`, requestOptions);
      const blob    = await result.blob();
      const blobObj = new Blob([blob], {type: mime_type});
      const urlObj  = URL.createObjectURL(blobObj);
      window.open(urlObj, "_blank");
      URL.revokeObjectURL(urlObj);
      throw dash_clientside.PreventUpdate;
    }
  }
};

window.dashExtensions = Object.assign({}, window.dashExtensions, {
  default: {
      function0: function(e, ctx) {
          ctx.setProps({
            latlng: { lat: `${e.target.getLatLng()['lat']}`,
                      lng: `${e.target.getLatLng()['lng']}` 
            },
          })
      }
  }
});
