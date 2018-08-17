
// function that enables fadein/fadeout of lower nav
function enableFadeBottomDiv() {
    $(document).ready(function () {
        var lastScrollTop = 0;
        function hideLowerNav(windowWidth) {
            if (windowWidth <= 550) {
                $('.Page').css({'padding': '75px 0 0 0', 'transition': 'padding 0.3s linear'});
            } else {
                $('.Page').css({'padding': '100px 0 0 0', 'transition': 'padding 0.3s linear'});
            }
        }
        function showLowerNav(windowWidth) {
            if (windowWidth <= 550) {
                $('.Page').css({'padding': '75px 0 70px 0', 'transition': 'padding 0.3s linear'});
            } else {
                $('.Page').css({'padding': '100px 0 70px 0', 'transition': 'padding 0.3s linear'});
            }
        }

        $("div").scroll(function () {
            var windowWidth = window.innerWidth;
            var st = $(this).scrollTop();
            if (lastScrollTop < st - 10) {
                $('.Header-lowerNav').fadeOut('fast', hideLowerNav(windowWidth));
                $('.Header-lowerNotLogged').fadeOut('fast', hideLowerNav(windowWidth));
            }

            if (lastScrollTop > st + 10) {
                $('.Header-lowerNav').fadeIn('fast', showLowerNav(windowWidth));
                $('.Header-lowerNotLogged').fadeIn('fast', showLowerNav(windowWidth));
            }
            lastScrollTop = st;
        });
    });
}
enableFadeBottomDiv();