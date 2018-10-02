/* Module to create dynamic forms on a django formset */


function cloneForm(element, preserve) {
    var cloned = $(element).clone(true);
    updateClonedFormAttributes(cloned);

    if(preserve) {
        cloned.find('select').each(function() {
            var selectName = $(this).attr("name")
        })
    }
    cloned.appendTo(".votes_form_class");
}

/*
    Update all information (id, name, etc) that changes when a new form
    on a formset is created.
*/
function updateClonedFormAttributes(clonedForm) {
    var totalForms = parseInt($("#id_form-TOTAL_FORMS").val());
    var formNumber = totalForms;

    $("#id_form-TOTAL_FORMS").val(totalForms + 1);

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
    var commentSelectLabel = clonedForm.find("label[for='" + oldCommentSelectId + "']");
    commentSelectLabel.attr("for", newCommentSelectId);
    
    var commentSelect = clonedForm.find("#" + oldCommentSelectId);
    commentSelect.attr("name", newCommentSelectName);
    commentSelect.attr("id", newCommentSelectId);
    

    // Vote choice form
    var choiceSelectLabel = clonedForm.find("label[for='" + oldChoiceSelectId + "']");
    choiceSelectLabel.attr("for", newChoiceSelectId);
    
    var choiceSelect = clonedForm.find("#" + oldChoiceSelectId);
    choiceSelect.attr("name", newChoiceSelectName);
    choiceSelect.attr("id", newChoiceSelectId);

    var choiceSelectInput = clonedForm.find("#" + oldChoiceInputId);
    choiceSelectInput.attr("name", newChoiceInputName);
    choiceSelectInput.attr("id", newChoiceInputId);
}

function generateNewId(formNumber, formType) {
    return "id_form-" + formNumber + "-" + formType;
}

function generateNewName(formNumber, formType) {
    return "form-" + formNumber + "-" + formType;
}