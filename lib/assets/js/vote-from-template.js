function retrieveQueryParams(urlParams) {
  var choiceValue = "";
  var commentId = "";
  for (index in urlParams) {
    var params = urlParams[index];
    var _param = params.split("=");
    if (/^.*choice.*$/.test(_param[0])) {
      choiceValue = _param[1];
    }

    if (/^.*comment_id.*$/.test(_param[0])) {
      commentId = _param[1];
    }
  }
  var data = {};
  data["choiceValue"] = choiceValue;
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
  console.log("URL");
  console.log(urlParams);
  console.log("URL");
  if (urlParams.length > 1) {
    var currentUrl = document.querySelector("body").dataset["currentUrl"];
    var queryParams = retrieveQueryParams(urlParams);
    console.log(queryParams);
    var choiceValue = queryParams.choiceValue;
    var commentId = queryParams.commentId;
    if (currentUrl != "/login/") {
      voteOnCampaignComment(choiceValue, commentId);
    } else {
      if (choiceValue && commentId) {
        localStorage.setItem("choice", choiceValue);
        localStorage.setItem("comment_id", commentId);
      }
    }
  } else {
    var choiceValue = localStorage.getItem("choice");
    var commentId = localStorage.getItem("comment_id");
    if (choiceValue && commentId) {
      location.search = `?choice=${choiceValue}&&comment_id=${commentId}`;
      localStorage.clear();
    }
  }
}

participateFromCampaign();
