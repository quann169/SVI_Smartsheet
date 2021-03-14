
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
		if (sheet_ids[idx] == 'all') {
			continue;
		}
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
		
		var result = colect_config_date();
		var data = result[0];
		var method_get_url = result[1];
		if (! confirm("This process will take about 1-5 minutes. Do you want to continue?")) {
			return null;
		}
		var cnt = "<div id='get_newest_data_console'><div class='cnt1'><div align='center' class='b-bottom '><b>Console</b><a class='close-p' onclick='" + '$("#overlay").hide();' + "'><i class='fas fa-times '></i></a></div><div class='cnt2'></div></div></div>";
		$('#overlay').html(cnt);
		$('#overlay').show();
		INTERVAL_GET_DATA = setInterval(function() {show_log_get_newest_data(); }, 2000);
		$.ajax({
			   url: '/get_newest_data',
			   type: "POST",
			   data: encodeURIComponent(JSON.stringify(data)),
			   success: function(resp){
				   var result = resp.result;
					clearInterval(INTERVAL_GET_DATA);
					INTERVAL_GET_DATA = null;
					$('#get_newest_data_console .close-p').show();

			      }
		   });
	});
});

function show_log_get_newest_data() {
		var data = {};
	    $.ajax({
	        url: "/get_newest_data_log",
	        type: "POST",
	        data: encodeURIComponent(JSON.stringify(data)),
	        success: function (resp) {
	        	var result = resp.result;
				
		        $('#get_newest_data_console .cnt2').html(result);
			 }
		 });
};

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
