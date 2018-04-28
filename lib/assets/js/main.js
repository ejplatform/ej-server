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


