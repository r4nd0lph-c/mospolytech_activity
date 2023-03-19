$(document).ready(function () {
    // removing empty choice "-----" for select2 field with given id
    function remove_empty_option(select_id) {
        document.getElementById(select_id)[0].selected = false;
    }

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

    // finding "date" fields parents
    let date_fields = [
        {
            "type": "day",
            "parent": document.getElementById("id_date_day").parentElement
        },
        {
            "type": "week",
            "parent": document.getElementById("id_date_week").parentElement
        },
        {
            "type": "month",
            "parent": document.getElementById("id_date_month").parentElement
        }
    ]

    // updating "date" fields visibility
    function update_df_visibility(val) {
        date_fields.forEach(obj => {
            if (obj["type"] === val) {
                obj["parent"].style.display = "flex";
            } else {
                obj["parent"].style.display = "none";
            }
        });
    }

    // TODO: make visual for week picker

    update_df_visibility("day");

    // detecting "display_type" changes & updating "date" fields visibility
    $(document.body).on("change", "#id_display_type", function () {
        update_df_visibility(this.value);
    });
});