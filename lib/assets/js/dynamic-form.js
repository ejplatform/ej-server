/* Module to create dynamic forms on a django formset */

function cloneForm(element, preserve) {
    var cloned = $(element).clone(true);
    var totalForms = parseInt($("#id_form-TOTAL_FORMS").val());
    $("#id_form-TOTAL_FORMS").val(totalForms + 1);

    updateFormIndex(cloned, totalForms);
    
    if (parseInt($("#id_form-TOTAL_FORMS").val()) == 2) {
        addRemoveFormBtn(cloned);
    }

    if(preserve) {
        cloned.find('select').each(function() {
            var selectName = $(this).attr("name")
        })
    }
    cloned.appendTo(".votes_form_class");
}

function deleteForm(element) {
    var totalForms = parseInt($("#id_form-TOTAL_FORMS").val());
    $("#id_form-TOTAL_FORMS").val(totalForms - 1);
    
    element.remove();

    var forms = $(".form-row");

    forms.each(function(index) {
        updateFormIndex($(this), index);
    });

    if (parseInt($("#id_form-TOTAL_FORMS").val()) == 1) {
        $(".form-row:last").find(".remove-form-row").remove();
    }
}

/*
    Update all information (id, name, etc) that changes when a new form
    on a formset is created.
*/
function updateFormIndex(form, newIndex) {
    console.log(newIndex);
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

function addRemoveFormBtn(form) {
   var html = `
        <div class="StereotypeAdd-append">
            <button class="btn btn-danger remove-form-row"><i class="fas fa-minus"></i></button>
            <span class="">{{ _('Remove Comment') }}</span>
        </div>
    `;

    $(html).appendTo(form);
}

function generateNewId(formNumber, formType) {
    return "id_form-" + formNumber + "-" + formType;
}

function generateNewName(formNumber, formType) {
    return "form-" + formNumber + "-" + formType;
}