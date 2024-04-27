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



function get_rating(display_choice , dates , display_type_id) {
    $.ajax({
        type: "POST",
        url: "get_rating/",
        data: {
            display_choice: display_choice,
            dates : dates,
            display_type_id : display_type_id,
            csrfmiddlewaretoken: CSRF_TOKEN
        },
        success: function (data) {
            console.log(data);
            display_raiting(data, display_choice , dates , display_type_id);
        },
        error: function () {
            console.log("Ошибка при получении рейтинга");
        }
    });
}


function get_schedule_group(group, dates, display_type_id) {
    $.ajax({
        type: "POST",
        url: "get_schedule_group/",
        data: {
            group: group,
            dates: dates,
            csrfmiddlewaretoken: CSRF_TOKEN
        },
        success: function (data) {
            console.log(data); // TODO: clear console logs
            display_group_schedule(data, dates, display_type_id);
        },
        error: function () {
            console.log("get_schedule() error");
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

//Create week day
let create_card_week = (parent, info, student, flag) => {

    let card = document.createElement("th");
    card.className = flag === true ? "card_card-schedule_row" : "card_card-schedule_row empty";
    card.id = `card-${uid()}`;

    let col_activity = document.createElement("div");
    col_activity.className = "activity_bar_week";

    card.innerText = `${info.substr(0, 2)}`;
    card.appendChild(col_activity)
    parent.appendChild(card);

    if (flag)
        card.addEventListener("click", function () {
            get_schedule(student, [info], "day");
        });

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


//--------------------------------------------------------------------------


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
        if (data["schedule"].length === 0) {
            let date = required_dates[0];
            let date2 = required_dates[6];
            create_nav_student_info(data["student"]["name"], format_date_for_nav_week(date, date2));
            disable_screens("zero_schedule");
            ["prev", "next"].forEach(function (tag) {
                let btn_week = document.getElementById(`z-btn-${tag}`);
                let clone_btn = btn_week.cloneNode(true);
                btn_week.parentNode.replaceChild(clone_btn, btn_week);
                clone_btn.addEventListener("click", function (e) {
                    let new_dates = change_dates_per_week(date, tag);
                    get_schedule(data["student"], new_dates, "week");
                });
            });
        } else {
            // TODO : fix bug with dates for incomplete schedules (showcase: "181-461", "20.11.2023 - 26.11.2023")
            while (data["schedule"].length !== 7)
                data["schedule"].unshift(null);
            let date = required_dates[0];
            let date2 = required_dates[6];
            create_nav_student_info(data["student"]["name"], format_date_for_nav_week(date, date2));
            disable_screens("schedule_week");
            let row = document.getElementById("week_tr");
            row.innerHTML = "";
            let created_cards_id = [];
            let student = data["student"];
            for (let i = 0; i < data["schedule"].length; i++) {
                if (data["schedule"][i])
                    created_cards_id.push(create_card_week(row, data["schedule"][i]["date"], student, true));
                else
                    created_cards_id.push(create_card_week(row, required_dates[i], student, false));
            }
            ["prev", "next"].forEach(function (tag) {
                let btn_week = document.getElementById(`btn-week-${tag}`);
                let clone_btn = btn_week.cloneNode(true);
                btn_week.parentNode.replaceChild(clone_btn, btn_week);
                clone_btn.addEventListener("click", function (e) {
                    let new_dates = change_dates_per_week(required_dates[0], tag);
                    get_schedule(data["student"], new_dates, "week");
                });
            });
        }
    } else if (display_type_id === "month") {
        // render for month
        function next_prev_events_month(btn_name) {
            ["prev", "next"].forEach(function (tag) {
                let btn_month = document.getElementById(`${btn_name}-${tag}`);
                let clone_btn = btn_month.cloneNode(true);
                btn_month.parentNode.replaceChild(clone_btn, btn_month);
                clone_btn.addEventListener("click", function (e) {
                    let new_date = tag === "prev" ? required_dates[0] : required_dates[required_dates.length - 1];
                    new_date = change_date_per_one(new_date, tag).split(".").reverse().join("-");
                    let new_dates = get_days_in_month(new_date);
                    get_schedule(data["student"], new_dates, "month");
                });
            });
        }

        if (data["schedule"].length === 0) {
            create_nav_student_info(data["student"]["name"], format_month_for_nav(required_dates[0]));
            disable_screens("zero_schedule");
            next_prev_events_month("z-btn");
        } else {
            let dateString = data["schedule"][0]["date"];
            create_nav_student_info(data["student"]["name"], format_month_for_nav(dateString));
            disable_screens("schedule_month");

            let table = document.getElementById("monthCalendar");
            table.innerHTML = "";
            let weekdaysRow = document.createElement("tr");
            ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"].forEach(day => {
                let th = document.createElement("th");
                th.className = "weekdays";
                th.innerText = day;
                weekdaysRow.appendChild(th);
            });
            table.appendChild(weekdaysRow);

            let created_cards_id = [];
            let student = data["student"];
            let dateParts = dateString.split(".");
            let date = new Date(`${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`);
            let firstDayOfMonth = new Date(date);
            firstDayOfMonth.setDate(1);
            let startingDay = (firstDayOfMonth.getDay() + 6) % 7;
            let lastDayOfMonth = new Date(date.getFullYear(), date.getMonth() + 1, 0);
            let fullM = lastDayOfMonth.getDate();
            let daysInMonth = lastDayOfMonth.getDate() % 7 + 1;

            // Создаем первую неделю и добавляем пустые ячейки для дней предыдущего месяца
            let weekRow = document.createElement("tr");
            for (let j = 0; j < startingDay; j++) {
                let emptyCell = document.createElement("td");
                emptyCell.innerText = "";
                emptyCell.className = "card_card-schedule_row"
                weekRow.appendChild(emptyCell);
            }
            table.appendChild(weekRow);

            for (let i = 0; i < data["schedule"].length; i++) {
                let info = data["schedule"][i]["date"];
                if (weekRow.childElementCount === 7) {
                    weekRow = document.createElement("tr");
                }
                created_cards_id.push(create_card_week(weekRow, info, student, true));
                table.appendChild(weekRow);
            }

            next_prev_events_month("btn-month");
        }
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

function format_month_for_nav(inputDate) {
    const months = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ];
    const [day, month, year] = inputDate.split('.');
    const date = new Date(`${year}-${month}-${day}`);
    return `${months[date.getMonth()]} ${year}`;
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

//input: "13.11.2023", "19.11.2023" output: "13 - 19 Ноября 2023" or "27 Ноября - 3 Декабря, 2023"
function format_date_for_nav_week(inputDate, inputDate2) {
    const months = [
        "Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
        "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"
    ];
    const [day, month, year] = inputDate.split('.');
    const [day2, month2, year2] = inputDate2.split('.');
    const date = new Date(`${year}-${month}-${day}`);
    const date2 = new Date(`${year}-${month2}-${day2}`);
    if (month == month2) {
        return `${day} - ${day2} ${months[date.getMonth()]} ${year}`;
    } else {
        return `${day} ${months[date.getMonth()]} - ${day2} ${months[date2.getMonth()]} ${year}`;
    }

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

function change_dates_per_week(inputDate, param) {
    const parts = inputDate.split(".");
    const day = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10);
    const year = parseInt(parts[2], 10);
    const date = new Date(year, month - 1, day);

    // Переместить дату на начало следующей недели
    if (param === "next") {
        date.setDate(date.getDate() + (8 - date.getDay()));
    } else if (param === "prev") {
        //date.setDate(date.getDate() - date.getDay() - 1);
        date.setDate(date.getDate() - date.getDay() - 6);
    }

    const new_dates = [];
    // Создать массив дат для следующей недели
    for (let i = 0; i < 7; i++) {
        const nextDay = date.getDate();
        const nextMonth = date.getMonth() + 1;
        const nextYear = date.getFullYear();
        new_dates.push(`${String(nextDay).padStart(2, '0')}.${String(nextMonth).padStart(2, '0')}.${nextYear}`);
        date.setDate(date.getDate() + 1);
    }

    return new_dates;
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

function get_days_in_week(inputDate) {
    const inputDateFormat = new Date(inputDate);
    const inputDayOfWeek = inputDateFormat.getDay();

    const mondayOffset = inputDayOfWeek === 0 ? 6 : inputDayOfWeek - 1;
    const mondayDate = new Date(inputDateFormat);
    mondayDate.setDate(mondayDate.getDate() - mondayOffset);

    const weekDates = [];
    for (let i = 0; i < 7; i++) {
        const currentDate = new Date(mondayDate);
        currentDate.setDate(currentDate.getDate() + i);
        const formattedDate = currentDate.toLocaleDateString("ru-RU", {
            year: "numeric", month: "2-digit", day: "2-digit"
        }).replace(/\./g, "-").split("-").join(".");
        weekDates.push(formattedDate);
    }
    return weekDates;
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

function display_group_schedule(data, required_dates, display_type_id) {
    if (display_type_id === "month") {
        // render for month
        function next_prev_events_month_group(btn_name) {
            ["prev", "next"].forEach(function (tag) {
                let btn_month = document.getElementById(`${btn_name}-${tag}`);
                let clone_btn = btn_month.cloneNode(true);
                btn_month.parentNode.replaceChild(clone_btn, btn_month);
              
            });
        }

        if (data["schedule"].length === 0) {
            create_nav_group_info(data["group"]["group"], format_month_for_nav(required_dates[0]));
            disable_screens("zero_schedule");
            next_prev_events_month_group("z-btn");
        } else {
            let dateString = data["schedule"][0]["date"];
            create_nav_group_info(data["group"]["group"], format_month_for_nav(dateString));
            disable_screens("schedule_month");

            let table = document.getElementById("monthCalendar");
            table.innerHTML = "";
            let weekdaysRow = document.createElement("tr");
            ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"].forEach(day => {
                let th = document.createElement("th");
                th.className = "weekdays";
                th.innerText = day;
                weekdaysRow.appendChild(th);
            });
            table.appendChild(weekdaysRow);

            let created_cards_id = [];
            let group = data["group"]["group"];
            let dateParts = dateString.split(".");
            let date = new Date(`${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`);
            let firstDayOfMonth = new Date(date);
            firstDayOfMonth.setDate(1);
            let startingDay = (firstDayOfMonth.getDay() + 6) % 7;
            let lastDayOfMonth = new Date(date.getFullYear(), date.getMonth() + 1, 0);
            let fullM = lastDayOfMonth.getDate();
            let daysInMonth = lastDayOfMonth.getDate() % 7 + 1;

            // Создаем первую неделю и добавляем пустые ячейки для дней предыдущего месяца
            let weekRow = document.createElement("tr");
            for (let j = 0; j < startingDay; j++) {
                let emptyCell = document.createElement("td");
                emptyCell.innerText = "";
                emptyCell.className = "card_card-schedule_row"
                weekRow.appendChild(emptyCell);
            }
            table.appendChild(weekRow);

            for (let i = 0; i < data["schedule"].length; i++) {
                let info = data["schedule"][i]["date"];
                if (weekRow.childElementCount === 7) {
                    weekRow = document.createElement("tr");
                }
                created_cards_id.push(create_card_week_group(weekRow, info, group, true));
                table.appendChild(weekRow);
            }

            next_prev_events_month_group("btn-month");
        }
    }
}

//Create week day fow group
let create_card_week_group = (parent, info, group, flag) => {

    //24 11 и 5 - фейковые данные о посещаемости
    var missed = 24;
    var visited = 11;
    var late = 5;

    var backgroundColor = ['#198754', '#DC3545', '#FFC107'];

    let card = document.createElement("th");
    card.className = flag === true ? "card_card-schedule_row" : "card_card-schedule_row empty";
    card.style.cursor = 'pointer';
    card.id = `card-${uid()}`;

    let col_act_width = 102; 
    let width_for_each_student = col_act_width/40; 
    let visited_bar = width_for_each_student * visited; 
    let late_bar = width_for_each_student * late; 
    let missed_bar = width_for_each_student * missed; 

    let col_activity = document.createElement("div");
    col_activity.className = "activity_bar_week";
    col_activity.style.background = `linear-gradient(to right, ${backgroundColor[0]} 0px ${visited_bar}px,  
        ${backgroundColor[2]} ${visited_bar}px ${visited_bar+late_bar}px, 
        ${backgroundColor[1]} ${visited_bar+late_bar}px ${visited_bar+late_bar+missed_bar}px)`;

    card.innerText = `${info.substr(0, 2)}`;
    card.appendChild(col_activity);
    // card.appendChild(modal_button);
    parent.appendChild(card);

    //MODAL_WINDOW
    if (flag)
        card.addEventListener("click", function () {
            $('#myModal').modal('show');
    });

    let modaldate = info;
    document.getElementById('modal_date').innerHTML = modaldate;

    // let modalgroup = group;
    // document.getElementById('modal_group').innerHTML = modalgroup;


    var canvas = document.getElementById('doughnut-chart');
    var ctx = canvas.getContext('2d');

    var options = {
        labels: ['Студент(ов) присутствовал(о):', 'Студент(ов) отсутствовал(о):', "Студент(ов) опоздал(о):"],
        data: [visited, missed, late],
        backgroundColor: ['#198754', '#DC3545', '#FFC107']
    };
  
    var total = options.data.reduce((a, b) => a + b, 0);
    var startAngle = -Math.PI / 2;
  
    for (var i = 0; i < options.data.length; i++) {
        var sliceAngle = (options.data[i] / total) * 2 * Math.PI;
        ctx.beginPath();
        ctx.moveTo(canvas.width / 2, canvas.height / 2);
        ctx.arc(canvas.width / 2, canvas.height / 2, canvas.height / 2, startAngle, startAngle + sliceAngle);
        ctx.fillStyle = options.backgroundColor[i];
        ctx.fill();
        startAngle += sliceAngle;
    }

    document.getElementById('modal_labels').innerHTML =
    `<div style="min-height: 25px;"></div>
    <div id="circ_visited" style="display: inline-block; min-width: 25px; min-height: 25px; border-radius: 50%; background-color: ${options.backgroundColor[0]}"></div>
    <p>${options.labels[0]} ${options.data[0]}/40</p>
    <div style="min-height: 20px;"></div>
    <div id="circ_missed" style="display: inline-block; min-width: 25px; min-height: 25px; border-radius: 50%; background-color: ${options.backgroundColor[1]}"></div>
    <p>${options.labels[1]} ${options.data[1]}/40</p>
    <div style="min-height: 20px;"></div>
    <div id="circ_late" style="display: inline-block; min-width: 25px; min-height: 25px; border-radius: 50%; background-color: ${options.backgroundColor[2]}"></div>
    <p>${options.labels[2]} ${options.data[2]}/40</p>`;
    
    return card.id;
}



let create_nav_group_info = (group, date) => {
    let nav_selected_group = document.getElementById("nav-selected-student");
    nav_selected_group.innerHTML = "";

    let h5 = document.createElement("h5");
    h5.className = "fw-light m-0";
    h5.innerText = "Группа ";

    let b = document.createElement("b");
    b.innerText = `${group}`;

    let p = document.createElement("p");
    p.innerText = `${date}`;
    p.style.color = "var(--text-secondary)";
    p.style.margin = "0";

    h5.appendChild(b);
    nav_selected_group.appendChild(h5);
    nav_selected_group.appendChild(p);
}

function display_raiting(data, display_choice , dates , display_type_id){
    var currentPageSubject = 1;
    var studentsPerPageSubject = 7;
   
    if (display_choice === "student"){
        if (display_type_id === "day"){
            // Определяем параметры 
            var currentPage = 1;
            var studentsPerPage = 7; // Количество студентов на странице

            // Функция для отображения студентов на текущей странице
            function displayStudents() {
                var startIndex = (currentPage - 1) * studentsPerPage;
                var endIndex = startIndex + studentsPerPage;
                var studentsToShow = data.students.slice(startIndex, endIndex);

                $('#students-rating-list tbody').empty();
                
                studentsToShow.forEach(function(student) {
                    var barColor = 'red'; 

                    if (student.total_visited_minutes > (student.minutes * 0.5)) {
                        barColor = 'green';
                    } else if (student.total_visited_minutes >= (student.minutes * 0.3) 
                    && student.total_visited_minutes <= student.minutes * 0.5){
                        barColor = 'yellow';
                    }
                
                    var barWidth = (student.total_visited_minutes / 20000) * 100 + '%';
                
                    var barWidth = '320px'; 

                    var barHtml = `
                        <div class="progress-bar" style="width: ${barWidth}; background-color: ${barColor}; position: relative;">
                            <span class="progress-number">${student.total_visited_minutes}/${student.minutes}</span>
                        </div>
                    `;

                    $('#students-rating-list tbody').append(`
                        <tr>
                            <td>${student.name}</td>
                            <td>${student.group}</td>
                            <td>${barHtml}</td>
                            
                        </tr>
                    `);
                });
            }

            // Показываем первую страницу при загрузке
            displayStudents();

            $('#btn-stud-prev').click(function() {
                if (currentPage > 1) {
                    currentPage--;
                    displayStudents();
                }
            });
    
            $('#btn-stud-next').click(function() {
                var totalPages = Math.ceil(data.students.length / studentsPerPage);
                if (currentPage < totalPages) {
                    currentPage++;
                    displayStudents();
                }
            });
        }
    } 


    function displaySubjects(data) {
        // Создаем объект-набор для хранения уникальных предметов
        var uniqueSubjects = {};

        // Проходим по всем студентам и добавляем их предметы в набор
        data.students.forEach(function(student) {
            var subjects = Object.keys(student.subjects_count);
            // Добавляем каждый предмет в набор
            subjects.forEach(function(subject) {
                uniqueSubjects[subject] = true;
            });
        });

        // Получаем список предметов из набора
        var subjectList = Object.keys(uniqueSubjects);

        // Находим элемент <select> по его id
        var selectElement = document.getElementById("subject-rating");

        // Очищаем все текущие опции внутри <select>
        selectElement.innerHTML = "";

        // Добавляем опцию "Все предметы" в начало списка
        var allOption = document.createElement("option");
        allOption.text = "Все предметы";
        selectElement.add(allOption);

        // Добавляем каждый предмет в элемент <select> в виде опции
        subjectList.forEach(function(subject) {
            var optionElement = document.createElement("option");
            optionElement.text = subject;
            selectElement.add(optionElement);
        });

        // Обработчик события изменения выбранного предмета
        selectElement.addEventListener('change', function() {
            var selectedSubject = selectElement.value;
            if (selectedSubject === "Все предметы") {
                // Если выбрана опция "Все предметы", отображаем всех студентов
                currentPageSubject = 1;
                displayStudents();
            } else {
                // Иначе отображаем студентов только с выбранным предметом
                currentPageSubject = 1;
                displayStudentsBySubject(data, selectedSubject);
            }
        });
    }

    // Вызываем функцию отображения предметов с вашими данными
    displaySubjects(data);

    // Функция для отображения студентов с выбранным предметом
    function displayStudentsBySubject(data, subject) {
        // Функция для отображения студентов по предмету
        function renderStudents(studentsToShow) {
            var startIndex = (currentPageSubject - 1) * studentsPerPageSubject;
            var endIndex = startIndex + studentsPerPageSubject;
            var studentsToRender = studentsToShow.slice(startIndex, endIndex);
            // Очищаем тело таблицы
            $('#students-rating-list tbody').empty();

            // Проходим по всем студентам
            studentsToRender.forEach(function(student) {
                // Проверяем, есть ли у студента выбранный предмет
                if (student.subjects_count.hasOwnProperty(subject)) {
                    var studentSubjectMinutes = student.subjects_visited_minutes[subject]; // Минуты студента по выбранному предмету
                    var studentTotalMin = student.subjects_count[subject] * 90
                    var barColor = 'red';

                    if (studentSubjectMinutes > (studentTotalMin * 0.5)) {
                        barColor = 'green';
                    } else if (studentSubjectMinutes >= (studentTotalMin * 0.3) &&
                        studentSubjectMinutes <= studentTotalMin * 0.5) {
                        barColor = '#FFC107';
                    }

                    var barWidth = '320px';

                    var barHtml = `
                        <div class="progress-bar" style="width: ${barWidth}; background-color: ${barColor}; position: relative;">
                            <span class="progress-number">${studentSubjectMinutes}/${studentTotalMin}</span>
                        </div>
                    `;

                    // Вставляем строку в таблицу с именем студента, его группой и количеством минут по выбранному предмету
                    $('#students-rating-list tbody').append(`
                        <tr>
                            <td>${student.name}</td>
                            <td>${student.group}</td>
                            <td>${barHtml}</td>
                        </tr>
                    `);
                }
            });
        }

        // Показываем первую страницу при загрузке
        renderStudents(data.students);

        // Обработчики кнопок перелистывания для студентов по выбранному предмету
        $('#btn-stud-prev').click(function() {
            if (currentPageSubject > 1) {
                currentPageSubject--;
                renderStudents(data.students);
            }
        });

        $('#btn-stud-next').click(function() {
            var totalPages = Math.ceil(data.students.length / studentsPerPageSubject);
            if (currentPageSubject < totalPages) {
                currentPageSubject++;
                renderStudents(data.students);
            }
        });
    }
    
}


// ----- ----- ----- ----- ----- ----- ----- ----- ----- -----


$(document).ready(function () {
    // button_search init
    let button_search = document.getElementById("btn-search");
    let formId = $(button_search).closest('form').attr('id');

    if (formId === 'schedule-form') {
        button_search.disabled = true;
        // detecting "student" field changes & unable / disable button_search
        $(":input[name$=student]").on("change", function () {
            let selected = $(this).select2("data")[0];
            button_search.disabled = selected.id === "";
        });

        $(":input[name$=group]").on("change", function () {
            let selected_group = $(this).select2("data")[0];
            button_search.disabled = selected_group.id === "";
        });

        // detecting button_search click & processing data
        button_search.onclick = function (e) {
            // creating "student" object
            let selected_student = $(":input[name$=student]").select2("data")[0].text;
            console.log("!!"+ selected_student);
            let student;
            let group
            if (selected_student != "---------") {
                student = {
                    group: selected_student.split(")")[0].substr(1),
                    name: selected_student.split(")")[1].substr(1)
                }
                group = student["group"]
            } else {
                student = null; 
                let selected_group = $(":input[name$=group]").select2("data")[0].text;
                group = selected_group
            }
            // creating "dates" array
            let display_type_id = $(":input[name$=display_type]").select2("data")[0].id;
            let raw_date = get_raw_date(display_type_id);
            let dates = [];
            if (display_type_id === "day") {
                // array of dates from day
                dates = [reformat_date(raw_date)];
                console.log(dates);
                get_schedule(student, dates, display_type_id);
            } else if (display_type_id === "week") {
                // array of dates from week
                dates = get_days_in_week(raw_date);
                console.log(dates);
                get_schedule(student, dates, display_type_id);
            } else if (display_type_id === "month") {
                // array of dates from month
                dates = get_days_in_month(raw_date);
                console.log(dates);
                if (student==null) {
                    get_schedule_group(group, dates, display_type_id);
                } else { 
                    get_schedule(student, dates, display_type_id);
                }
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
    } else if (formId === 'rating-form') {
        button_search.onclick = function (e) { 
            let display_choice = document.querySelector("[name$='display_choices']").value;
            let display_type_id = document.querySelector("[name$='display_type']").value;
            let raw_date = get_raw_date(display_type_id);
            let dates = [];
            if (display_type_id === "day") {
                // array of dates from day
                dates = [reformat_date(raw_date)];
                console.log(dates);
                    get_rating(display_choice, dates, display_type_id)
            } else if (display_type_id === "week") {
                // array of dates from week
                dates = get_days_in_week(raw_date);
                console.log(dates);
                    get_rating(display_choice, dates, display_type_id)
            } else if (display_type_id === "month") {
                // array of dates from month
                dates = get_days_in_month(raw_date);
                console.log(dates);
                    get_rating(display_choice, dates, display_type_id)
            } 

        }
    }
   
});