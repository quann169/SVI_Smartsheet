
$(document).ready( function () {
	load_datatable('#timesheet_table');
});

function colect_config_date() {
	var data = get_form_submit('#timesheet_form');
	var sheet_ids = get_value_from_multiple_select();
	var method_get_url = '';
	if (sheet_ids.length == 0) {
		custom_alert('No sheet name selected', 'error');
		return null;
	} 
	var ids = []
	for (var idx = 0; idx < sheet_ids.length; idx++) {
		method_get_url = method_get_url + '&' + SESSION_SHEETS + '=' + sheet_ids[idx];
		ids.push(sheet_ids[idx]);
	}
	
	
	var from_date 	= data['from_date'];
	var to_date 	= data['to_date'];
	var filter 		= data['task_filter'];
	
	if (to_date == '' || from_date == '') {
		custom_alert('Missing date', 'error');
		return null;
	}
	data[SESSION_FROM] = from_date;
	data[SESSION_TO] = to_date;
	data[SESSION_FILTER] = filter;
	data[SESSION_SHEETS] = ids;
	
	method_get_url = method_get_url + '&' + SESSION_FROM + '=' + from_date;
	method_get_url = method_get_url + '&' + SESSION_TO + '=' + to_date;
	method_get_url = method_get_url + '&' + SESSION_FILTER + '=' + filter;
	return [data, method_get_url];
}


function load_timesheet_report() {
	var result = colect_config_date();
	if (result) {
		var data = result[0];
		var method_get_url = result[1];
		location.href = 'daily_timesheet?' + method_get_url;
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
	$('#get_newest_data').click(function(event) {
		$('#overlay_loader').show();
		var result = colect_config_date();
		var data = result[0];
		var method_get_url = result[1];
		$.ajax({
			   url: '/get_newest_data',
			   type: "POST",
			   data: encodeURIComponent(JSON.stringify(data)),
			   success: function(resp){
				   var result = resp.result;
					if (result[0]) {
							custom_alert(result[1], 'success');
						} else {
							custom_alert(result[1], 'error');
						}
			      }
		   });
	});
});

$(document).ready(function () {
	$('#analyze').click(function(event) {
		var result = colect_config_date();
		if (result) {
			var data = result[0];
			var method_get_url = result[1];
			location.href = 'resource_timesheet?' + method_get_url;
		}
	});
});

$(document).ready(function () {
	$('#export').click(function(event) {
		
	});
});
