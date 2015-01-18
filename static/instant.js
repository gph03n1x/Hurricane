var url = $(location).attr('href');
$( "#search_string" ).on('input', function() {
    var search_input = $( "#search_string" ).val();
    if (search_input.length > 2) {
        $.post( url, { search_string: search_input, nohtml: "true" }, function( data ) {
            $( "#container" ).empty();
            $( "#container" ).append( data );
        });
    }
});