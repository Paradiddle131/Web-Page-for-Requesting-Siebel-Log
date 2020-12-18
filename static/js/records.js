$("#submit-button").on("click", function(){
    if ($(".table tbody").length == 0) {
        $(".table").append("<tbody></tbody>");
    }
    $(".table").append("<div class=\"row\">" + 
    "<div class=\"cell\" data-title=\"Username\">" + 
        "X" + 
    "</div>" + 
    "<div class=\"cell\" data-title=\"Email\">" + 
        "Y@hotmail.com" + 
    "</div>" + 
    "<div class=\"cell\" data-title=\"Password\">" + 
        "*******" + 
    "</div>" + 
    "<div class=\"cell\" data-title=\"Active\">" + 
        "YES" + 
    "</div>" + 
    "</div>");
});

$('#btnToggleTable').click(function(){
    $(this).find('span').text(function(_, value){return value=='-'?'+':'-'});
    $(this).nextUntil('div.row').slideToggle(100, function(){
    });
 });