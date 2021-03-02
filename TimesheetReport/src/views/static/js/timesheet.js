$(function(){
    $('#list_sheet').multiSelect()
});

$(document).ready( function () {
	load_datatable('#timesheet_table');
});

function load_timesheet_report() {
	var data = get_form_submit('#timesheet_form');
	var sheet_ids = get_value_from_multiple_select();
	var get_method = '';
	if (sheet_ids.length == 0) {
		custom_alert('No sheet name selected', 'error');
		return null;
	} 
	for (var idx = 0; idx < sheet_ids.length; idx++) {
		get_method = get_method + '&' + SESSION_SHEETS + '=' + sheet_ids[idx];
	}
	
	
	var from_date 	= data['from_date'];
	var to_date 	= data['to_date'];
	var filter 		= data['task_filter'];
	
	if (to_date == '' || from_date == '') {
		custom_alert('Missing date', 'error');
		return null;
	}
	
	get_method = get_method + '&' + SESSION_FROM + '=' + from_date;
	get_method = get_method + '&' + SESSION_TO + '=' + to_date;
	get_method = get_method + '&' + SESSION_FILTER + '=' + filter;
	location.href = 'timesheet?' + get_method;
	
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
	$('#get_newest_data').click(function(event) {
		event.preventDefault();
	});
});

$(document).ready(function () {
	$('#analyze').click(function(event) {
		event.preventDefault();
	});
});

$(document).ready(function () {
	$('#export').click(function(event) {
		event.preventDefault();
	});
});
