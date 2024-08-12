const getFileBasedOnTrigger = (isInitCall, triggered_id, file_store, active_id) => {
  if (isInitCall) {
    return getNextImage(0, 0, file_store.files);
  }

  const getIndex = id => file_store.files.findIndex(it => it.id === id);

  // left or right button of slideshow clicked
  // TODO: replace hard coded strings
  if(triggered_id === "id-slideshow-btn-left" || triggered_id === "id-slideshow-btn-right") {
    const reversed = triggered_id === "id-slideshow-btn-left" ;
    const step     = reversed ? -1 : 1;
    const index    = getIndex(active_id);
    return getNextImage(index, step, file_store.files)
  }

  // click on image preview
  const id = dash_clientside.callback_context.triggered_id["file_id"];
  return file_store.files.filter(item => item["id"] === id)[0];
};


const getNextImage = (index, step, files) => {
  const len       = files.length;
  let file        = null;
  let valid       = false;
  let loopCounter = 0;

  // filter documents
  while(!valid && loopCounter <= len) {
    index = index + step;
    const idx = (index + len) % len;
    file = files[idx];
    valid = file.type.startsWith("image/") || file.type.startsWith("audio/");
    loopCounter++;
  }
  return file;
};


const extractFromCookie = (name, cookie) => {
     let cookieValue = "";
     const cname     = `${name}=`;
     const ca        = cookie.split(';');

     for(let i = 0; i <ca.length; i++) {
       let c = ca[i];
       while (c.charAt(0) === ' ') {
         c = c.substring(1);
       }
       if (c.indexOf(cname) === 0) {
         cookieValue = c.substring(cname.length, c.length);
       }
     }
  return cookieValue;
};

const getBlobUrl = async (api_url,  file) => {
    const requestOptions = {
      method: 'GET',
      mode: "cors",
      //headers: {Authorization: `Bearer ${auth_token}`},
      redirect: 'follow'
    };

    const result  = await fetch(`${api_url}/files/${file["object_name"]}`, requestOptions);
    const blob    = await result.blob();
    const blobObj = new Blob([blob], {type: file["type"]});
    return URL.createObjectURL(blobObj);
};

const getBlobUrlAuth = async (api_url, auth_token, file) => {
    const requestOptions = {
      method: 'GET',
      mode: "cors",
      headers: {Authorization: `Bearer ${auth_token}`},
      redirect: 'follow'
    };

    const result  = await fetch(`${api_url}/files/${file["object_name"]}`, requestOptions);
    const blob    = await result.blob();
    const blobObj = new Blob([blob], {type: file["type"]});
    return URL.createObjectURL(blobObj);
};


const formatTime = seconds => {
  const min = Math.floor(seconds / 60);
  let sec = Math.floor(seconds - min * 60);
  if (sec < 10){ 
    sec = `0${sec}`;
  }
  return `${min}:${sec}`;
};
