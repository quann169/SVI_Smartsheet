

$(document).ready( function () {
	load_datatable('#project_timesheet', false);
});

function load_timesheet_report() {
	var data = colect_config_date();
	if (data) {
		var method_get_url = encodeURIComponent(JSON.stringify(data));
		location.href = PROJECT_TIMESHEET + '?' + method_get_url;
	}
}

$(document).ready(function () {
	$('#load').click(function(event) {
		load_timesheet_report();
	});
	$('#task_filter').change(function(event) {
		load_timesheet_report();
	});
	$('#filter').change(function(event) {
		load_timesheet_report();
	});
});




