
// function that enables fadein/fadeout of lower nav
function enableFadeBottomDiv() {
    $(document).ready(function () {
        var lastScrollTop = 0;
        
        $("div").scroll(function () {
            var windowWidth = window.innerWidth;
            var st = $(this).scrollTop();
            if (lastScrollTop < st) {
                $('.Header-lowerNav').fadeOut();
                if (windowWidth <= 550) {
                    $('.Page').css('padding', '75px 0 0 0');
                } else {
                    $('.Page').css('padding', '100px 0 0 0');
                }
            }
            else {
                $('.Header-lowerNav').fadeIn();
                if (windowWidth <= 550) {
                    $('.Page').css('padding', '75px 0 70px 0');
                } else {
                    $('.Page').css('padding', '100px 0 70px 0');
                }
            }
            lastScrollTop = st;
        });
    });
}
enableFadeBottomDiv();