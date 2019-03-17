console.log('[EJ] hydrating HTML.');

// CONVERSATIONS
// -----------------------------------------------------------------------------
/**
 * Make slider in list view
 */
function registerSlick($elem) {
    let settings = {
        autoplay: true,
        autoplaySpeed: 5000,
        centerPadding: '0',
        prevArrow: '<i class="fa fa-chevron-left CircleButton CircleButton-leftConversationSlider"></i>',
        nextArrow: '<i class="fa fa-chevron-right CircleButton CircleButton-rightConversationSlider"></i>'
    };
    if ($elem.find('.ConversationCard').length > 1 || $elem.find('.HomeCommercial-logo').length > 1) {
        $elem.slick({
            responsive: [
                {breakpoint: 10000, settings: 'unslick'},
                {breakpoint: 550, settings: settings}
            ]
        })
    }
}
