$(document).ready(function () {
    // bind on group field change
    $(":input[name$=group]").on("change", function () {
        // get the field prefix, ie. if this comes from a formset form
        let prefix = $(this).getFormPrefix();
        // clear the autocomplete with the same prefix
        $(":input[name=" + prefix + "student]").val(null).trigger("change");
    });
});