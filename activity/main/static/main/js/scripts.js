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

function get_schedule(student, dates, display_type_id) {
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
            display_schedule(data, dates, display_type_id);
        },
        error: function () {
            console.log("get_schedule() error");
        }
    });
}

function get_year_activity(student, start_year) {
    /* student = {"name": "...", "group": "..."} year = "YYYY" */
    $.ajax({
        type: "POST",
        url: "get_year_activity/",
        data: {
            name: student["name"],
            group: student["group"],
            start_year: start_year,
            csrfmiddlewaretoken: CSRF_TOKEN
        },
        success: function (data) {
            console.log(data); // TODO: clear console logs
            display_year_activity(data, student, start_year);
        },
        error: function () {
            console.log("get_year_activity() error");
            display_year_activity(null, student, start_year);
        }
    });
}


// ----- ----- ----- ----- ----- ----- ----- ----- ----- -----


// DOM objects init
let screens = [
    document.getElementById("empty_filler"),
    document.getElementById("zero_schedule"),
    document.getElementById("schedule_day"),
    document.getElementById("schedule_week"),
    document.getElementById("schedule_month"),
    document.getElementById("schedule_year")
];

// disabling screens
function disable_screens(exception) {
    screens.forEach(function (scrn) {
        if (scrn.id === exception)
            scrn.style.display = "block";
        else
            scrn.style.display = "none";
    });
}

const uid = function () {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

let create_card_day = (parent, info) => {

    let card = document.createElement("div");
    card.className = "card card-schedule row";
    card.id = `card-${uid()}`;

    let col_activity = document.createElement("div");
    col_activity.className = "col-1 activity_bar";

    let col_body = document.createElement("div");
    col_body.className = "col-11 body_bar";

    let cardBody = document.createElement("div");
    cardBody.className = "card-body";

    let header = document.createElement("h6");
    header.className = "card-title";

    let text = document.createElement("p");
    text.className = "card-text";

    let subtext = document.createElement("p");
    subtext.className = "card-text";
    subtext.style.color = "var(--text-secondary)";
    subtext.style.margin = "0";

    if (!!info["subject"]) {
        header.innerText = `${info["time"][0]} – ${info["time"][1]}`;
        if (info["subject"]["location"] !== "")
            header.innerText += ` (${info["subject"]["location"]})`;
        text.innerText = `${info["subject"]["title"]}`;
        if (info["subject"]["type"] !== "")
            text.innerText += ` (${info["subject"]["type"]})`;
        if (info["subject"]["teachers"].length > 0)
            subtext.innerText = info["subject"]["teachers"].join(", ");
    } else {
        header.innerText = `${info["time"][0]} – ${info["time"][1]}`;
        text.innerText = "-----";
        subtext.innerText = "";
    }

    cardBody.appendChild(header);
    cardBody.appendChild(text);
    cardBody.appendChild(subtext);
    col_body.appendChild(cardBody);
    card.appendChild(col_activity);
    card.appendChild(col_body);
    parent.appendChild(card);

    return card.id;
}

let create_nav_student_info = (name, date) => {
    let nav_selected_student = document.getElementById("nav-selected-student");
    nav_selected_student.innerHTML = "";

    let h5 = document.createElement("h5");
    h5.className = "fw-light m-0";
    h5.innerText = "Студент ";

    let b = document.createElement("b");
    b.innerText = `${name}`;

    let p = document.createElement("p");
    p.innerText = `${date}`;
    p.style.color = "var(--text-secondary)";
    p.style.margin = "0";

    h5.appendChild(b);
    nav_selected_student.appendChild(h5);
    nav_selected_student.appendChild(p);
}

// changing screens for schedules
function display_schedule(data, required_dates, display_type_id) {
    // changing process
    if (display_type_id === "day") {
        // render for day
        if (data["schedule"].length === 0) {
            create_nav_student_info(data["student"]["name"], format_date_for_nav(required_dates[0]));
            disable_screens("zero_schedule");
            ["prev", "next"].forEach(function (tag) {
                let btn_day = document.getElementById(`z-btn-${tag}`);
                let clone_btn = btn_day.cloneNode(true);
                btn_day.parentNode.replaceChild(clone_btn, btn_day);
                clone_btn.addEventListener("click", function (e) {
                    let new_date = change_date_per_one(required_dates[0], tag);
                    get_schedule(data["student"], [new_date], "day");
                });
            });
        } else {
            let date = data["schedule"][0]["date"];
            create_nav_student_info(data["student"]["name"], format_date_for_nav(date));
            disable_screens("schedule_day");
            let row = document.getElementById("schedule_day_row");
            let cols = row.children;
            cols[0].innerHTML = "";
            cols[1].innerHTML = "";
            let col_num = 0;
            let created_cards_id = [];
            for (let i = 0; i < data["schedule"][0]["day"].length; i++) {
                let info = data["schedule"][0]["day"][i];
                if (i === 3) {
                    let info_additional = {
                        subject: {
                            title: "Обеденный перерыв",
                            type: "",
                            location: "",
                            teachers: []
                        },
                        time: ["13:50", "14:30"]
                    };
                    created_cards_id.push(create_card_day(cols[col_num], info_additional));
                    col_num += 1;
                }
                created_cards_id.push(create_card_day(cols[col_num], info));
            }
            let resizeObserver = new ResizeObserver(() => {
                created_cards_id.forEach(function (id) {
                    let card = document.getElementById(id);
                    if (!!card) {
                        let body_children = card.childNodes[1].firstChild.childNodes;
                        let text1 = body_children[1];
                        let text2 = body_children[2];
                        if (card.offsetWidth >= 560) {
                            text1.style.fontSize = "16px";
                            text2.style.fontSize = "16px";
                        } else if (card.offsetWidth < 560 && card.offsetWidth >= 390) {
                            text1.style.fontSize = "14px";
                            text2.style.fontSize = "14px";
                        } else if (card.offsetWidth < 390) {
                            text1.style.fontSize = "12px";
                            text2.style.fontSize = "10px";
                        }
                    }
                });
            });
            resizeObserver.observe($(`#${created_cards_id[0]}`)[0]);
            ["prev", "next"].forEach(function (tag) {
                let btn_day = document.getElementById(`btn-day-${tag}`);
                let clone_btn = btn_day.cloneNode(true);
                btn_day.parentNode.replaceChild(clone_btn, btn_day);
                clone_btn.addEventListener("click", function (e) {
                    let new_date = change_date_per_one(data["schedule"][0]["date"], tag);
                    get_schedule(data["student"], [new_date], "day");
                });
            });
        }
    } else if (display_type_id === "week") {
        // render for week
        // TODO: render for week
    } else if (display_type_id === "month") {
        // render for month
        // TODO: render for month
    }
}

function display_year_activity(data, student, start_year) {
    // function for adding events to "next" & "prev" buttons
    function next_prev_events(btn_name) {
        ["prev", "next"].forEach(function (tag) {
            let btn = document.getElementById(`${btn_name}-${tag}`);
            let clone_btn = btn.cloneNode(true);
            btn.parentNode.replaceChild(clone_btn, btn);
            clone_btn.addEventListener("click", function (e) {
                let k = tag === "next" ? 1 : -1;
                get_year_activity(student, Number(start_year) + k);
            });
        });
    }

    // detect errors
    let error_flag = 0;
    if (data === null)
        error_flag = 1;
    else if (data["activity"]["subjects"].length === 0)
        error_flag = 1;

    // render screens
    if (error_flag) {
        // render error screen
        disable_screens("zero_schedule");

        // add events to "next" & "prev" buttons
        next_prev_events("z-btn");
    } else {
        // render year screen
        disable_screens("schedule_year");

        // render nav info
        create_nav_student_info(student["name"], `Учебный год ${start_year} – ${Number(start_year) + 1}`);

        // add option(s) to subject select box
        let subject_select = document.getElementById("subject-select");
        subject_select.innerHTML = "";
        let subjects = data["activity"]["subjects"];
        for (let i = 0; i < subjects.length; i++) {
            let opt = document.createElement("option");
            opt.value = `${i}`;
            opt.innerHTML = `${subjects[i]["title"]} (${subjects[i]["group"]} – ${subjects[i]["semester"]} семестр, ${subjects[i]["year"]})`;
            subject_select.appendChild(opt);
        }

        // const(s) for month naming in activity table(s)
        const month_names = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ];

        // function for creating activity table
        function create_activity_table(container, sbj, month, year) {
            function days_in_month(month, year) {
                return new Date(year, month, 0).getDate();
            }

            function parse_date_str(str) {
                let [day, month, year] = str.split(/[.-]/);
                return new Date(year, month - 1, day);
            }

            function date_in_range(date, sbj) {
                let date_check = parse_date_str(date);
                let date_start = parse_date_str(sbj["dates"][0]);
                let date_end = parse_date_str(sbj["dates"][1]);
                return date_start <= date_check && date_check <= date_end;
            }

            let label = document.createElement("p");
            label.className = "activity-table-label";
            label.innerText = `${month_names[month - 1]}, ${year}`;

            let table = document.createElement("table");
            table.className = "table table-sm";
            let tbody = document.createElement("tbody");
            let tr = document.createElement("tr");

            let days = days_in_month(month, year);
            let date_today = new Date();
            for (let i = 0; i < days; i++) {
                let td = document.createElement("td");
                td.innerText = `${i + 1}`;
                td.id = `${i + 1}-${month}-${year}`;
                if (date_in_range(td.id, sbj)) {
                    td.className = "in-range";
                    let date_check = parse_date_str(td.id);
                    sbj["visits"].forEach(function (visit) {
                        let date_visit = parse_date_str(visit["date"]);
                        if (date_check.getTime() === date_visit.getTime()) {
                            if (date_check > date_today)
                                td.classList.add("unchecked");
                            else {
                                // TODO: check "visits" status
                                td.classList.add("red");
                            }
                        }
                    });
                }
                tr.appendChild(td);
            }

            container.appendChild(label);
            container.appendChild(table);
            table.appendChild(tbody);
            tbody.appendChild(tr);
        }

        // function for rendering subject activity
        function subject_activity(subject_val) {
            let container = document.getElementById("year-activity-table-container");
            container.innerHTML = "";

            let sbj = subjects[subject_val];

            let year = data["activity"]["years"][sbj["semester"] - 1];
            let month_first = Number(data["activity"]["semesters"][sbj["semester"]]["date_start"].split(".")[1]);
            let month_last = Number(data["activity"]["semesters"][sbj["semester"]]["date_end"].split(".")[1]);

            for (let month = month_first; month <= month_last; month++) {
                create_activity_table(container, sbj, month, year)
            }
        }

        // render subject activity event
        subject_select.onchange = (event) => {
            subject_activity(Number(event.target.value));
        }
        subject_activity(0);

        // add events to "next" & "prev" buttons
        next_prev_events("btn-year");
    }
}


// ----- ----- ----- ----- ----- ----- ----- ----- ----- -----


// input: "2023-10-17", output: "17.10.2023"
function reformat_date(dateStr) {
    let dArr = dateStr.split("-");
    return dArr[2] + "." + dArr[1] + "." + dArr[0];
}

//input: "17.10.2023", output: "17 Октября 2023, Вторник"
function format_date_for_nav(inputDate) {
    const months = [
        "Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
        "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"
    ];
    const weekDays = [
        "Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"
    ];
    const [day, month, year] = inputDate.split('.');
    const date = new Date(`${year}-${month}-${day}`);
    return `${day} ${months[date.getMonth()]} ${year}, ${weekDays[date.getDay()]}`;
}

function change_date_per_one(inputDate, param) {
    const parts = inputDate.split(".");
    const day = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10);
    const year = parseInt(parts[2], 10);
    const date = new Date(year, month - 1, day);
    if (param === "prev")
        date.setDate(date.getDate() - 1);
    else if (param === "next")
        date.setDate(date.getDate() + 1);
    const nextDay = date.getDate();
    const nextMonth = date.getMonth() + 1;
    const nextYear = date.getFullYear();
    return `${String(nextDay).padStart(2, '0')}.${String(nextMonth).padStart(2, '0')}.${nextYear}`;
}

function get_days_in_month(inputDate) {
    const [year, month, day] = inputDate.split("-");
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


// ----- ----- ----- ----- ----- ----- ----- ----- ----- -----


$(document).ready(function () {
    // button_search init
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
            get_schedule(student, dates, display_type_id);
        } else if (display_type_id === "week") {
            // array of dates from week
            // TODO: week widget
            dates = [];
            get_schedule(student, dates, display_type_id);
        } else if (display_type_id === "month") {
            // array of dates from month
            dates = get_days_in_month(raw_date);
            get_schedule(student, dates, display_type_id);
        } else if (display_type_id === "year") {
            // academic year activity
            let start_year = document.getElementsByName("date_year")[0].value.split("-")[0];
            if (start_year === "") {
                let today_date = new Date();
                const offset = today_date.getTimezoneOffset()
                today_date = new Date(today_date.getTime() - (offset * 60 * 1000))
                start_year = today_date.toISOString().split("T")[0].split("-")[0]
            }
            get_year_activity(student, start_year);
        }
    };
});