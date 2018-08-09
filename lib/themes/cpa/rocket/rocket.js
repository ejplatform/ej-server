//Add your script

$(document).ready(function() {
  
  $('footer a').first().click(function() {
    $(window)[0].menu.close();
  });
  
  //$('.rooms-list__type-text').html('Canais');
  //$('.rooms-list__type-text')[1].innerHTML='Canais privados';
  $('.rooms-list__type-text')[1].replaceWith('Canais privados');
  
  
  
});
