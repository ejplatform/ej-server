//Add your script
$(document).ready(function() {
  
  $('footer a').first().click(function() {
    $(window)[0].menu.close();
  });
  
  $('.rooms-list .rooms-list__type-text:eq(1)').html('Canais Privados');
  $('.rooms-list .rooms-list__type-text:eq(1)').on( "DOMNodeInserted", function($event) {
    if($('.rooms-list .rooms-list__type-text:eq(1)').html() !== 'Canais Privados'){
       $('.rooms-list .rooms-list__type-text:eq(1)').html('Canais Privados')
     }
  });
  
});
