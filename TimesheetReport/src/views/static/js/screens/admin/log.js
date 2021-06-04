

$(document).ready( function () {
	load_datatable('#log_table');
});

function colect_config() {
	var data = get_form_submit('#log_form');
	var action1 = get_value_from_multiple_select('action');
	if (action1.length == 0) {
		custom_alert('No action selected', 'error');
		return null;
	} 
	var action2 = [];
	for (var idx = 0; idx < action1.length; idx++) {
		if (action1[idx] == 'all') {
			continue;
		}
		action2.push(action1[idx]);
	}

	var from_date 	= data['from_date'];
	var to_date 	= data['to_date'];
	if (to_date == '' || from_date == '') {
		custom_alert('Missing date', 'error');
		return null;
	}
	let out = {};
	out[SESSION_FROM] = from_date;
	out[SESSION_TO] = to_date;
	out[SESSION_ACTIONS] = action2;

	return out;
}

function load_log_table() {
	var data = colect_config();
	if (data) {
		var method_get_url = encodeURIComponent(JSON.stringify(data));
		location.href = LOG + '?' + method_get_url;
	}
}

$(document).ready(function () {
	$('#load').click(function(event) {
		load_log_table();
	});
	
});



