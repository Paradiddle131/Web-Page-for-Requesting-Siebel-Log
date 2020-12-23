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
var server_name = "";


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
    http.open("POST", "http://172.24.84.34:5004/request_log");
    http.setRequestHeader("Access-Control-Allow-Headers", "Accept");
    http.setRequestHeader("Access-Control-Allow-Origin", "http://172.24.84.34:5004/request_log");
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


window.addEventListener("load", function () {
    const form = document.getElementById("myForm");
    let server_action;
    var date_log = new Date().toString();
    date_log = date_log.substring(0, date_log.length-21);
    btn1.onclick = function (e) {
        server_action = "OPEN_LOG";
    }

    btn2.onclick = function (e) {
        server_action = "CLOSE_LOG";
    }

    btn3.onclick = function (e) {
        server_action = "REQUEST_LOG";
    }

    btn_reload.onclick = function (e) {
        location.reload(true);
        // fetchTable(false);
        // console.log("Table Reloaded.");
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        sendData();
    });
    function sendData() {
        const XHR = new XMLHttpRequest();
        const FD = new FormData(form);
        XHR.addEventListener("load", function (event) {
            if (server_action = "OPEN_LOG"){
                // $("#btn1").attr("disabled", true);
                // $("#btn2").attr("disabled", false);
            } else if (server_action = "CLOSE_LOG"){
                // $("#btn1").attr("disabled", false);
                // $("#btn2").attr("disabled", true);
            }
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
            } else if (this.response.type === "application/json"){ 
                var response = blobToString(this.response);
                var responseJSON = JSON.parse(response);
                if (responseJSON["response_message"].match("Log level increased.")) {
                    updateActiveServers("NewAddedEmail@vodafone.com", $("#machine_no option:selected").text(), date_log, "Active", true);
                    fetchTable(false);
                    alert("Log level increased.");
                    logActions("LOG_USER_ACTIVITY", "Increase");
                } else if (responseJSON["response_message"].match("Log level decreased.")) {
                    updateActiveServers("-", $("#machine_no option:selected").text(), "-", "Not Active", true);
                    fetchTable(false);
                    alert("Log level decreased.");
                    logActions("LOG_USER_ACTIVITY", "Decrease");
                } else if (responseJSON["response_message"].match("Success!")) {
                    console.log("Success!");
                } else {
                    alert("Something bad happened.");
            }
        }});
        XHR.open("POST", "http://172.24.84.34:5004/request_log");
        XHR.setRequestHeader("Access-Control-Allow-Headers", "Accept");
        XHR.setRequestHeader("Access-Control-Allow-Origin", "http://172.24.84.34:5004/request_log");
        XHR.responseType='blob';
        FD.append("Server_action", server_action);
        FD.set("server_name", server_name);
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