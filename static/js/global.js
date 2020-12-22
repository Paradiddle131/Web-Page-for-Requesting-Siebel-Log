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
    }})(jQuery);


var btn1 = document.getElementById("btn1");
var btn2 = document.getElementById("btn2");
var btn3 = document.getElementById("btn3");
var server_name = "";

function str2bytes(str) {
    var bytes = new Uint8Array(str.length);
    for (var i = 0; i < str.length; i++) {
        bytes[i] = str.charCodeAt(i);
    }
    return bytes;
}

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
                if (responseJSON["response_message"].match("Log level increased.")) {
                    alert("Log level increased.");
                } else if (responseJSON["response_message"].match("Log level decreased.")) {
                    alert("Log level decreased.");
                } else if (responseJSON["response_message"].match("Success!")) {
                    console.log("Success.");
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


//Reference: https://jsfiddle.net/fwv18zo1/
var $machine_no = $('#machine_no'),
    $server_name = $('#server_name'),
    $options = $server_name.find('option');

$machine_no.on('change', function () {
    $server_name.html($options.filter('[value="' + this.value + '"]'));
    server_name = $server_name.find('option:selected').text();
}).trigger('change');


$server_name.on('change', function () {
    server_name = $(this).find('option:selected').text();
});