let checkSpecificPages = (fragment) => {
    if(fragment[0].className == "Profile-tabs"){
        fillTrophies();
    }
    
    if(fragment[0].className != "NavMenu"){
        checkFontSize();
    } else {
        checkClassMenuFontSize();
    }
    
}



//profile fill empty trophies
let fillTrophies = function() {
    var icon = 'icon_trofeu';
    if(localStorage.hicontrast == 'true'){
        icon = 'icon_trofeu_dark'
    }

    var trophyImageDivs = document.getElementsByClassName('blank-trophy');
    for(let i in trophyImageDivs){
        trophyImageDivs[i].src = `/static/img/icons/${icon}.svg`
    }
}