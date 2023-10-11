function get_option() {
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
	
	let out = {};
	out[SESSION_SHEETS] = ids;
	return out;
}

function load_timesheet_report() {
	var data = get_option();
	if (data) {
		var method_get_url = encodeURIComponent(JSON.stringify(data));
		location.href = EFFECTIVE_RATE + '?' + method_get_url;
	}
}

$(document).ready(function () {
    $('#load').click(function(event) {
		load_timesheet_report();
	});
	$('#checkout').click(function() {
		var data = get_option();
		var method_get_url = encodeURIComponent(JSON.stringify(data));
		if (! confirm("This process will take about 10-15 minutes. Do you want to continue?")) {
			return null;
		}
		
		var cnt = "<div id='get_newest_data_console'><div class='cnt1'><div align='center' class='b-bottom '><b>Console</b><a class='close-p dp-none' onclick='close_overlay();'><i class='fas fa-times '></i></a></div><div class='cnt2'></div></div></div>";
		$('#overlay').html(cnt);
		$('#overlay').show();
		INTERVAL_GET_DATA = setInterval(function() {show_log_get_newest_data('EffectiveRate.log'); }, 2000);
		$.ajax({
			   url: SYNC_EFFECTIVE_DATA,
			   type: "POST",
			   data: encodeURIComponent(JSON.stringify(data)),
			   success: function(resp){
				   var result = resp.result;
					clearInterval(INTERVAL_GET_DATA);
					INTERVAL_GET_DATA = null;
					$('#get_newest_data_console .close-p').show();

			      },
                  error: function(resp){
                    clearInterval(INTERVAL_GET_DATA);
					INTERVAL_GET_DATA = null;
                    $('#get_newest_data_console .close-p').show();
                    
                }
		   });
	});
    $('#export_effective').click(function(){
        var data = get_option();
        $('#notify').hide();
	    $('#overlay_loader').show();
        $.ajax({
            url: EXPORT_EFFECTIVE,
            type: "POST",
            data: encodeURIComponent(JSON.stringify(data)),
            success: function(resp){
                var result = resp.result;
                if (result[0]) {
                        var file_name = result[1];
                        var data = {}
                        data[SESSION_FILE_NAME] = file_name;
                        var method_url = encodeURIComponent(JSON.stringify(data));
                        var link = DOWNLOAD_FILE + '?' + method_url;
                        var ctn = 'Export successfully. Click here to download:' + '<a class="cl-blue" href="' + link + '"><u>  ' + file_name + '</u></a>'
                        $('#notify_content').html(ctn);
                        $('#notify').show();
                        $('#overlay_loader').hide();
                        $('#overlay').hide();
                    } else {
                        custom_alert(result[1], 'error');
                    }
            },
            error: function(resp){
                $('#overlay_loader').hide();
                $('#overlay').hide();
            }
        });
    })
});