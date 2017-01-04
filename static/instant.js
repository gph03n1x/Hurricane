var url = $(location).attr('href');
$( "#search_string" ).on('input', function() {
    var search_input = $( "#search_string" ).val();
    setTimeout(make_post, 800, search_input);

    $.post( "/suggest", { search_string: search_input}, function( data ) {
        $( "#autocomplete" ).empty();
        $( "#autocomplete" ).append( data );
    });

});

function a_onClick( data ) {
   $( "#search_string" ).val( data );
   make_post( data );
}

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
