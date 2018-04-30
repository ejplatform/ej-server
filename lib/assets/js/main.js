console.log('[EJ] hydrating HTML.');


// Profile
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


// Conversations
/**
 * Make slider in list view
 */
function registerSlick($elem) {
    var settings = {
        autoplay: true,
        autoplaySpeed: 5000,
        centerPadding: '0',
        prevArrow: '<i class="fa fa-chevron-left CircleButton CircleButton--leftConversationSlider"></i>',
        nextArrow: '<i class="fa fa-chevron-right CircleButton CircleButton--rightConversationSlider"></i>'
    };
    if ($elem.find('.ConversationCard').length > 1) {
        $elem.slick({
            responsive: [
                {breakpoint: 10000, settings: 'unslick'},
                {breakpoint: 550, settings: settings}
            ]
        })
    }
}

up.compiler('.ConversationList-cardList', function ($elem) {
    registerSlick($elem);
});


// Home page
up.compiler('.HowItWorksCard-extra', function ($elem) {
    $elem.addClass('hide-on-small');
});

up.compiler('.HowItWorksCard', function ($card) {
    $card.find('.HowItWorksCard-content h1').click(function () {
        $card.find('.HowItWorksCard-content h1').toggleClass('expanded');
        $card.find('.HowItWorksCard-extra').toggleClass('hide-on-small');
    })
});

console.log('[EJ] finished.');

