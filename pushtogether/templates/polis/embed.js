(function() {
  var polis = window.polis = window.polis || {};
  polis._hasRun = 1;
  var iframes = [];
  var maxHeightsSeen = {};

  polis.on = polis.on || {};
  polis.on.vote = polis.on.vote || [];
  polis.on.doneVoting = polis.on.doneVoting || [];
  polis.on.write = polis.on.write || [];
  polis.on.resize = polis.on.resize || [];

  var availableDomains = {
    prod: "https://polis.brasilqueopovoquer.org.br/",
    dev: "https://devpolis.brasilqueopovoquer.org.br/",
    local: "http://localhost:5000/"
  };

  var polisUrl = availableDomains.prod;
  console.log(document.domain);
  Object.keys(availableDomains).forEach( function(key){
    if(document.domain.match(new RegExp(availableDomains[key].replace(
      /[\w]+:\/\/([\w.]+)[\W].*/, "$1")))){
      polisUrl = availableDomains[key];
    }
  });
  console.log(polisUrl);

  function getConfig(d) {
     return {
         conversation_id: d.getAttribute("data-conversation_id"),
         site_id: d.getAttribute("data-site_id"),
         page_id: d.getAttribute("data-page_id"),
         parent_url: d.getAttribute("data-parent_url"),
         {% if user.is_authenticated %}
         xid: '{{ user.id }}',
         x_name: '{{ user.name }}',
         x_profile_image_url: '{{ user.image_url }}',
         {% else %}
         xid: d.getAttribute("data-xid"),
         x_name: d.getAttribute("data-x_name"),
         x_profile_image_url: d.getAttribute("data-x_profile_image_url"),
         {% endif %}

         border: d.getAttribute("data-border"),
         border_radius: d.getAttribute("data-border_radius"),
         padding: d.getAttribute("data-padding"),
         height: d.getAttribute("data-height"),
         demo: d.getAttribute("data-demo"),

         ucv: d.getAttribute("data-ucv"),
         ucw: d.getAttribute("data-ucw"),
         ucsh: d.getAttribute("data-ucsh"),
         ucst: d.getAttribute("data-ucst"),
         ucsd: d.getAttribute("data-ucsd"),
         ucsv: d.getAttribute("data-ucsv"),
         ucsf: d.getAttribute("data-ucsf"),

         subscribe_type: d.getAttribute("data-subscribe_type"), // 0 for no prompt, 1 for email prompt (1 is default)


         // These config variables will be used to init the conversation.
         // Subsequent loads will not update to these values in our DB.
         // To change the values after the conversation is created, go to the config tab of
         // https://pol.is/m/<conversation_id>
         show_vis: d.getAttribute("data-show_vis"),
         show_share: d.getAttribute("data-show_share"),
         bg_white: d.getAttribute("data-bg_white"),

         auth_needed_to_vote: d.getAttribute("data-auth_needed_to_vote"), // default false
         auth_needed_to_write: d.getAttribute("data-auth_needed_to_write"), // default true
         // Prompt users to auth using Facebook.
         auth_opt_fb: d.getAttribute("data-auth_opt_fb"), // default true
         // Prompt users to auth using Twitter.
         auth_opt_tw: d.getAttribute("data-auth_opt_tw"), // default true
         // This is here in case we add other auth providers (Google, etc), you can preemptively disable them by setting this to false.
         // Example: if auth_opt_fb is true, but auth_opt_allow_3rdparty is false, users will not be prompted to auth using Facebook.
         auth_opt_allow_3rdparty: d.getAttribute("data-auth_opt_allow_3rdparty"), // default true
         topic: d.getAttribute("data-topic")

     };
  }


  function createPolisIframe(parent, o) {
    var iframe = document.createElement("iframe");
    var path = [];
    if (o.demo) {
      path.push("demo");
    }
    o.parent_url = o.parent_url || window.location+"";
    var id = "polis_";
    if (o.conversation_id) {
      path.push(o.conversation_id);
      id += o.conversation_id;
    } else if (o.site_id) {
      path.push(o.site_id);
      id += o.site_id;
      if (!o.page_id) {
        alert("Error: need data-page_id when using data-site_id");
        return;
      }
      path.push(o.page_id);
      id += "_" + o.page_id;
    } else {
      alert("Error: need data-conversation_id or data-site_id");
      return;
    }
    var src = polisUrl + path.join("/");
    var paramStrings = [];

    function appendIfPresent(name) {
      if (o[name] !== null) {
        paramStrings.push(name + "=" + encodeURIComponent(o[name]));
      }
    }

    appendIfPresent("parent_url");
    if (o.parent_url) {
      paramStrings.push("referrer="+ encodeURIComponent(document.referrer));
    }

    appendIfPresent("user_is_authenticated");
    appendIfPresent("xid");
    appendIfPresent("x_name");
    appendIfPresent("x_profile_image_url");

    appendIfPresent("ucv");
    appendIfPresent("ucw");
    appendIfPresent("ucsh");
    appendIfPresent("ucst");
    appendIfPresent("ucsd");
    appendIfPresent("ucsv");
    appendIfPresent("ucsf");

    appendIfPresent("subscribe_type");

    appendIfPresent("show_vis");
    appendIfPresent("show_share");
    appendIfPresent("bg_white");
    appendIfPresent("auth_needed_to_vote");
    appendIfPresent("auth_needed_to_write");
    appendIfPresent("auth_opt_fb");
    appendIfPresent("auth_opt_tw");
    appendIfPresent("auth_opt_allow_3rdparty");
    appendIfPresent("topic");

    if (paramStrings.length) {
      src += "?" + paramStrings.join("&");
    }

    iframe.src = src;
    iframe.width = "1px"; // may be constrained by parent div
    iframe.style["min-width"] = "100%";
    iframe.scrolling = "no";
    iframe.height = o.height || 930;
    iframe.style.border = o.border || "1px solid #ccc";
    iframe.style.borderRadius = o.border_radius || "4px";
    iframe.style.padding = o.padding || "4px"; // 1px ensures that right border shows up on default wordpress theme
    iframe.style.backgroundColor = "white";
    // iframe.style.backgroundColor = "rgb(247, 247, 247)";
    iframe.id = id;
    parent.appendChild(iframe);
    iframes.push(iframe);
  }

  function encodeReturnUrl(str) {
    var x, i;
    var result = "";
    for (i=0; i<str.length; i++) {
      x = str.charCodeAt(i).toString(16);
      result += ("000"+x).slice(-4);
    }
    return result;
  }

  function outerIframeSetHeightMsg() {
    var data = {
      name: 'outerIframeSetHeightMsg',
      height: window.document.body.scrollHeight
    };
    window.top.postMessage(data, '*');
  }

  window.addEventListener("message", function(event) {
    var data = event.data||{};

    var cbList = polis.on[data.name]||[];
    var cbResults = [];
    for (var i = 0; i < cbList.length; i++) {
      cbResults.push(cbList[i]({
        iframe: document.getElementById("polis_" + data.polisFrameId),
        data: data
      }));
    }

    if (data.name === "resize") {
      var resizeWasHandled = false;
      for (var j = 0; j < cbResults.length; j++) {
        if (cbResults[j] === true) {
          resizeWasHandled = true;
        }
      }
      if (!resizeWasHandled) {
        console.log(data.polisFrameId);
        var frameId = "polis_" + data.polisFrameId;
        var iframe = document.getElementById(frameId);
        var h = data.height + 70;
        if (h > maxHeightsSeen[frameId] || typeof maxHeightsSeen[frameId] === "undefined") {
          // Prevents resize loops and excessive scrollbar flashing by only allowing iframe to expand.
          maxHeightsSeen[frameId] = h;
          iframe.setAttribute("height", h);
          iframe.style["min-width"] = "100%";
          iframe.setAttribute("width", "1px");
          iframe.setAttribute("scrolling", "no");
          outerIframeSetHeightMsg();
        }
      }
    }
  }, false);

  var loadIframes = function() {

    // Add iframes to any polis divs that don't already have iframes.
    // (check needed since this script may be included multiple times)
    var polisDivs = document.getElementsByClassName("polis");
    for (var i = 0; i < polisDivs.length; i++) {
      var d = polisDivs[i];
      if (d.children && d.children.length) {
        // already populated
      } else {
        var config = getConfig(d);
        createPolisIframe(d, config);
      }
    }
  }

  loadIframes();

  var reLoadIframes = function(user_data) {

    for (var i = 0; i < iframes.length; i++) {
      iframes[i].parentNode.removeChild(iframes[i]);
    }
    iframes = [];

    // Add iframes to any polis divs that don't already have iframes.
    // (check needed since this script may be included multiple times)
    var polisDivs = document.getElementsByClassName("polis");
    for (var i = 0; i < polisDivs.length; i++) {
      var d = polisDivs[i];
      if (d.children && d.children.length) {
        // already populated
      } else {
        var config = getConfig(d);
        config.xid = user_data.xid;
        config.x_name = user_data.x_name;
        config.x_profile_image_url = user_data.x_profile_image_url;
        createPolisIframe(d, config);
      }
    }
  }

  function loginModal(build) {
    // Remove previous instances before start
    var loginIframe = document.getElementById('pushtogether');
    if (loginIframe != null) {
      loginIframe.parentNode.removeChild(loginIframe);
    }

    // Creates de iframe
    var loginIframe = document.createElement("iframe");
    loginIframe.id = 'pushtogether';
    // loginIframe.src = 'http://localhost:8000/accounts/login/',
    loginIframe.src = 'https://ej.brasilqueopovoquer.org.br/accounts/login/',
    loginIframe.height = 600;
    loginIframe.width = "100%"; // may be constrained by parent div
    loginIframe.style["min-width"] = "100%";
    loginIframe.style.border = '0px';
    loginIframe.scrolling = "no";
    document.getElementById('modal-content').appendChild(loginIframe);

    jQuery('#myModal').modal('show');

  }

  function receiveMessage(event) {
    // if (event.data === 'askForLogin') {
    if (event.data && event.data.xid !== undefined) {
      reLoadIframes(event.data);
      jQuery('#myModal').modal('hide');
    } else if (event.data === 'askForLogin') {
      // loginModal();
    }
  }

  window.addEventListener('message', receiveMessage, false);

  window.onload = outerIframeSetHeightMsg();

  window.loadIframes = loadIframes;

}());
