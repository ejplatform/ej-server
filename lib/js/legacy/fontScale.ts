let fontSizeLimit = 4;

let checkFontSize = () => {
    if(localStorage.fontSize === undefined){
        localStorage.fontSize = 0;
    }

    if(localStorage.fontSize != 0) {
        var divs = document.body.getElementsByTagName("*");
        for(var i = 0; i < divs.length; i++){
            divs[i].style.fontSize = parseInt(getComputedStyle(divs[i]).fontSize.replace(/px/,"")) + "px";
        }

        for(var i = 0; i < divs.length; i++){
            divs[i].style.fontSize = parseInt(getComputedStyle(divs[i]).fontSize.replace(/px/,"")) + parseInt(localStorage.fontSize) + "px";
        }
    }
}


let checkClassMenuFontSize = () => {
    if(localStorage.fontSize === undefined){
        localStorage.fontSize = 0;
    }

    if(localStorage.fontSize != 0) {
        var divs = document.getElementsByClassName("NavMenu")[0].getElementsByTagName("*");
        for(var i = 0; i < divs.length; i++){
            divs[i].style.fontSize = parseInt(getComputedStyle(divs[i]).fontSize.replace(/px/,"")) + "px";
        }

        for(var i = 0; i < divs.length; i++){
            divs[i].style.fontSize = parseInt(getComputedStyle(divs[i]).fontSize.replace(/px/,"")) + parseInt(localStorage.fontSize) + "px";
        }
    }
}

let increaseFontSize = () => {

    if(localStorage.fontSize >= fontSizeLimit){
        return;
    }

    var divs = document.body.getElementsByTagName("*");
    for(var i = 0; i < divs.length; i++){
        divs[i].style.fontSize = parseInt(getComputedStyle(divs[i]).fontSize.replace(/px/,"")) + "px";
    }

    for(var i = 0; i < divs.length; i++){
		divs[i].style.fontSize = parseInt(getComputedStyle(divs[i]).fontSize.replace(/px/,"")) + 1 + "px";
    }

    if(localStorage.fontSize != undefined){
        localStorage.fontSize++;
    } else {
        localStorage.fontSize = 1;
    }
}

let decreaseFontSize = () => {

    if(localStorage.fontSize <= -fontSizeLimit){
        return;
    }

    var divs = document.body.getElementsByTagName("*");
    for(var i = 0; i < divs.length; i++){
        divs[i].style.fontSize = parseInt(getComputedStyle(divs[i]).fontSize.replace(/px/,"")) + "px";
    }

    for(var i = 0; i < divs.length; i++){
		divs[i].style.fontSize = parseInt(getComputedStyle(divs[i]).fontSize.replace(/px/,"")) - 1 + "px";
    }

    if(localStorage.fontSize != undefined){
        localStorage.fontSize--;
    } else {
        localStorage.fontSize = -1;
    }
}

let setStandardFontSize = () => {
    var auxFontSize = - parseInt(localStorage.fontSize);
    var divs = document.body.getElementsByTagName("*");
    for(var i = 0; i < divs.length; i++){
        divs[i].style.fontSize = parseInt(getComputedStyle(divs[i]).fontSize.replace(/px/,"")) + "px";
    }

    for(var i = 0; i < divs.length; i++){
        divs[i].style.fontSize = parseInt(getComputedStyle(divs[i]).fontSize.replace(/px/,"")) + auxFontSize + "px";
    }
    localStorage.fontSize = 0;
}
