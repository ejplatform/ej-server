
// web share only works in https connections
function webShare() {
    let url = window.location;
    if (navigator.share) {
        console.log('Sharing EJ content')
        window.navigator.share({
            title: 'EJ',
            url: url
        });
    } else {
        let dummyInput = document.createElement('input'), text = url;
        document.body.appendChild(dummyInput);
        dummyInput.value = text;
        dummyInput.select();
        document.execCommand('copy');
        document.body.removeChild(dummyInput);
        
        alert("Link added to clipboard!");
    }
}