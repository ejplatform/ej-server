console.log('[EJ] hydrating HTML.');

// MAIN LINKS
/**
 * Append ?target=main to all links targeting the main page content.
 */
up.compiler('[up-target]', function ($elem) {
    if ($elem.attr('up-target') == '.Page-mainContainer') {
        var href = $elem.attr('href');
        var query = href.indexOf('?');
        href = href + ((query === -1)? '?': '&') + 'target=main';
        $elem.attr('href', href);
    }
});


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


