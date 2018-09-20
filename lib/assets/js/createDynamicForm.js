function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

function cloneMore(selector, prefix) {
    var newElement = $(selector).clone(true);
    var selected = $("option:selected", $('.comment_select:last')).val();
    var total = $('.comment_select').length;
    newElement.find('select').each(function() {
        var name = $(this).attr('name').replace('-' + (total-1) + '-', '-' + (total) + '-');
        var id = 'id_' + name;
        this.setAttribute("name", name);
        this.setAttribute("id", id);
    });
    newElement.find(".comment_select").each(function(){
      $("option[value='" + selected + "']", $(this)).attr("disabled", true);
    });
    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
    var conditionRow = $('.form-row:not(:last)');
    conditionRow.find('.btn.add-form-row')
    .removeClass('btn-success').addClass('btn-danger')
    .removeClass('add-form-row').addClass('remove-form-row')
    .html('<i class="fas fa-minus"></i>');
    return false;
}



function deleteForm(prefix, btn) {
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (total > 1){
        btn.closest('.form-row').remove();
        var forms = $('.form-row');
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        for (var i=0, formCount=forms.length; i<formCount; i++) {
            $(forms.get(i)).find(':input').each(function() {
                updateElementIndex(this, prefix, i);
            });
        }
    }
    return false;
}


(function () {
    var previous;

    $(".comment_select").focus(function () {
        previous = this.value;
    }).change(function() {
      var selected = $("option:selected", $(this)).val();
      // Get the ID of this element
      var thisID = $(this).attr("id");
      // Reset so all values are showing:
      $(".comment_select option").each(function() {
          $(this).show();
      });
      $(".comment_select").each(function() {
          if ($(this).attr("id") != thisID) {
              $("option[value='" + selected + "']", $(this)).attr("disabled", true);
          }
          $("option[value='" + previous + "']", $(this)).attr("disabled", false);
      });
    });
})();



$(document).on('click', '.add-form-row', function(e){
    e.preventDefault();
    cloneMore('.form-row:last', 'form');
    return false;
});
$(document).on('click', '.remove-form-row', function(e){
    e.preventDefault();
    deleteForm('form', $(this));
    return false;
});
