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
    /*LOAD JSON DATA*/
    $.getJSON("static/data/active_servers.json", function (data) { 
        $.each(data, function (key, value) { 
            addOpenMachine(value.Email, value.Machine, value.Date_activated, value.Status, false);
        }); 
    }); 
})(jQuery);


var btn1 = document.getElementById("btn1");
var btn2 = document.getElementById("btn2");
var btn3 = document.getElementById("btn3");
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

function addOpenMachine(email, machine, date, status, doPush) {
    $(".record_table").append("<div class=\"record_row\">" + 
        "<div class=\"record_cell\" data-title=\"Email\">" + 
            email + 
        "</div>" + 
        "<div class=\"record_cell\" data-title=\"Machine\">" + 
            machine + 
        "</div>" + 
        "<div class=\"record_cell\" data-title=\"Date Activated\">" + 
            date + 
        "</div>" + 
        "<div class=\"record_cell\" data-title=\"Status\">" + 
            status + 
        "</div>" + 
        "</div>");
    if (doPush) {
        $.getJSON("static/data/active_servers.json", function (data) {
            data.push({
                "Email": email,
                "Machine": machine,
                "Date_activated": date,
                "Status": status
            });
        }); 
        // XHR SEND POST REQUEST
        var http = new XMLHttpRequest();
        var data = new FormData();
        data.append('Email', email);
        data.append('Machine', machine);
        data.append('Date_activated', date);
        data.append('Status', status);
        http.open("POST", "http://172.24.84.34:5004/request_log");
        http.setRequestHeader("Access-Control-Allow-Headers", "Accept");
        http.setRequestHeader("Access-Control-Allow-Origin", "http://172.24.84.34:5004/request_log");
        http.send(data);
    }
}


window.addEventListener("load", function () {
    const form = document.getElementById("myForm");
    let action;
    btn1.onclick = function (e) {
        console.log("open onclick");
        action = "OPEN_LOG";
    }

    btn2.onclick = function (e) {
        console.log("close onclick");
        action = "CLOSE_LOG";
    }

    btn3.onclick = function (e) {
        action = "REQUEST_LOG";
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        sendData();
    });
    function sendData() {
        const XHR = new XMLHttpRequest();
        const FD = new FormData(form);
        XHR.addEventListener("load", function (event) {
            console.log(action);
            if (action = "OPEN_LOG"){
                console.log("open");
                // $("#btn1").attr("disabled", true);
                // $("#btn2").attr("disabled", false);
            } else if (action = "CLOSE_LOG"){
                console.log("close");
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
                console.log(responseJSON);
                if (responseJSON["response_message"].match("Log level increased.")) {
                    addOpenMachine("NewAddedEmail@vodafone.com", $("#machine_no option:selected").text(), new Date(), "Active", true);
                    alert("Log level increased.");
                } else if (responseJSON["response_message"].match("Log level decreased.")) {
                    alert("Log level decreased.");
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
        FD.append("Action", action);
        FD.set("server_name", server_name);
        XHR.send(FD);
    }
});


$('#btnToggleTable').click(function(){
    $(this).find('span').text(function(_, value){return value=='-'?'+':'-'});
    $(this).nextUntil('div.row').slideToggle(100, function(){
    });
 });