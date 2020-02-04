function urlParamsToObject(urlParams) {
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

function vote(choice, commentId) {
  if (choice && commentId) {
    const commentCard = document.querySelector('input[name="comment_id"]');
    if (commentCard.value == commentId) {
      var choiceButton = document.querySelector(`button[value=${choice}]`);
      setTimeout(function() {
        console.log("votou");
        choiceButton.click();
      }, 1000);
    }
  }
}

function storeChoiceToUseAfterLogin(choiceValue, commentId) {
  if (choiceValue && commentId) {
    localStorage.setItem("choice", choiceValue);
    localStorage.setItem("comment_id", commentId);
  }
}

function setUrlParamsAfterLogin() {
  var choiceValue = localStorage.getItem("choice");
  var commentId = localStorage.getItem("comment_id");
  if (choiceValue && commentId) {
    location.search = `?choice=${choiceValue}&&comment_id=${commentId}`;
    localStorage.clear();
  }
}

function voteFromTemplate() {
  let urlParams = location.search.split("&");
  if (urlParams.length > 1) {
    let queryParams = urlParamsToObject(urlParams);
    let choiceValue = queryParams.choiceValue;
    let commentId = queryParams.commentId;
    let currentUrl = document.querySelector("body").dataset["currentUrl"];
    if (currentUrl != "/login/" && currentUrl != "/register/") {
      vote(choiceValue, commentId);
    } else {
      storeChoiceToUseAfterLogin(choiceValue, commentId);
    }
  } else {
    setUrlParamsAfterLogin();
  }
}

window.onload = voteFromTemplate;
