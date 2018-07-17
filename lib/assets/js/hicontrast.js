let checkHicontrast = function() {
    let bodyDiv = document.getElementsByTagName('body')[0];
    
    if(localStorage.hicontrast == "true" && bodyDiv.className.indexOf("hicontrast") == -1){
        bodyDiv.className += " hicontrast";
    }        
}