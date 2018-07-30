
// function that enables fadein/fadeout of lower nav
function enableFadeBottomDiv() {
    $(document).ready(function () {
        var lastScrollTop = 0;
        $("div").scroll(function () {
            var st = $(this).scrollTop();
            if (lastScrollTop < st) {
                $('.Header-lowerNav').fadeOut();
            }
            else {
                $('.Header-lowerNav').fadeIn();
            }
            lastScrollTop = st;
        });
    });
}
enableFadeBottomDiv();