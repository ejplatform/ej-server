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


/**
 * It receives an URL and calls the callback function with the concated url
 * as a parameter.
 * @param {String} url 
 * @param {Function} cb
 */
const concatCoordsAsQuery = (url, cb) => {
    let query = url
    navigator.geolocation.getCurrentPosition(pos => {
      query += `?latitude=${pos.coords.latitude}&longitude=${pos.coords.longitude}`
      cb(query)
    })
}

/**
 * On loading profile screen, it updates the href propery from the button that
 * redirects to edit profile form. It gives the user 1s for decide to give
 * permissions or not for getting the coordinates.
 */
const onLoadProfileDetails = () => {
    const btn = document.getElementById('edit-profile-link')

    if(btn) {
        concatCoordsAsQuery(btn.href, (newUrl) => { 
           btn.href = newUrl
        });
    }
}