(function() {
  document.addEventListener("DOMContentLoaded", function() {
    // Open twitter login link in a new window when this page is embed in a
    // iframe.

    function inIframe() {
      try {
        return window.self !== window.top;
      } catch (e) {
        return true;
      }
    }

    if (inIframe) {
      var twitterButtonLinkEl = document.getElementById('twitter-button-link');
      var twitterLoginLinkEl = document.getElementById('twitter-login-link');
      twitterButtonLinkEl.addEventListener("click", function(event) {
        event.preventDefault();
        var twitterLoginUrl = twitterLoginLinkEl.getAttribute("href");
        var params = 'location=0,status=0,width=800,height=400';
        var twitterLoginWindow = window.open(twitterLoginUrl, 'twitterLoginWindow', params);

        var popupTick = setInterval(function() {
          if (twitterLoginWindow.closed) {
            clearInterval(popupTick);
            window.location.replace("/users/close");
          }
        }, 500);
      });
    }

  });
}());
