var url = $(location).attr('href');


var input = document.getElementById("search_string");
var awesomplete = new Awesomplete(input);


$( "#search_string" ).on('input', function() {
    var search_input = $( "#search_string" ).val();
    setTimeout(make_post, 800, search_input);
    console.log("Called");
    $.post( "/suggest", { search_string: search_input}, function( data ) {
        awesomplete.list = data;
    },'json');

});

function make_post( search_input ) {
    if (search_input.length > 2 && search_input == $( "#search_string" ).val()) {
        $.post( url, { search_string: search_input, nohtml: "true" }, function( data ) {
            data = data.split("\n");
            $( "#qTime").empty();
            $( "#qTime").append(data[0]);
            data.splice(0,1);
            data = data.join("\n");
            $( "#container" ).empty();
            $( "#container" ).append( data );
        });
    }
}
