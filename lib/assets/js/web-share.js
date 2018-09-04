
// web share only works in https connections
function webShare() {
    if (navigator.share != undefined) {
        console.log('Sharing EJ content')
        window.navigator.share({
            title: 'EJ',
            url: 'http://dev.ejplatform.org'
        })
    }
}