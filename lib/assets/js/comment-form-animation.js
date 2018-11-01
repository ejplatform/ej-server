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


$('#id_content').keyup(updateCount);
$('#id_content').keydown(updateCount);

function updateCount() {
    var cs = $(this).val().length;
    $('#characters-count').text(cs + ' / 252');
}
