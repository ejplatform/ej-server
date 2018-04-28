console.log('[EJ] hydrating HTML.');


// PROFILE PAGE
/**
 * Move arrow in the profile page under the active tab.
 */
up.compiler('.Profile-tabs', function ($elem) {
    var active = $elem.find('.Profile-tabActive');
    var arrow = $('.Profile-arrow');
    var x = arrow.offset().left;
    var leftMargin = active.offset().left - x + (active.width() / 2) - 28;
    arrow.css('visibility', 'inherit');
    arrow.css('margin-left', leftMargin);
});


/**
 * Make slider in list view
 */
$(function () {
    function register($elem) {
        if ($elem.find('.ConversationCard').length > 1) {
            $elem.slick({
                responsive:
                    [
                        {
                            breakpoint: 550,
                            settings: {
                                autoplay: true,
                                autoplaySpeed: 3000,
                                prevArrow: '<i class="fa fa-chevron-left CircleButton CircleButton--leftConversationSlider"></i>',
                                nextArrow: '<i class="fa fa-chevron-right CircleButton CircleButton--rightConversationSlider"></i>',
                                centerPadding: '0',
                                pauseOnFocus: true,
                                pauseOnHover: true
                            }
                        },
                        {
                            breakpoint: 10000,
                            settings: 'unslick'
                        }
                    ]
            });
        }
    }

    up.compiler('.ConversationList-cardList', function ($elem) {
        register($elem);
    });

    register($('.ConversationList-cardList'));
});




