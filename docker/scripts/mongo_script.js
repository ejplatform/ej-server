const script = "\n" +
    "//Add your script\n" +
    "$(document).ready(function() {\n" +
    "\n" +
    "  $('footer a').first().click(function() {\n" +
    "    $(window)[0].menu.close();\n" +
    "  });\n" +
    "  \n" +
    "  $('.rooms-list .rooms-list__type-text:eq(1)').html('Canais Privados');\n" +
    "  $('.rooms-list .rooms-list__type-text:eq(1)').on( \"DOMNodeInserted\", function($event) {\n" +
    "    if($('.rooms-list .rooms-list__type-text:eq(1)').html() !== 'Canais Privados'){\n" +
    "       $('.rooms-list .rooms-list__type-text:eq(1)').html('Canais Privados')\n" +
    "     }\n" +
    "  });\n" +
    "  \n" +
    "});\n";


db.rocketchat_settings.findAndModify({
    query: {_id: "Custom_Script_Logged_In"},
    sort: {createdAt: 1},
    update: {$set: {"value": script}}
});
