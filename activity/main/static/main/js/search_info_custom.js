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

    // -----
    // visual for week picker (start)

    let additional_week_style =
        ".datepicker .datepicker-days tr:hover td{\n" +
        "  background: #e5e2e3;\n" +
        "  border-radius: 0;\n" +
        "}\n" +
        ".datepicker .datepicker-days tr td.active{\n" +
        "  border-radius: 0;\n" +
        "}";

    let input_week_visible = document.getElementById("id_date_week");
    setTimeout(function () {
        let input_week_hidden = getElementByXpath("//*[@id='sidebar']/div/div/form/input[2]");
        observer_hidden.observe(input_week_hidden, {attributes: true});
    }, 50);

    // returns DOM obj by its XPath
    function getElementByXpath(path) {
        return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    }

    // date obj -> "dd.mm.yyyy"
    function date_to_string(date) {
        const day = date.getDate().toString().padStart(2, "0");
        const month = (date.getMonth() + 1).toString().padStart(2, "0");
        const year = date.getFullYear();
        return `${day}.${month}.${year}`;
    }

    // calculates the dates ["dd.mm.yyyy", "dd.mm.yyyy"] of the first and last day of the week
    // for the specified date "yyyy-mm-dd"
    function calc_date(date_selected) {
        let date = new Date(date_selected);
        let day = date.getDay();
        let diff = date.getDate() - day + (day === 0 ? -6 : 1);

        let first_day = new Date(date.setDate(diff));
        let last_day = new Date(first_day);
        last_day.setDate(last_day.getDate() + 6);

        return [date_to_string(first_day), date_to_string(last_day)];
    }

    // sets visual week range (date = "yyyy-mm-dd")
    function set_week_range(date) {
        let [start, end] = calc_date(date);
        input_week_visible.value = `${start} – ${end}`;
    }

    // detects hidden input week value changes
    let observer_hidden = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            if (mutation.type === "attributes") {
                let input_week_hidden = getElementByXpath("//*[@id='sidebar']/div/div/form/input[2]");
                let date_selected = input_week_hidden.value;
                set_week_range(date_selected);
            }
        });
    });

    // detects calendar btn clicks
    let btn_calendar = document.getElementsByClassName("input-group-addon")[1]; // !!! 1 - week !!!
    btn_calendar.addEventListener("click", function () {
        // fix visual range (1)
        let d = input_week_visible.value.split(" ")[2].split(".");
        setTimeout(function () {
            set_week_range(`${d[2]}-${d[1]}-${d[0]}`);
        }, 10);
        // display active row
        setTimeout(function () {
            let td_active = document.getElementsByClassName("day active")[0];
            if (td_active) {
                let tr_parent = td_active.parentNode;
                let tr_children = Array.from(tr_parent.children);
                tr_children.forEach((item) => {
                    item.classList.add("active");
                });
                // fix visual range (2)
                let td_last = tr_children[tr_children.length - 1];
                td_last.addEventListener("click", function (e) {
                    setTimeout(function () {
                        set_week_range(`${d[2]}-${d[1]}-${d[0]}`);
                    }, 10);
                });
            }
        }, 10);
    });

    // visual for week picker (end)
    // -----

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
        },
        {
            "type": "year",
            "parent": document.getElementById("id_date_year").parentElement
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

    update_df_visibility("day");

    // detecting "display_type" changes & updating "date" fields visibility
    $(document.body).on("change", "#id_display_type", function () {
        update_df_visibility(this.value);

        // special init value for week widget
        if (this.value === "week") {
            let input_week_hidden = getElementByXpath("//*[@id='sidebar']/div/div/form/input[2]");
            if (input_week_hidden.value === "") {
                let today = new Date();
                set_week_range(today.toISOString().split("T")[0]);
            }

            let style = document.getElementById("additional-week-style");
            if (style === null) {
                style = document.createElement("style");
                style.id = "additional-week-style";
                style.innerHTML = additional_week_style
                document.head.appendChild(style);
            }
        } else {
            let style = document.getElementById("additional-week-style");
            if (style)
                style.remove();
        }
    });
});