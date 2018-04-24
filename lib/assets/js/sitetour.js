/**
 * Register a simple site tour using Intro.js.
 */
(function ($) {
    // TODO: consider a more powerful lib such as Shepherd (http://github.hubspot.com/shepherd/)
    // or Slideshow (http://fortesinformatica.github.io/Sideshow/)

    // jQuery selectors
    var firstConversationCard = $('.ConversationCard');
    var firstConversationLink = firstConversationCard.attr('href');
    var intro = introJs();

    // Configure options
    intro.setOptions({
        disableInteraction: false,
        showProgress: true,
        showBullets: false,
        steps: [
            {
                intro: (
                    '<div style="width: 50vh">' +
                    '<h1>Welcome to Empurrando juntos!</h1>' +
                    '<p>This tour will explain how the platform works and how can you participate.</p>' +
                    '<p>We are commited to provide a friendly and inclusive environment for social participation.</p>' +
                    '</div>'
                )
            },
            {
                element: $('#conversations-link')[0],
                intro: (
                    '<h1>Conversations</h1>' +
                    '<p>Our journey starts here! In "conversations" we see which topics of discussion are hot now.</p>' +
                    "<p>You don't have to click here here because we are already on the conversations page.</p>"
                )
            },
            {
                element: firstConversationCard[0],
                intro: (
                    '<p>A conversation is a place that we can share opinions and post comments about a given topic.</p>' +
                    '<a>Click on the conversation title or <a href="' + firstConversationLink + '" up-target=".Content-main">here</a>.</p>'
                )
            },
            {
                element: $('.Conversation-voteArea'),
                intro: (
                    '<h1>Vote!</h1>' +
                    '<a>We want to know your opinion about things. Please vote if you agree or disagree with the selected comment.</p>'
                )
            },
            {
                intro: (
                    '<h1>How does it work?</h1>' +
                    '<a>After you cast a few votes, we\'ll analyze your opinion profile and classify it in one of many clusters.</p>'
                )
            }
        ]
    });


    intro.start();
})(jQuery);

