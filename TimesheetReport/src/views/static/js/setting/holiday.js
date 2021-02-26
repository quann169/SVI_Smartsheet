// submit import timeoff form
$(document).ready(function () {
	$('#import_holiday').submit(function(event) {
		event.preventDefault();
		var up_file = upload_file('#import_holiday');
		if (up_file != null && up_file[0] == 1) {
			var file_name	= $('#holiday_file').get(0).files[0].name;
			var data = {'file_name': file_name};
			$.ajax({
			   url: '/import_holiday',
			   type: "POST",
			   async: false,
			   data: encodeURIComponent(JSON.stringify(data)),
			   success: function(resp){
				   var result = resp.result;
					if (result[0]) {
						custom_alert(result[1], 'success');
						location.reload();
					} else {
						custom_alert(result[1], 'error');
					}
			   }
		   });
		} else {
			custom_alert(up_file[1], 'error');
		}
	})
})

// control 'import' btn
$('#holiday_file').change(function(e){
        var files	= $('#holiday_file').get(0).files[0];
		if (files == undefined) {
			$('#btn_import').prop('disabled', true);
		} else {
			$('#btn_import').prop('disabled', false);
		}
    });

$(document).ready( function () {
	load_datatable('#holiday_table');
	});