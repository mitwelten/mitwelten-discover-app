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
  },
};
