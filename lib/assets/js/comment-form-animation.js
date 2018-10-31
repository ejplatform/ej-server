function showForm() {
       var commentform = document.getElementById("commentform");
       if(commentform.className == "show"){
            commentform.className = "hideanimation";
            setTimeout(function(){
                commentform.className = commentform.className.replace("hideanimation", "");
            }, 500);
            timesicon = document.getElementsByClassName('fas fa-times')[0]
            timesicon.className = plusicon.className.replace("times", "plus")
       }
       else{
            commentform.className = "show";
            plusicon = document.getElementsByClassName('fas fa-plus')[0]
            plusicon.className = plusicon.className.replace("plus", "times")
       }
  }
