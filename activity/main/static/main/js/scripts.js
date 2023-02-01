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

function clear_selected() {
    document.getElementById("id_group")[0].selected = false;
    document.getElementById("id_student")[0].selected = false;
}

clear_selected();