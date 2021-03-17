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
});

$(document).ready(function () {
    $('#notify_close').on('click', function () {
        $('.notify').hide();
    });
});


// multiple select 
$(function(){
	    $('select[multiple]').multiSelect({
	})
	$('.select-all').click(function() {
		const list_checkbox = $('.multi-select-menu').find('input');
		var result = [];
		var is_check_all = $(this).prop('checked');
		list_checkbox.each(function(){
			$(this).prop('checked', is_check_all);
			
		});
		if (is_check_all) {
			$('.multi-select-button').text('All Values');
		} else {
			$('.multi-select-button').text('-- Select --');
		}
		return result;
	})
});

$('input[type="file"]').change(function(e){
        var file_name = e.target.files[0].name;
        $('.custom-file-label').html(file_name);
    });

function load_datatable (id) {
	
	// $(id + ' thead th').each( function () {
    //     var title = $(this).text();
    //     $(this).html(title);
    // } );
 
    // DataTable
    $(id).DataTable({
		"dom": '<"top"f>rt<"bottom"lp><"clear">',
		"scrollX": true,
    //     initComplete: function () {
    //         // Apply the search
    //         this.api().columns().every( function () {
    //             var that = this;
    //             $( 'input', this.header() ).on( 'keyup change clear', function () {
    //                 if ( that.search() !== this.value ) {
    //                     that
    //                         .search( this.value )
    //                         .draw();
    //                 }
    //             } );
    //         } );
    //     }
    });
}

function get_form_submit(form_id) {
	var data = $(form_id).serializeArray().reduce(function(obj, item){
        obj[item.name] = item.value.trim();
        return obj;
    }, {});
    return data
};

function get_value_from_multiple_select() {
	const list_checkbox = $('.multi-select-menu').find('input');
	var result = [];
	list_checkbox.each(function(){
		if ($(this).prop('checked') == true ) {
			result.push($(this).val());
		}
	});
	return result;
	}

function upload_file (form_id) {
	var form_data = new FormData($(form_id)[0]);
	var result = null;
    $.ajax({
        type: 'POST',
        url: '/upload_file',
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
	return data;
}

function export_file (form_id) {
	$('#notify').hide();
	$('#overlay_loader').show();
	var data = get_data_from_form(form_id);
	if (! data) {
		return null;
	}
    $.ajax({
	   url: '/export',
	   type: "POST",
	   data: encodeURIComponent(JSON.stringify(data)),
	   success: function(resp){
		   var result = resp.result;
			if (result[0]) {
					var file_name = result[1];
					var link = 'dowload_file?' + SESSION_FILE_NAME + '=' + file_name;
					var ctn = 'Export successfully. Click here to download:' + '<a class="cl-blue" href="' + link + '"><u>  ' + file_name + '</u></a>'
					$('#notify_content').html(ctn);
					$('#notify').show();
					$('#overlay_loader').hide();
				} else {
					custom_alert(result[1], 'error');
				}
	      }
   });
}
$(document).ready(function () {
	$('#export').click(function(event) {
		export_file('form');
	});
});

function custom_alert(message, type) {
	$('#overlay_loader').hide();
	$('#overlay').hide();
	alert(message);
}

function update_session(session_key, session_value) {
	var data = {'session_key': session_key, 'session_value': session_value, };
	$.ajax({
	   url: '/update_session',
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
	var data = {};
	
	var list_arg = method_str.split('&');
	
	for (var idx =0; idx < list_arg.length; idx++) {
		if (list_arg[idx].length > 0) {
			var spl = list_arg[idx].split('=');
			var key = spl[0];
			var value = spl[1];
			if (key == SESSION_SHEETS) {
				if (key in data) {
					data[key].push(value);
				} else {
					data[key] = [value];
				}
			} else {
				data[key] = value;
				}
		}
	}
	var output = [method_get_str, data];
	return output;
}

function check_loading_smartsheet() {
	var method_info = parse_url()
	var data = method_info[1];
    $.ajax({
        url: "/check_loading_smartsheet",
        type: "POST",
        data: encodeURIComponent(JSON.stringify(data)),
        success: function (resp) {
        	var result = resp.result;
			var is_running = result[0];
			var list_sheet_name = result[1];
			var ctn = '<a class="cl-yellow" id="is_loading_smartsheet">WARNING:</a>' + 'Process to get data for "' + list_sheet_name + '" is running.';
			if (is_running) {
				$('#notify_content').html(ctn);
				$('#notify').show();
				$('#get_newest_data').attr('disabled', true);
				$('#notify_close').hide();
			} else {
				if ($('#is_loading_smartsheet').length) {
					$('#notify_close').show();
					$('#notify').hide();
					$('#get_newest_data').attr('disabled', false);
				}
				
			}
			
		 }
	 });
};
INTERVAL_CHECK_SMARTSHEET = setInterval(function() {check_loading_smartsheet(); }, 5000);