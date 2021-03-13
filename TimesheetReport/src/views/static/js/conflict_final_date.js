$(document).ready(function () {
	$('#add_final').click(function(event) {
		
		var url_info = parse_url();
		var method_get_str = url_info[0];
		var data = url_info[1];
		var from_date = data[SESSION_FROM];
		var to_date = data[SESSION_TO];
		if (! confirm("Are you sure you want to mark final task from " + from_date + " to " + to_date + "?")) {
			return null;
		} else {
			$('#overlay_loader').show();
			$.ajax({
				   url: '/add_to_final',
				   type: "POST",
				   data: encodeURIComponent(JSON.stringify(data)),
				   success: function(resp){
					   var result = resp.result;
						if (result[0]) {
								custom_alert(result[1], 'success');
								location.href = 'resource_timesheet' + method_get_str;
							} else {
								custom_alert(result[1], 'error');
							}
				      }
			   });
		}
		
		
	});
});