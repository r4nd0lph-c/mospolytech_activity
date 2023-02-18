// removing empty choice "-----" for field with given id
function remove_empty_option(select_id) {
    document.getElementById(select_id)[0].selected = false;
}

$(document).ready(function () {

    // clearing "student" field if "group" field is changed
    $(":input[name$=group]").on("change", function () {
        let prefix = $(this).getFormPrefix();
        $(":input[name=" + prefix + "student]").val(null).trigger("change");
    });

    // closing "group" list if "remove all items" was pressed
    // removing "group" empty choice "-----"
    $("#id_group").on("select2:unselecting", function (e) {
        $(this).data('unselecting', true);
        remove_empty_option("id_group");
    }).on("select2:opening", function (e) {
        if ($(this).data("unselecting")) {
            $(this).removeData("unselecting");
            e.preventDefault();
        }
    });

    // closing "student" list if "remove all items" was pressed
    $("#id_student").on("select2:unselecting", function (e) {
        $(this).data('unselecting', true);
    }).on("select2:opening", function (e) {
        if ($(this).data("unselecting")) {
            $(this).removeData("unselecting");
            e.preventDefault();
        }
    });

    // removing "group" empty choice "-----"
    remove_empty_option("id_group");

    // making "display_type" choice field default style looks like select2 style
    // hiding "display_type" search field
    $("#id_display_type").select2({
        minimumResultsForSearch: Infinity
    });
});