function retrieveQueryParams(urlParams) {
  var voteValue = "";
  var commentId = "";
  for (index in urlParams) {
    var params = urlParams[index];
    var _param = params.split("=");
    if (/^.*vote.*$/.test(_param[0])) {
      voteValue = _param[1];
    }

    if (/^.*comment_id.*$/.test(_param[0])) {
      commentId = _param[1];
    }
  }
  var data = {};
  data["voteValue"] = voteValue;
  data["commentId"] = commentId;
  return data;
}

function voteOnCampaignComment(choice, commentId) {
  if (choice && commentId) {
    const commentCard = document.querySelector('input[name="comment_id"]');
    if (commentCard.value == commentId) {
      var choiceButton = document.querySelector(`button[value=${choice}]`);
      setTimeout(function() {
        choiceButton.click();
      }, 1000);
    } else {
      location.search = "";
    }
  }
}

function participateFromCampaign() {
  var urlParams = location.search.split("&");
  if (urlParams.length > 1) {
    var isLogged = !document.querySelector(".Header-lowerNotLogged");
    var queryParams = retrieveQueryParams(urlParams);
    var voteValue = queryParams.voteValue;
    var commentId = queryParams.commentId;
    if (isLogged) {
      voteOnCampaignComment(voteValue, commentId);
    } else {
      if (voteValue && commentId) {
        localStorage.setItem("vote", voteValue);
        localStorage.setItem("comment_id", commentId);
      }
    }
  } else {
    var voteValue = localStorage.getItem("vote");
    var commentId = localStorage.getItem("comment_id");
    if (voteValue && commentId) {
      location.search = `?vote=${voteValue}&&comment_id=${commentId}`;
      localStorage.clear();
    }
  }
}

participateFromCampaign();
