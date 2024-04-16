if (!window.dash_clientside) {
  window.dash_clientside = {};
  window.activePopup = "";
}

window.addEventListener("keydown", (e) => {
  const evtobj = window.event? event : e;

  if (evtobj.keyCode == 32 && evtobj.ctrlKey) {
    const store = localStorage.getItem("id-test-icon-store");
    let alertText = "Switched to colored icons.";
    if (store === "false" || store === false) {
      localStorage.setItem("id-test-icon-store", true);
      alertText = "Switched to graphical icons.";
    } else {
      localStorage.setItem("id-test-icon-store", false);
    }
    alert(`${alertText}\nReload the page to make changes visible!`);
  }
}),


window.dash_clientside.browser_properties = {
  fetchWindowProps: () => ({
    pixelRatio: window.devicePixelRatio,
    width: window.innerWidth,
    height: window.innerHeight,
  })
};

window.dash_clientside.attachment = {
  singleImage: async (url) => {
  },

  create_blob: async (_click, _prev, _next, file_store, blob_store) => {

    // no files to load
    if (file_store.files && file_store.files.length === 0) {
      return ["", blob_store];
    }

    // check if the callback was triggered on initialization
    const { triggered_id } = dash_clientside.callback_context;
    const isInitCall       = dash_clientside.callback_context.triggered.every(({ value }) => value === null);

    const file = getFileBasedOnTrigger(isInitCall, triggered_id, file_store, blob_store.active_id);

    // if file is already in blob store, return its url
    const isFileLoaded = blob_store.files.find(it => it && it["id"] === file.id);
    if (isFileLoaded !== undefined) {
      if (blob_store.active_id === file.id) {
        throw dash_clientside.PreventUpdate;
      }
      blob_store.active_id = file.id;
      const currentFile = {url: isFileLoaded.url, name: file.name, type: file.type, id: file.id};
      return [currentFile, blob_store];
    }

    if (file === undefined) {
      throw dash_clientside.PreventUpdate;
    }

    const auth_token = extractFromCookie("auth", document.cookie);
    const blob_url   = await getBlobUrlAuth(blob_store.api_url, auth_token, file);

    blob_store.files.push({id: file.id, url: blob_url});
    blob_store.active_id = file.id;

    const currentFile = {url: blob_url, name: file.name, type: file.type, id: file.id};
    return [currentFile, blob_store];
  },


  load_text_blob: async (_click, file_store) => {
    docs = file_store.documents
    api_url = file_store.API_URL

    // no files to load
    if (docs && docs.length === 0) {
      throw dash_clientside.PreventUpdate;
    }

    // check if the callback was triggered on initialization
    const { triggered_id } = dash_clientside.callback_context;
    const isInitCall       = dash_clientside.callback_context.triggered.every(({ value }) => value === null);

    if(isInitCall) {
      throw dash_clientside.PreventUpdate;
    }

    const file = docs.filter(it => it.id == triggered_id.file_id)[0]

    if (file === undefined) {
      throw dash_clientside.PreventUpdate;
    }

    const blob_url = await getBlobUrl(api_url, file);

    window.open(blob_url, "_blank");
    //URL.revokeObjectURL(blobObj);

    throw dash_clientside.PreventUpdate;
  },


  clear_blob: async (note_store, blob_store) => {

    if (note_store["data"] === null) {

      if (blob_store.files.length > 0){
        blob_store.files.forEach(it => {
          URL.revokeObjectURL(it.url);
        });
      }
    }
    blob_store.files = [];
    blob_store.active_id = undefined; 
    return blob_store;
  },

  //load_audio_files: async (_clicks, file_store, blob_store) => {

  //  const isInitCall = dash_clientside.callback_context.triggered.every(({ value }) => value === null);
  //  // load audio files eagerly on initialization 
  //  if (!isInitCall) {
  //    throw dash_clientside.PreventUpdate;
  //  }

  //  const audio_files = file_store.files.filter(file => file.type === "audio/mpeg");

  //  const auth_token = extractFromCookie("auth", document.cookie);
  //  const audio_urls = [];

  //  for(let i = 0; i < audio_files.length; i ++) {
  //    const file = audio_files[i];
  //    const blob_url = await getBlobUrl(blob_store.api_url, auth_token, file);
  //    blob_store.files.push({id: file.id, url: blob_url});
  //    audio_urls.push(blob_url);
  //  }
  //  return [audio_urls, blob_store];
  //}
};


window.dash_clientside.audio= {

  playOrPause: (_, id) => {
    const player = document.getElementById(id);
    if(player.paused || player.currentTime === 0) {
      player.play();
    } else {
      player.pause();
    }
  },

  pause: (_1, _2, id) => {
    document.getElementById(id).pause();
    throw dash_clientside.PreventUpdate;
  },

  stop : (_, id) => {
    const player = document.getElementById(id);
    player.pause();
    player.currentTime = 0;

    return `${formatTime(player.currentTime)} / ${formatTime(player.duration)}`;
  },

  noSound: (_, id) => document.getElementById(id).muted = !document.getElementById(id).muted,

  progress: (_, id) => {
    const player = document.getElementById(id);
    if (player.seeking) {
      throw dash_clientside.PreventUpdate;
    }
    return `${formatTime(player.currentTime)} / ${formatTime(player.duration)}`;
  },
};


// handling leaflet marker popup states
window.dashExtensions = Object.assign({}, window.dashExtensions, {
  default: {
    setLatLng: (e, ctx) => {
      ctx.setProps({
        latlng: { lat: `${e.target.getLatLng()['lat']}`,
          lng: `${e.target.getLatLng()['lng']}`
        },
      })
    },

    mouseover: function(e, _ctx) {
      e.target.openPopup();
    },

    mouseout: function(e, ctx) {  
      if (window.activePopup != ctx.id) {
        e.target.closePopup();
      }
    },  

    click: function(e, ctx) {  
      for (const [_, value] of Object.entries(ctx.map._targets)) {
        if (value.options.id != ctx.id) {
          value.closePopup();
        }
      }
      e.target.openPopup();
      window.activePopup = ctx.id;
    },  
  }
});

