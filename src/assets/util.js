function getFileBasedOnTrigger(isInitCall, triggered_id, file_store, blob_store) {
  if (isInitCall) return file_store.files[0];

  const getIndex             = (id)     => file_store.files.findIndex(it => it.id === id);
  const getFileByIndexOffset = (offset) => file_store.files[(index + offset + len) % len];

  const offset = triggered_id === "img-btn-left" ? -1 : 1;
  const index  = getIndex(blob_store.active_id);
  const len    = file_store.files.length;

  // left or right button of slideshow clicked
  if(triggered_id === "id-slideshow-btn-left" || triggered_id === "id-slideshow-btn-right") {
    let isImage = false;
    let index   = 0;
    while(!isImage) {
      file    = getFileByIndexOffset(offset + index);
      isImage = file.type.startsWith("image/");
      index ++;
      if (index > file_store.files.length) {
        // no image found
        return null;
      }
    }
    return file;
  }

  // click on image preview
  const id = dash_clientside.callback_context.triggered_id["file_id"];
  return file_store.files.filter((item) => item["id"] == id)[0];
}


function extractFromCookie(name, cookie) {
     let cookieValue = "";
     const cname    = `${name}=`;
     const ca       = cookie.split(';');

     for(let i = 0; i <ca.length; i++) {
       let c = ca[i];
       while (c.charAt(0) == ' ') {
         c = c.substring(1);
       }
       if (c.indexOf(cname) == 0) {
         cookieValue = c.substring(cname.length, c.length);
       }
     }
  return cookieValue;
}


async function getBlobUrl(api_url, auth_token, file) {
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
}
