
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
			console.log(data);
			$.ajax({
				   url: ADD_TO_FINAL,
				   type: "POST",
				   data: encodeURIComponent(JSON.stringify(data)),
				   success: function(resp){
					   var result = resp.result;
						if (result[0]) {
								custom_alert(result[1], 'success');
								location.href = DETAIL + method_get_str;
							} else {
								custom_alert(result[1], 'error');
							}
				      }
			   });
		}
	});
});

function control_add_to_final_button() {
	var is_enable = true;
	$( ".analyze-enable-checkbox" ).each(function( index ) {
		var checked = $(this).prop('checked');
		if (! checked) {
			is_enable = false;
		}
	});
	if (is_enable) {
		$('#add_final').attr('disabled', false);
	} else {
		$('#add_final').attr('disabled', true);
	}
}
control_add_to_final_button();
$(document).ready(function () {
	$('.analyze-enable-checkbox').click(function(event) {
		control_add_to_final_button();
	});
});