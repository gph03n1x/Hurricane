var url = $(location).attr('href');


var input = document.getElementById("search");
var awesomplete = new Awesomplete(input);


$( "#search" ).on('input', function() {
    var search_input = $( "#search" ).val();
    setTimeout(make_post, 800, search_input);
    console.log("Called");
    $.post( "/suggest", { search: search_input}, function( data ) {
        console.log(data);
        awesomplete.list = data;
    },'json');

});

function make_post( search_input ) {
    if (search_input.length > 2 && search_input == $( "#search" ).val()) {
        $.post( url, { search: search_input, nohtml: "true" }, function( data ) {
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
