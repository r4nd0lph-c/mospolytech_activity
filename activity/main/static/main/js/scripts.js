function get_groups() {
    $.ajax({
        type: "POST",
        url: "get_groups/",
        data: {csrfmiddlewaretoken: CSRF_TOKEN},
        success: function (data) {
            let groups = data["groups"];
            console.log(groups); // TODO: clear console logs
        },
        error: function () {
            console.log("get_groups() error");
        }
    });
}

function get_students(groups) {
    $.ajax({
        type: "POST",
        url: "get_students/",
        data: {
            groups: groups,
            csrfmiddlewaretoken: CSRF_TOKEN
        },
        success: function (data) {
            let students = data["students"];
            console.log(students); // TODO: clear console logs
        },
        error: function () {
            console.log("get_students() error");
        }
    });
}

function get_schedule(student, dates) {
    /* student = {"name": "...", "group": "..."} dates = ["dd.mm.yyyy", ...] */
    $.ajax({
        type: "POST",
        url: "get_schedule/",
        data: {
            name: student["name"],
            group: student["group"],
            dates: dates,
            csrfmiddlewaretoken: CSRF_TOKEN
        },
        success: function (data) {
            console.log(data); // TODO: clear console logs
        },
        error: function () {
            console.log("get_schedule() error");
        }
    });
}

function reformat_date(dateStr) {
    let dArr = dateStr.split("-");  // ex input: "2023-10-17"
    return dArr[2] + "." + dArr[1] + "." + dArr[0]; //ex output: "17.10.2023"
}

function get_days_in_month(inputDate) {
    const [year, month, day] = inputDate.split("-");
    const firstDayUTC = new Date(Date.UTC(year, month - 1, 1));
    const lastDayUTC = new Date(Date.UTC(year, month, 0));
    const daysInMonth = [];

    for (let i = 1; i <= lastDayUTC.getUTCDate(); i++) {
        // raw dayString
        // const dayString = `${year}-${month}-${String(i).padStart(2, "0")}`;
        // reformatted dayString
        const dayString = `${String(i).padStart(2, "0")}.${month}.${year}`;
        daysInMonth.push(dayString);
    }

    return daysInMonth;
}

function get_raw_date(display_type_id) {
    let raw_date = document.getElementsByName("date_" + display_type_id)[0].value;
    if (raw_date === "") {
        let today_date = new Date();
        const offset = today_date.getTimezoneOffset()
        today_date = new Date(today_date.getTime() - (offset * 60 * 1000))
        raw_date = today_date.toISOString().split("T")[0]
    }
    return raw_date;
}

$(document).ready(function () {
    let button_search = document.getElementById("btn-search");
    button_search.disabled = true;

    // detecting "student" field changes & unable / disable button_search
    $(":input[name$=student]").on("change", function () {
        let selected = $(this).select2("data")[0];
        button_search.disabled = selected.id === "";
    });

    // detecting button_search click & processing data
    button_search.onclick = function (e) {
        // creating "student" object
        let selected_student = $(":input[name$=student]").select2("data")[0].text;
        let student = {
            group: selected_student.split(")")[0].substr(1),
            name: selected_student.split(")")[1].substr(1)
        }
        // creating "dates" array
        let display_type_id = $(":input[name$=display_type]").select2("data")[0].id;
        let raw_date = get_raw_date(display_type_id);
        let dates = [];
        if (display_type_id === "day") {
            // array of dates from day
            dates = [reformat_date(raw_date)];
        } else if (display_type_id === "week") {
            // array of dates from week
            // TODO: week widget
            dates = [];
        } else if (display_type_id === "month") {
            // array of dates from month
            dates = get_days_in_month(raw_date);
        }
        console.log(student);
        console.log(dates);
    };
});