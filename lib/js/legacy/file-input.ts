var initialFileStatus = $(".FileStatus").text();

var pickFileFunction = function (){
    elements = $(".PickFileButton");

    elements.each(function(index) {
        children = $(this).children();
        status = $(this).siblings()

        children.blur(function() {
            $(this).parent().css("background-color", "#A3D8DD")
            $(this).parent().css("color", "#052B47");
        })


        children.focus(function() {
            $(this).parent().css("background-color", "#30BFD3")
            $(this).parent().css("color", "white")
        })


        children.change(function() {
            var files = $(this)[0].files
            var fileName = files.length > 0 ? files[0].name : null
            changeFileStatus($(this).parent(), fileName);
        })
    })
};

function changeFileStatus(pickFile, newText) {
    fileStatus = pickFile.siblings();

    if (newText) {
        fileStatus.text(newText);
        fileStatus.css("background-color", "#C4F2F4")
    }else {
        fileStatus.text(initialFileStatus);
        fileStatus.css("background-color", "white")
    }
}

pickFileFunction();