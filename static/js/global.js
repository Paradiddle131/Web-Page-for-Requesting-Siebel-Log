(function ($) {
    /*[ Select 2 Config ]
        ===========================================================*/
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
    fetchTable();
})(jQuery);

var $status = $('.status');
var $loading_ring = $('.loading_ring');
var $done = $('.done');
var processing = false;

$status.on('processing done', function(e) {
    e.preventDefault();
    e.stopPropagation();
})

function start_processing_animation() {
    console.log("starting animation...");
    if (!processing) {
        processing = true;
        // $button.html('Uploading...');
        // $status.fadeOut();
        $done.removeClass('active');
        $loading_ring.addClass('active');
    }
}

function stop_processing_animation() {
    console.log("stopping animation...");
    $loading_ring.removeClass('active');
    $done.addClass('active');
    processing = false;
}

function fetchTable(doPush=false){
    var loadUrl = "static/data/active_servers.json";
    $("#record_table").empty();
    $.getJSON(loadUrl, function(data){ 
        $("#record_table").append("<div class=\"record_row header blue\">" +
            "<div class=\"record_cell\">" +
                "Machine" +
            "</div>" +
            "<div class=\"record_cell\">" +
                "Email" +
            "</div>" +
            "<div class=\"record_cell\">" +
                "Date Activated" +
            "</div>" +
            "<div class=\"record_cell\">" +
                "Status" +
            "</div>" +
        "</div>");
        $.each(data, function (key, value) { 
            updateActiveServers(value.Email, key, value.Date_activated, value.Status, doPush);
        });
    });
}

var btn1 = document.getElementById("btn1");
var btn2 = document.getElementById("btn2");
var btn3 = document.getElementById("btn3");
var btn_reload = document.getElementById("btn_reload");


function blobToFile(theBlob, fileName){
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

function postXHR(data) {
    var http = new XMLHttpRequest();
    http.open("POST", "http://itcisopsadmin:5005/request_log");
    http.setRequestHeader("Access-Control-Allow-Headers", "Accept");
    http.setRequestHeader("Access-Control-Allow-Origin", "http://itcisopsadmin:5005/request_log");
    if (typeof data == "string") { // assumed a stringified JSON
        http.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    }
    http.send(data);
}


function updateActiveServers(email, machine, date, status, doPush) {
    if (doPush) {
        var data = new FormData();
        data.append('Machine', machine);
        data.append('Email', email);
        data.append('Date_activated', date);
        data.append('Status', status);
        postXHR(data)
    } else {
        $("#record_table").append("<div class=\"record_row\">" + 
            "<div class=\"record_cell\" data-title=\"Machine\">" + 
                machine + 
            "</div>" + 
            "<div class=\"record_cell\" data-title=\"Email\">" + 
                email + 
            "</div>" + 
            "<div class=\"record_cell\" data-title=\"Date Activated\">" + 
                date + 
            "</div>" + 
            "<div class=\"record_cell\" data-title=\"Status\">" + 
                status + 
            "</div>" + 
            "</div>");
    }
}

function getTime() {
    var date_log = new Date().toString();
    return date_log.substring(0, date_log.length-21);
}


window.addEventListener("load", function () {
    const form = document.getElementById("myForm");
    let server_action;
    let missing_value;
    var date_log;
    btn1.onclick = function (e) {
        server_action = "OPEN_LOG";
        date_log = getTime();
    }

    btn2.onclick = function (e) {
        server_action = "CLOSE_LOG";
        date_log = getTime();
    }

    btn3.onclick = function (e) {
        if ($("#machine_no")[0].value === "not_selected") {
            missing_value = true;
            alert("Please select a machine.");
            throw new Error("No machine is selected.");
        } else if ($("#keyword")[0].value === "") {
            missing_value = true;
            alert("Please enter a keyword.");
            throw new Error("No keyword is given.");
        }
        server_action = "REQUEST_LOG";
        date_log = getTime();
    }

    btn_reload.onclick = function (e) {
        location.reload(true);
        // fetchTable(false);
        // console.log("Table Reloaded.");
    }

    form.addEventListener("submit", function (event) {
        // console.log(missing_value);
        // console.log(missing_value != null);
        // if (missing_value != null) {
        //     throw new Error("There is missing value in the form.");
        // }
        event.preventDefault();
        sendData();
    });
    function sendData() {
        const XHR = new XMLHttpRequest();
        const FD = new FormData(form);
        XHR.addEventListener("load", function (event) {
            stop_processing_animation();
            console.log(this.response);
            console.log(this.response.type);
            if (this.response.type === "application/x-zip-compressed"){
                var keyword = document.getElementsByClassName("input--style-1")[0].value;
                const blob = new Blob([this.response], { type: 'application/x-zip-compressed' });
                var myFile = blobToFile(blob, keyword+".zip");
                let a = document.createElement("a");
                a.style = "display: none";
                document.body.appendChild(a);
                let url = window.URL.createObjectURL(myFile);
                a.href = url;
                a.download = keyword+'.zip';
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                logActions("LOG_USER_ACTIVITY", "Request");
            } else if (this.response.type === "application/json"){ 
                var response = blobToString(this.response);
                var responseJSON = JSON.parse(response);
                var response_message = responseJSON["response_message"]
                if (response_message === "Log level increased.") {
                    updateActiveServers("NewAddedEmail@vodafone.com", $("#machine_no option:selected").text(), date_log, "Active", true);
                    fetchTable(false);
                    alert("Log level increased.");
                    logActions("LOG_USER_ACTIVITY", "Increase");
                } else if (response_message === "Log level decreased.") {
                    updateActiveServers("-", $("#machine_no option:selected").text(), "-", "Not Active", true);
                    fetchTable(false);
                    alert("Log level decreased.");
                    logActions("LOG_USER_ACTIVITY", "Decrease");
                } else if (response_message === "Success!") {
                    console.log("Success!");
                } else {
                    alert("Something bad happened.");
            }
        }
    });
        XHR.open("POST", "http://itcisopsadmin:5005/request_log");
        XHR.setRequestHeader("Access-Control-Allow-Headers", "Accept");
        XHR.setRequestHeader("Access-Control-Allow-Origin", "http://itcisopsadmin:5005/request_log");
        XHR.responseType='blob';
        FD.append("Server_action", server_action);
        FD.set("component", $('#component').find('option:selected').text());
        start_processing_animation();
        XHR.send(FD);
    }
    function logActions(server_action, user_action) {
        var data = {
            "Server_action": server_action,
            "Email": "emailToBeFetched@vodafone.com",
            "Machine": $("#machine_no option:selected").text(),
            "Date_activated": date_log,
            "User_action": user_action
        };
        data = JSON.stringify(data);
        postXHR(data);
    }
});

//Reference: https://jsfiddle.net/fwv18zo1/
// var $machine_no = $('#machine_no'),
//     $component = $('#component'),
//     $options = $component.find('option');

// $machine_no.on('change', function () {
//     $component.html($options.filter('[value="' + this.value + '"]'));
//     component = $component.find('option:selected').text();
// }).trigger('change');


// $component.on('change', function () {
//     component = $(this).find('option:selected').text();
// });