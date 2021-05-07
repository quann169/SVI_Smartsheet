
$(document).ready( function () {
	load_datatable('#timesheet_table');
});


function load_timesheet_report() {
	var data = colect_config_date();
	if (data) {
		var method_get_url = encodeURIComponent(JSON.stringify(data));
		location.href = DETAIL + '?' + method_get_url;
	}
}

$(document).ready(function () {
	$('#load').click(function(event) {
		load_timesheet_report();
	});
	$('#task_filter').change(function(event) {
		load_timesheet_report();
	});
	
});



$(document).ready(function () {
	$('#analyze').click(function(event) {
		var data = colect_config_date();
		if (data) {
			data[SESSION_TASK_FILTER] = 'current';
			var method_get_url = encodeURIComponent(JSON.stringify(data));
			location.href = ANALYZE + '?' + method_get_url;
		}
	});
});
