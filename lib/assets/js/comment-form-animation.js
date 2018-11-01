function showForm(button) {
       var commentform = document.getElementById("commentform");
       buttonicon = button[0].firstElementChild
       if(commentform.className == "show"){
            commentform.className = "hideanimation";
            setTimeout(function(){
                commentform.className = commentform.className.replace("hideanimation", "");
            }, 500);
            buttonicon.className = buttonicon.className.replace("times", "plus")
       }
       else{
            commentform.className = "show";
            buttonicon.className = buttonicon.className.replace("plus", "times")
       }
  }
