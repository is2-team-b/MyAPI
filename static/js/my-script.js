$(document).ready(function() {
    $('#postConfig').off('submit').on('submit', function(event) {
		event.stopPropagation();
		var direccion = $(this).attr('action');
		var method = $(this).attr('method');
		var formData = $(this).serializeArray();
		// process the form
		$.ajax({
			type : method, // define the type of HTTP verb we want to use (POST
			// for our form)
			url : direccion, // the url where we want to POST
			data : formData, // our data object
			// what type of data do we expect back from the server
			success : function(data) {
				$('#divForm').html(data);
				$('#divForm').slideDown(1000);
			}
		})
		// stop the form from submitting the normal way and refreshing the page
		event.preventDefault();
	});
}