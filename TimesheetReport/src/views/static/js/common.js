$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
		$('#content').toggleClass('active');
		if ($('#sidebar').hasClass('active')) {
			update_session(SESSION_SIDEBAR, 1);
		} else {
			update_session(SESSION_SIDEBAR, 0);
		}
    });
})

$(document).ready(function () {
    $('#notify_close').on('click', function () {
        $('.notify').hide();
    });
});


// multiple select 
function control_select_all_button() {
	var list_checkbox = $(FOCUS_MULTISELECT).find('.multi-select-menuitems').find('input');
	var is_check_all = true;
	list_checkbox.each(function(){
		if ($(this).prop('checked') == false) {
			is_check_all = false;
			return null;
		} 
	});
	$('.select-all').prop('checked', is_check_all);
	if (is_check_all) {
		$(FOCUS_MULTISELECT).find('.multi-select-button').text('All Values');
	}
}
$(function(){
    $('select[multiple]').multiSelect({
		allText: 'All Values'
	})
	$('.select-all').click(function() {
		var list_checkbox = $(FOCUS_MULTISELECT).find('.multi-select-menuitems').find('input');
		var result = [];
		var is_check_all = $(this).prop('checked');
		list_checkbox.each(function(){
			$(this).prop('checked', is_check_all);
		});
		if (is_check_all) {
			$(FOCUS_MULTISELECT).find('.multi-select-button').text('All Values');
		} else {
			$(FOCUS_MULTISELECT).find('.multi-select-button').text('-- Select --');
		}
		return result;
	})
	$('.multi-select-container').click(function() {
		FOCUS_MULTISELECT = $(this);
		control_select_all_button();
	})
	
});

// end multiple select 

$('input[type="file"]').change(function(e){
        var file_name = e.target.files[0].name;
        $('.custom-file-label').html(file_name);
    });

function create_dropdown_show_hide_column(id) {
    var cols = [];
    $(id + " thead tr th").each(function(){
        cols.push($(this).text());
    });
    var html = "";
    html += '<div class="dropdown allow-focus " style="margin-left: auto;">';
    html += '<button id="dropdownLabel" type="button" style="background-color: #e9e9e9; border: 1px solid #aaa;" class="btn btn-default mnw-auto" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">';
    html += '<i class="fas fa-bars"></i>';
    html += '</button>';
    html += '<div class="dropdown-menu panel" aria-labelledby="dropdownLabel">';
    
    for (var idx=0; idx < cols.length; idx++) {
		if (! idx) {
			html += '<input type="checkbox" class="toggle-vis" value="' + idx + '" checked id="show_hide_' + idx + '">' + '<label class="lb-toggle-vis" for="show_hide_' + idx + '">&nbsp;' + cols[idx] + '</label><br>';
		} else {
			html += '<input type="checkbox" class="toggle-vis" value="' + idx + '" checked id="show_hide_' + idx + '">' + '<label class="lb-toggle-vis" for="show_hide_' + idx + '">&nbsp;' + cols[idx] + '</label><br>';
		}
    }
    html += '</div>';
    $(id +  '_wrapper .top').append(html);
}

$(document).on('click', '.allow-focus .dropdown-menu', function (e) {
  e.stopPropagation();
});

function load_datatable (id, ordering, paging, info, scroll_class) {
	if (ordering == undefined) {
		ordering = true;
	}
	if (paging == undefined) {
		paging = true;
	}
	if (info == undefined) {
		info = true;
	}
	if (scroll_class == undefined) {
		scroll_class = '';
	}
    var table = $(id).DataTable({
		"dom": '<"top"f>rt<"bottom"lp><"clear">', 
		"ordering": ordering,
		"paging":   paging,
        "info":     info,
		"lengthMenu": [[10, 50, 100, -1], [10, 50, 100, "All"]],
		"iDisplayLength": 100,
		initComplete: function () {
        create_dropdown_show_hide_column(id);
    }
    });
	$(id).wrap('<div style="overflow-x: auto; resize: vertical;" class="' + scroll_class + '"></div>');
	$('input.toggle-vis').on( 'click', function (e) {
		var column_number = $(this).val();
		if (column_number != 0){
			var column = table.column(column_number);
        	column.visible( ! column.visible() );
		} else {
			$(this).prop('checked', true);
		}
        
    } );

}
function get_form_submit(form_id) {
	var data = $(form_id).serializeArray().reduce(function(obj, item){
        obj[item.name] = item.value.trim();
        return obj;
    }, {});
    return data
};

function get_value_from_multiple_select(prefix) {
	if (prefix == undefined) {
		prefix = 'undefined';
	}
	var list_checkbox = $('.multi-select-menuitems').find('input');
	var result = [];
	list_checkbox.each(function(){
		if ($(this).prop('checked') == true ) {
			let id = $(this).attr('id');
			if (id.startsWith(prefix)) {
				result.push($(this).val());
			}
			
		}
	});
	return result;
	}

function upload_file (form_id) {
	var form_data = new FormData($(form_id)[0]);
	var result = null;
    $.ajax({
        type: 'POST',
        url: UPLOAD_FILE,
		async: false,
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        success: function(resp) {
		result = resp.result;
        },
    });
	return result;
}

function get_data_from_form(form_id) {
	var data = get_form_submit(form_id);
	var sheet_ids = get_value_from_multiple_select();
	if (sheet_ids.length == 0) {
		custom_alert('No sheet name selected', 'error');
		return null;
	} 
	var ids = []
	for (var idx = 0; idx < sheet_ids.length; idx++) {
		ids.push(sheet_ids[idx]);
	}
	var users1 = get_value_from_multiple_select('user');
	
	if (users1.length == 0) {
		custom_alert('No user name selected', 'error');
		return null;
	} 
	var users2 = [];
	for (var idx = 0; idx < users1.length; idx++) {
		if (users1[idx] == 'all') {
			continue;
		}
		users2.push(users1[idx]);
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
	data[SESSION_USERS] = users2;
	return data;
}

function custom_alert(message, type) {
	$('#overlay_loader').hide();
	$('#overlay').hide();
	alert(message);
}

function update_session(session_key, session_value) {
	var data = {'session_key': session_key, 'session_value': session_value, };
	$.ajax({
	   url: UPDATE_SESSION,
	   type: "POST",
	   async: false,
	   data: encodeURIComponent(JSON.stringify(data)),
	   success: function(resp){
	   }
   });
}
$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();   
});

function parse_url() {
	var url_string = window.location.href;
	var url = new URL(url_string);
	var method_get_str = url.search;
	var method_str = method_get_str.replace("?", "");
	if (method_str.trim()) {
		var data = JSON.parse(decodeURIComponent(method_str));
	} else {
		var data = {};
	}
	var output = [method_get_str, data];
	return output;
}

function is_synchronize_task(data) {
	try {
		var out = [false, []];
	    $.ajax({
	        url: CHECK_LOADING_SMARTSHEET,
	        type: "POST",
			async: false,
	        data: encodeURIComponent(JSON.stringify(data)),
	        success: function (resp) {
	        	var result = resp.result;
				out = result;
			 }
		 });
		return out;
	} catch(err) {
		out = [false, []];
		return out;
	}
}
function check_loading_smartsheet() {
	try {
		var method_info = parse_url();
		var data = method_info[1];
	    $.ajax({
	        url: CHECK_LOADING_SMARTSHEET,
	        type: "POST",
	        data: encodeURIComponent(JSON.stringify(data)),
	        success: function (resp) {
	        	var result = resp.result;
				var is_running = result[0];
				var list_sheet_name = result[1];
				//var ctn = '<a class="cl-yellow" id="is_loading_smartsheet">WARNING:</a>' + 'Process to get data for "' + list_sheet_name + '" is running.';
				if (is_running) {
					//$('#notify_content').html(ctn);
					//$('#notify').show();
					$('#get_newest_data').attr('disabled', true);
					//$('#notify_close').hide();
				} else {
					//if ($('#is_loading_smartsheet').length) {
						//$('#notify_close').show();
					//$('#notify').hide();
						$('#get_newest_data').attr('disabled', false);
					//}
				}
				
			 }
		 });
	} catch(err) {
		console.log(err);
		return null;	
	}
}
$(document).ready(function() {
	$('#main_div').scroll(function() {
		if ($(this).scrollTop() > 300) {
			$('#to_top_btn').fadeIn();
		} else {
			$('#to_top_btn').fadeOut();
		}
	});
		
	$('#to_top_btn').click(function() {
	$("#main_div").animate({
		scrollTop: 0
		}, 1000);
	return false;
	});
});
function colect_config_date() {
	var data = get_form_submit('#timesheet_form');
	var sheet_ids = get_value_from_multiple_select();
	if (sheet_ids.length == 0) {
		custom_alert('No sheet name selected', 'error');
		return null;
	} 
	var ids = [];
	for (var idx = 0; idx < sheet_ids.length; idx++) {
		if (sheet_ids[idx] == 'all') {
			continue;
		}
		ids.push(sheet_ids[idx]);
	}
	var users1 = get_value_from_multiple_select('user');
	
	if (users1.length == 0) {
		custom_alert('No user name selected', 'error');
		return null;
	} 
	var users2 = [];
	for (var idx = 0; idx < users1.length; idx++) {
		if (users1[idx] == 'all') {
			continue;
		}
		users2.push(users1[idx]);
	}

	var from_date 	= data['from_date'];
	var to_date 	= data['to_date'];
	var filter 		= data['filter'];
	var task_filter = data['task_filter'];
	if (to_date == '' || from_date == '') {
		custom_alert('Missing date', 'error');
		return null;
	}
	let out = {};
	out[SESSION_FROM] = from_date;
	out[SESSION_TO] = to_date;
	out[SESSION_FILTER] = filter;
	out[SESSION_TASK_FILTER] = task_filter;
	out[SESSION_SHEETS] = ids;
	out[SESSION_USERS] = users2;
	return out;
}
$(document).ready(function () {
	$('#get_newest_data').click(function(event) {
		
		var data = colect_config_date();
		var method_get_url = encodeURIComponent(JSON.stringify(data));
		if (! confirm("This process will take about 1-5 minutes. Do you want to continue?")) {
			return null;
		}
		var is_running = is_synchronize_task(data);
		if (is_running[0]) {
			custom_alert('Process to synchronize data from smartsheet is running. Plelease try again later!');
			return null;
		}
		var cnt = "<div id='get_newest_data_console'><div class='cnt1'><div align='center' class='b-bottom '><b>Console</b><a class='close-p dp-none' onclick='close_overlay();'><i class='fas fa-times '></i></a></div><div class='cnt2'></div></div></div>";
		$('#overlay').html(cnt);
		$('#overlay').show();
		INTERVAL_GET_DATA = setInterval(function() {show_log_get_newest_data(); }, 2000);
		$.ajax({
			   url: GET_NEWEST_DATA,
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
	$('#lock').click(function(event) {
		var disable_sync = $('#get_newest_data').prop('disabled');
		var is_loading = 0;
		if (disable_sync) {
			var lock = 'Unlock';
			
		} else {
			var lock = 'Lock';
			is_loading = 1;
		}
		if (! confirm("Are you sure you want to " + lock + " 'Synchronize Data' feature?")) {
			return null;
		}
		var data = {'is_loading': is_loading}; 
		$('#overlay_loader').show();
		$.ajax({
			   url: LOCK_SYNC,
			   type: "POST",
			   data: encodeURIComponent(JSON.stringify(data)),
			   success: function(resp){
					check_loading_smartsheet();
				   $('#overlay_loader').hide();
					
			      }
		   });
	});
});

function show_log_get_newest_data() {
		var data = {};
	    $.ajax({
	        url: GET_NEWEST_DATA_LOG,
	        type: "POST",
	        data: encodeURIComponent(JSON.stringify(data)),
	        success: function (resp) {
	        	var result = resp.result;
		        $('#get_newest_data_console .cnt2').html(result);
			 }
		 });
};
function close_overlay(is_clean=true) {
	if (is_clean) {
		$('#overlay').html('');
	}
	$('#overlay').hide();
}

function get_template_content(path, handle_output) {
	var data = {'path': path};
	$.ajax({
		   url: GET_TEMPLATE_CONTENT,
		   type: "POST",
		   data: encodeURIComponent(JSON.stringify(data)),
		   success: function(resp){
			   var result = resp.result;
				handle_output(result);
		      }
	   });
}

function get_template_content_asyn(path) {
	var data = {'path': path};
	var out = '';
	$.ajax({
		   url: GET_TEMPLATE_CONTENT,
		   type: "POST",
			async: false,
		   data: encodeURIComponent(JSON.stringify(data)),
		   success: function(resp){
			   var result = resp.result;
				out = result;
		      }
	   });
	return out;
}
function parse_serialize(serialize){
	var out = {}
	var elements = serialize.split('&');
	for (var idx = 0; idx < elements.length; idx++ ){
		var items = elements[idx].split('=')
		out[items[0]] = items[1];
	}
	return out;
}

INTERVAL_CHECK_SMARTSHEET = setInterval(function() {check_loading_smartsheet(); }, 10000);