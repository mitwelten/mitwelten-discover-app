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

  create_blob: async function(_click, _prev, _next, file_store, blob_store) {

    // no files to load
    if (file_store.files.length === 0) {
      return ["", blob_store];
    }

    // check if the callback was triggered on initialization
    const { triggered_id } = dash_clientside.callback_context;
    const isInitCall       = dash_clientside.callback_context.triggered.every(({ value }) => value === null);

    const file = getFileBasedOnTrigger(isInitCall, triggered_id, file_store, blob_store);

    // if file is already in blob store, return its url
    isFileLoaded = blob_store.files.find(it => it && it["id"] == file.id);
    if (isFileLoaded !== undefined) {
      blob_store.active_id = file.id;
      return [isFileLoaded.url, blob_store];
    }

    if (file === undefined) {
      throw dash_clientside.PreventUpdate;
    }

    const auth_token = extractFromCookie("auth", document.cookie);
    const blob_url   = await getBlobUrl(blob_store.api_url, auth_token, file);

    if (file["type"] == "application/pdf" || file["type"] == "text/plain") {
      window.open(blob_url, "_blank");
      URL.revokeObjectURL(blob_url);
      throw dash_clientside.PreventUpdate;
    }
    blob_store.files.push({id: file.id, url: blob_url});
    blob_store.active_id = file.id;
    return [blob_url, blob_store];
  },


  clear_blob: async function(note_store, blob_store) {

    if (note_store["data"] === null) {
      blob_store.files.forEach(it => {
        URL.revokeObjectURL(it.url);
      });
    }
    blob_store.files = [];
    blob_store.active_id = undefined; 
    return blob_store;
  },

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
