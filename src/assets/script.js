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


    function getFileBasedOnTrigger(isInitCall, triggered_id, file_store, blob_store) {
      if (isInitCall) return file_store.files[0];

      const getIndex             = (id)     => file_store.files.findIndex(it => it.id === id);
      const getFileByIndexOffset = (offset) => file_store.files[(index + offset + len) % len];

      const offset = triggered_id === "img-btn-left" ? -1 : 1;
      const index  = getIndex(blob_store.active_id);
      const len    = file_store.files.length;

      // left or right button of slideshow clicked
      if(triggered_id === "id-slideshow-btn-left" || triggered_id === "id-slideshow-btn-right") {
        return getFileByIndexOffset(offset);
      }

      // click on image preview
      const id = dash_clientside.callback_context.triggered_id["file_id"];
      return file_store.files.filter((item) => item["id"] == id)[0];
    }

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
     }

    const requestOptions = {
      method: 'GET',
      mode: "cors",
      headers: {Authorization: `Bearer ${auth_token}`},
      redirect: 'follow'
    };

    const api_url = blob_store.api_url;
    const result  = await fetch(`${api_url}/files/${file["object_name"]}`, requestOptions);
    const blob    = await result.blob();
    const blobObj = new Blob([blob], {type: file["type"]});
    const urlObj  = URL.createObjectURL(blobObj);
    if (file["type"] == "application/pdf" || file["type"] == "text/plain") {
      window.open(urlObj, "_blank");
      URL.revokeObjectURL(urlObj);
      throw dash_clientside.PreventUpdate;
    }
    blob_store.files.push({id: file.id, url: urlObj});
    blob_store.active_id = file.id;
    return [urlObj, blob_store];
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
