/* Module to create dynamic forms on a django formset */

function cloneForm(element, preserve) {
    var cloned = $(element).clone(true);
    var totalForms = parseInt($("#id_form-TOTAL_FORMS").val());
    $("#id_form-TOTAL_FORMS").val(totalForms + 1);

    
    updateFormIndex(cloned, totalForms);
        
    // if(preserve) {
    //     cloned.find('select').each(function() {
    //         var selectName = $(this).attr("name")
    //     })
    // }

    cloned.appendTo(".votes_form_class");
    
    var forms = $(".form-row");
    updateFormsRemoveBtns(forms);
    preserveSelectedOptions(forms);
}

function deleteForm(element) {
    var totalForms = parseInt($("#id_form-TOTAL_FORMS").val());
    $("#id_form-TOTAL_FORMS").val(totalForms - 1);
    
    element.remove();

    var forms = $(".form-row");

    forms.each(function(index) {
        updateFormIndex($(this), index);
    });

    updateFormsRemoveBtns(forms);
    preserveSelectedOptions(forms);
}

/*
    Update all information (id, name, etc) that changes when a new form
    on a formset is created.
*/
function updateFormIndex(form, newIndex) {
    var formNumber = newIndex;

    var oldCommentSelectId = generateNewId(formNumber - 1, "comment");
    var newCommentSelectId = generateNewId(formNumber, "comment");
    var newCommentSelectName = generateNewName(formNumber, "comment");

    var oldChoiceSelectId = generateNewId(formNumber - 1, "choice");
    var newChoiceSelectId = generateNewId(formNumber, "choice");
    var newChoiceSelectName = generateNewName(formNumber, "choice");
    var oldChoiceInputId = generateNewId(formNumber - 1, "id");
    var newChoiceInputId = generateNewId(formNumber, "id");
    var newChoiceInputName = generateNewName(formNumber, "id");


    // Comment form
    var commentSelectLabel = form.find("label[for='" + oldCommentSelectId + "']");
    commentSelectLabel.attr("for", newCommentSelectId);
    
    var commentSelect = form.find("#" + oldCommentSelectId);
    commentSelect.attr("name", newCommentSelectName);
    commentSelect.attr("id", newCommentSelectId);
    

    // Vote choice form
    var choiceSelectLabel = form.find("label[for='" + oldChoiceSelectId + "']");
    choiceSelectLabel.attr("for", newChoiceSelectId);
    
    var choiceSelect = form.find("#" + oldChoiceSelectId);
    choiceSelect.attr("name", newChoiceSelectName);
    choiceSelect.attr("id", newChoiceSelectId);

    var choiceSelectInput = form.find("#" + oldChoiceInputId);
    choiceSelectInput.attr("name", newChoiceInputName);
    choiceSelectInput.attr("id", newChoiceInputId);
}

function updateFormsRemoveBtns(forms) {
    var totalForms = parseInt($("#id_form-TOTAL_FORMS").val());
    forms.each(function(index) {
        if (totalForms == 1) {
            $(this).find(".StereotypeAdd-append").attr("style", "display: none;");
        } else {
            $(this).find(".StereotypeAdd-append").attr("style", "");
        }
    });
}

function preserveSelectedOptions(forms) {
    var selectedOptions = []

    forms.each(function(index) {
        var commentSelect = $(this).find('.comment_select');
        var selectedOption = $("option:selected", commentSelect).val();
        if (selectedOption != "") {
            selectedOptions.push(selectedOption);
        }
    });

    forms.each(function(index) {
        var commentSelect = $(this).find('.comment_select');
        var options = $("option", commentSelect);

        options.each(function(index) {
            var option = $(this);

            if (isOnList(option.val(), selectedOptions)) {
                option.attr("disabled", true);
            } else {
                option.attr("disabled", false);
            }
        })
    });
}

function isOnList(element, list) {

    for(i=0; i<list.length; i++) {
        if (element == list[i]) {
            return true;
        }
    }
    return false;
}

function addRemoveFormBtn(form) {
    form.find(".StereotypeAdd-append").attr("style", "");
}

function generateNewId(formNumber, formType) {
    return "id_form-" + formNumber + "-" + formType;
}

function generateNewName(formNumber, formType) {
    return "form-" + formNumber + "-" + formType;
}

(function (){
    $(".comment_select").focus(function () {}).change(function() {
        preserveSelectedOptions($(".form-row"));
    })
})();