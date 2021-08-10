// submit import timeoff form
$(document).ready(function () {
	$('#import_granted').submit(function(event) {
		event.preventDefault();
		
		var up_file = upload_file('#import_granted');
		$('#overlay_loader').show();
		if (up_file != null && up_file[0] == 1) {
			var file_name	= $('#granted_file').get(0).files[0].name;
			var data = {'file_name': file_name};
			$.ajax({
			   url: IMPORT_GRANTED,
			   type: "POST",
			   //async: false,
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
$('#granted_file').change(function(e){
        var files	= $('#granted_file').get(0).files[0];
		if (files == undefined) {
			$('#btn_import').prop('disabled', true);
		} else {
			$('#btn_import').prop('disabled', false);
		}
    });

$(document).ready( function () {
	load_datatable('#granted_table', false);
	});