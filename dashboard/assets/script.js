if (!window.dash_clientside) {
  window.dash_clientside = {};
}
window.dash_clientside.browser = {
  testFunction: function() {
    const retval = {
      pixelRatio:  window.devicePixelRatio,
      width: window.innerWidth,
      height: window.innerHeight,
    };
    return retval
  },
};
