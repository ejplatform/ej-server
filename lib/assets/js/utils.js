
// function that enables fadein/fadeout of lower nav
function enableFadeBottomDiv() {
    $(document).ready(function () {
        var lastScrollTop = 0;
        $("div").scroll(function () {
            var st = $(this).scrollTop();
            if (lastScrollTop < st) {
                $('.Header-lowerNav').fadeOut();
                $('.Page').css('padding', '75px 0 0 0');
            }
            else {
                $('.Header-lowerNav').fadeIn();
                $('.Page').css('padding', '75px 0 70px 0');
            }
            lastScrollTop = st;
        });
    });
}
enableFadeBottomDiv();