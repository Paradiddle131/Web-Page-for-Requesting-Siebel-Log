(function ($) {
    /*[ Select 2 Config ]*/
    try {
        var selectSimple = $('.js-select-simple');

        selectSimple.each(function () {
            var that = $(this);
            var selectBox = that.find('select');
            var selectDropdown = that.find('.select-dropdown');
            selectBox.select2({
                dropdownParent: selectDropdown
            });
        });
    } catch (err) {
        console.log(err);
    }
})(jQuery);

$(document).ready(function () {
    fetchTable();
});

const host_url = "http://itcisopsadmin:5005/"

function fetchTable() {
    const xhr = new XMLHttpRequest(),
        method = "GET",
        url = host_url + "get_servers";
    xhr.open(method, url, true);
    xhr.send();
    xhr.onload = function () {
        data = JSON.parse(xhr.responseText);
        var record_table = $("#record_table");
        record_table.empty();
        record_table.append("<div class=\"record_row header blue\">" +
            "<div class=\"record_cell\">" +
            "Machine" +
            "</div>" +
            "<div class=\"record_cell\">" +
            "User" +
            "</div>" +
            "<div class=\"record_cell\">" +
            "Last Updated" +
            "</div>" +
            "<div class=\"record_cell\">" +
            "Status" +
            "</div>" +
            "</div>");
        $.each(data, function (key, value) {
            record_table.append("<div class=\"record_row\">" +
                "<div class=\"record_cell\" data-title=\"Machine\">" +
                "Pro " + (key + 1) +
                "</div>" +
                "<div class=\"record_cell\" data-title=\"User\">" +
                value.last_user_name +
                "</div>" +
                "<div class=\"record_cell\" data-title=\"Last Updated\">" +
                new Date(parseInt(value.log_level_last_updated.toString().substring(0, 10) + value.log_level_last_updated.toString().substring(11, 14))).toLocaleString("tr-TR") +
                "</div>" +
                "<div class=\"record_cell\" data-title=\"Status\">" +
                (value.log_level_status === "0" ? "Closed" : "<b>Open</b>") +
                "</div>" +
                "</div>");
        })
    }
}

var status_message = $("#status_message")

async function get_request_details(FD) {
    const xhr = new XMLHttpRequest(),
        method = "POST",
        url = host_url + "get_request_details";
    xhr.open(method, url, true);
    xhr.setRequestHeader("Access-Control-Allow-Headers", "Accept");
    xhr.setRequestHeader("Access-Control-Allow-Origin", url);
    xhr.send(FD);
    xhr.onload = function () {
        data = JSON.parse(xhr.responseText);
        status_message.empty();
        status_message.append(`<p style="display: inline-block; color: #000; font-style: italic; font-weight: bold;">${data.status_message}</p>`)
    }
}

var $status = $('.status');
var processing = false;

$status.on('processing done', function (e) {
    e.preventDefault();
    e.stopPropagation();
})

function start_processing_animation(loading_ring, done) {
    console.log("starting animation...");
    if (!processing) {
        processing = true;
        done.removeClass('active');
        loading_ring.addClass('active');
    }
}

function stop_processing_animation(loading_ring, done) {
    console.log("stopping animation...");
    loading_ring.removeClass('active');
    done.addClass('active');
    processing = false;
}

function updateActiveServers(email, machine_no, log_level_last_updated, log_level_status) {
    var data = new FormData();
    data.append('machine_no', machine_no);
    // data.append('Email', email);
    data.append('log_level_last_updated', log_level_last_updated);
    data.append('log_level_status', log_level_status);
    postXHR(data, "update_servers")
}

var btn1 = document.getElementById("btn1");
var btn2 = document.getElementById("btn2");
var btn3 = document.getElementById("btn3");
var btnLogout = document.getElementById("btnLogout");
var btn_refresh = document.getElementById("btn_refresh");


function blobToFile(theBlob, fileName) {
    theBlob.lastModifiedDate = new Date();
    theBlob.name = fileName;
    return theBlob;
}

function blobToString(b) {
    var u, x;
    u = URL.createObjectURL(b);
    x = new XMLHttpRequest();
    x.open('GET', u, false);
    x.send();
    URL.revokeObjectURL(u);
    return x.responseText;
}

function postXHR(data, endpoint) {
    var http = new XMLHttpRequest();
    http.open("POST", host_url + endpoint);
    http.setRequestHeader("Access-Control-Allow-Headers", "Accept");
    http.setRequestHeader("Access-Control-Allow-Origin", host_url + endpoint);
    if (typeof data == "string") { // assumed a stringified JSON
        http.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    }
    http.send(data);
}


function checkEmptyFields() {
    if ($("#machine_no")[0].value === "not_selected") {
        alert("Please select a machine.");
        throw new Error("No machine is selected.");
    }
}


window.addEventListener("load", function () {
    const form = document.getElementById("myForm");
    let server_action = "";
    var loading_ring;
    var done;
    btn1.onclick = function (e) {
        checkEmptyFields();
        server_action = "open_log";
        loading_ring = $('#loading_ring_1')
        done = $('#done_1')
    }

    btn2.onclick = function (e) {
        checkEmptyFields();
        server_action = "close_log";
        loading_ring = $('#loading_ring_2')
        done = $('#done_2')
    }

    btn3.onclick = function (e) {
        checkEmptyFields();
        if ($("#keyword")[0].value === "") {
            alert("Please enter a keyword.");
            throw new Error("No keyword is given.");
        }
        server_action = "request_log";
        loading_ring = $('#loading_ring_3')
        done = $('#done_3')
    }

    btnLogout.onclick = () => {
        window.location.href = "logout";
    }

    btn_refresh.onclick = function (e) {
        fetchTable();
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        sendData();
    });

    function sendData() {
        const XHR = new XMLHttpRequest();
        const FD = new FormData(form);
        XHR.addEventListener("load", function (event) {
            stop_processing_animation(loading_ring, done);
            console.log(this.response);
            console.log(this.response.type);
            if (this.response.type === "application/x-zip-compressed") {
                var keyword = document.getElementsByClassName("input--style-1")[0].value;
                const blob = new Blob([this.response], { type: 'application/x-zip-compressed' });
                var myFile = blobToFile(blob, keyword + ".zip");
                let a = document.createElement("a");
                a.style = "display: none";
                document.body.appendChild(a);
                let url = window.URL.createObjectURL(myFile);
                a.href = url;
                a.download = keyword + '.zip';
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                status_message.empty();
                status_message.append(`<p style="display: inline-block; color: #000; font-style: italic; font-weight: bold;">Download process completed.</p>`)
            } else if (this.response.type === "application/json") {
                var response = blobToString(this.response);
                var response_message = JSON.parse(response);
                console.log(response_message)
                var timestamp = Date.now().toString();
                if (response_message === "Log level increased.") {
                    updateActiveServers("-", $("#machine_no option:selected").val(), timestamp.substring(0, 10) + "." + timestamp.substring(10) + "000", "5");
                    fetchTable();
                    alert("Log level increased.");
                } else if (response_message === "Log level decreased.") {
                    updateActiveServers("-", $("#machine_no option:selected").val(), timestamp.substring(0, 10) + "." + timestamp.substring(10) + "000", "0");
                    fetchTable();
                    alert("Log level decreased.");
                } else if (response_message === "Success!") {
                    console.log("Success!");
                } else if (response_message === "Couldn't find any files.") {
                    alert("Couldn't find any log containing the given keyword. Please try another keyword.");
                } else if (response_message === "Error changing the log level.") {
                    alert("Error changing the log level. Please contact the administrator.");
                } else {
                    alert("Something bad happened.");
                }
            }
        });
        FD.append("isAdm", $("#isTest").is(":checked"));
        FD.set("component", $('#component').find('option:selected').text());
        if (server_action === "request_log") { get_request_details(FD); }
        XHR.open("POST", host_url + server_action);
        XHR.setRequestHeader("Access-Control-Allow-Headers", "Accept");
        XHR.setRequestHeader("Access-Control-Allow-Origin", host_url + server_action);
        XHR.responseType = 'blob';
        start_processing_animation(loading_ring, done);
        XHR.send(FD);
        server_action = "";
    }
});