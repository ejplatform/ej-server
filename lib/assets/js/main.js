console.log('[EJ] hydrating HTML.');

// PROFILE
// -----------------------------------------------------------------------------
/**
 * Move arrow in the profile page under the active tab.
 */
up.compiler('.Profile-tabs', function ($elem) {
    $elem.ready(function () {
            let $active = $elem.find('.Profile-tabActive');
            let $arrow = $elem.find('.Profile-arrow');
            let arrowOffset = $arrow.offset();
            let activeOffset = $active.offset();

            if (arrowOffset !== undefined && activeOffset !== undefined) {
                let x = arrowOffset.left;
                let leftMargin = activeOffset.left - x + ($active.width() / 2) - 28;
                $arrow.css('visibility', 'inherit');
                $arrow.css('margin-left', leftMargin);
            }
        }
    );
});

up.compiler('.CollapsibleList', function ($elem) {
    $elem.toggleClass('CollapsibleList--hidden');
    $elem.find('.CollapsibleList-data').hide();

    $elem.click(function () {
        $elem.find('> h2 > i').css('transition', '500ms');
        $elem.toggleClass('CollapsibleList--hidden');
        $elem.find('.CollapsibleList-data').toggle(250);
    });
});


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

up.compiler('.ConversationList-cardList', function ($elem) {
    registerSlick($elem);
});

up.compiler('#HomeCommercial-logos', function ($elem) {
    registerSlick($elem);
});

// Navigate to board url
up.compiler('#select-board', function () {
    $(this).on('change', function () {
        window.location = this.value;
    });
});


// HOME PAGE
// -----------------------------------------------------------------------------
up.compiler('.HowItWorksCard-extra', function ($elem) {
    $elem.addClass('hide-on-small');
});

up.compiler('.HowItWorksCard', function ($card) {
    $card.find('.HowItWorksCard-content h1').click(function () {
        $card.find('.HowItWorksCard-content h1').toggleClass('expanded');
        $card.find('.HowItWorksCard-extra').toggleClass('hide-on-small');
    })
});


// Profile edit
up.compiler('#id_image', function ($fileInput) {
    $fileInput.change(function () {
        let $displayedFileName = $('#image-filename');
        let filename = $fileInput.prop('files')[0].name;
        $displayedFileName.text(filename);
    })
});

console.log('[EJ] finished.');



