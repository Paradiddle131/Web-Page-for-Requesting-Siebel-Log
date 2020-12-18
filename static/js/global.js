// var cors = require('cors')
// app.use(cors())

var server_name = "";

(function ($) {
    'use strict';
    /*==================================================================
        [ Daterangepicker ]*/
    try {
        $('.js-datepicker').daterangepicker({
            "singleDatePicker": true,
            "showDropdowns": true,
            "autoUpdateInput": false,
            locale: {
                format: 'DD/MM/YYYY'
            },
        });
    
        var myCalendar = $('.js-datepicker');
        var isClick = 0;
    
        $(window).on('click',function(){
            isClick = 0;
        });
    
        $(myCalendar).on('apply.daterangepicker',function(ev, picker){
            isClick = 0;
            $(this).val(picker.startDate.format('DD/MM/YYYY'));
    
        });
    
        $('.js-btn-calendar').on('click',function(e){
            e.stopPropagation();
    
            if(isClick === 1) isClick = 0;
            else if(isClick === 0) isClick = 1;
    
            if (isClick === 1) {
                myCalendar.focus();
            }
        });
    
        $(myCalendar).on('click',function(e){
            e.stopPropagation();
            isClick = 1;
        });
    
        $('.daterangepicker').on('click',function(e){
            e.stopPropagation();
        });
    
    
    } catch(er) {console.log(er);}
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
    

})(jQuery);




// Since there can be multiple elements with the class "popup-trigger", it returns an array. Putting the [0] will call the first button with the class "popup-trigger".
var btn1 = document.getElementById("btn1");
var btn2 = document.getElementById("btn2");
var btn3 = document.getElementById("btn3");
// If you wanted to check clicks on ALL buttons with the class, remove the [0] at the end.


function str2bytes (str) {
   var bytes = new Uint8Array(str.length);
   for (var i=0; i<str.length; i++) {
      bytes[i] = str.charCodeAt(i);
    }
    return bytes;
}


window.addEventListener( "load", function () {
    // Access the form element...
    const form = document.getElementById( "myForm" );
	//var action;
	let action;
    
		//var action;
		btn1.onclick = function(e) {
			action = "OPEN_LOG";
		}

		btn2.onclick = function(e) {
			action = "CLOSE_LOG";
		}

		btn3.onclick = function(e) {
			action = "REQUEST_LOG";
		}
	  
    // ...and take over its submit event.
    form.addEventListener( "submit", function ( event ) {
      event.preventDefault();
  
      sendData();
    });
    function sendData() {
		const XHR = new XMLHttpRequest();
		// Bind the FormData object and the form element
		const FD = new FormData( form );
      // Define what happens on successful data submission
      /*XHR.addEventListener( "load", function(event) {
        alert( event.target.responseText );
      } );*/
	

	  //XHR.onload = function(e) {
	  XHR.addEventListener( "load", function(event) {
      if (this.status == 200 && !this.response.match("Log level increased.") && !this.response.match("Log level decreased.")) {
		const blob = new Blob([str2bytes(this.response)], {type: 'image/pdf'});
		//const file = new File([blob], 'myLog.zip', {type: 'application/zip'});
		//this.handleUpload(file); // Sends POST request with received file
		  //window.URL.revokeObjectURL(window.URL.createObjectURL(blob))
		  
          // Create a new Blob object using the response data of the onload object
          //var blob = new Blob([str2bytes(XHR.response)], {type: 'application/rar'});
		  //var fileName = 'myLog.rar';
          //Create a link element, hide it, direct it towards the blob, and then 'click' it programatically
          let a = document.createElement("a");
          a.style = "display: none";
          document.body.appendChild(a);
          //Create a DOMString representing the blob and point the link element towards it
          let url = window.URL.createObjectURL(blob);
          a.href = url;
          a.download = 'myLog.log';
          //programatically click the link to trigger the download
          a.click();
          //release the reference to the file by revoking the Object URL
          window.URL.revokeObjectURL(url);
		  a.remove();
	  }else if (this.response.match("Log level increased.")) {
		  alert("Log level increased.");
	  }else if (this.response.match("Log level decreased.")) {
		  alert("Log level decreased.");
      }else if (this.response.match("Success!")) {
		  console.log("Success.");
	  }else{
		  alert("Something bad happened.");
      }
	});
  
      // Define what happens in case of error
    //   XHR.addEventListener( "error", function( event ) {
    //     alert( 'Oops! Something went wrong!' );
    //   } );
  
      // Set up our request
    //   XHR.open( "POST", "http://localhost:5003/request_log" );
      XHR.open( "POST", "http://172.24.84.34:5003/request_log" );
	  
  
      // The data sent is what the user provided in the form
      XHR.setRequestHeader("Access-Control-Allow-Headers", "Accept");
      XHR.setRequestHeader("Access-Control-Allow-Origin", "http://172.24.84.34:5003/request_log");
	  //XHR.responseType='blob';
      //XHR.setRequestHeader("Content-Type", "multipart/form-data")
	  FD.append("Action", action);
	  FD.set("server_name", server_name);
      XHR.send( FD );
    }
  });
 

//Reference: https://jsfiddle.net/fwv18zo1/
var $machine_no = $( '#machine_no' ),
$server_name = $( '#server_name' ),
$options = $server_name.find( 'option' );

$machine_no.on( 'change', function() {
	$server_name.html( $options.filter( '[value="' + this.value + '"]' ) );
	server_name = $server_name.find('option:selected').text();
} ).trigger( 'change' );


$server_name.on( 'change', function() {
	server_name = $(this).find('option:selected').text();
});







