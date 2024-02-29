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

window.dash_clientside.attachment = {
  create_blob: async function(_click, file_store) {

    // check if the callback was triggered on initialization
    const arr = dash_clientside.callback_context.triggered;
    const init_call = arr.reduce((previous, current) => {
      return previous && current["value"] == null;
    }, true);
    if (init_call) {
      throw dash_clientside.PreventUpdate;
    }

    const id      = dash_clientside.callback_context.triggered_id["file_id"];
    const files   = file_store["files"];
    const api_url = file_store["url"];

    const file    = files.filter((item) => item["id"] == id)[0]

    if (file === undefined) {
      throw dash_clientside.PreventUpdate;
    }

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

      const result  = await fetch(`${api_url}/files/${file["object_name"]}`, requestOptions);
      const blob    = await result.blob();
      const blobObj = new Blob([blob], {type: file["type"]});
      const urlObj  = URL.createObjectURL(blobObj);
      if (file["type"] == "application/pdf" || file["type"] == "text/plain") {
        window.open(urlObj, "_blank");
        URL.revokeObjectURL(urlObj);
        throw dash_clientside.PreventUpdate;
      }
      return urlObj;
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
