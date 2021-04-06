// submit import sheet form
$(document).ready(function () {
	$('#import_sheet').submit(function(event) {
		event.preventDefault();
		var up_file = upload_file('#import_sheet');
		$('#overlay_loader').show();
		if (up_file != null && up_file[0] == 1) {
			var file_name	= $('#sheet_file').get(0).files[0].name;
			var data = {'file_name': file_name};
			$.ajax({
			   url: IMPORT_SHEET,
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


$(document).ready(function () {
	$('#mode').change(function(event) {
		var mode = $(this).val();
		var request = {};
		request[SESSION_MODE] = mode;
		location.href = SHEET + '?' + encodeURIComponent(JSON.stringify(request));;
	});
	
});

// control 'import' btn
$('#sheet_file').change(function(e){
        var files	= $('#sheet_file').get(0).files[0];
		if (files == undefined) {
			$('#btn_import').prop('disabled', true);
		} else {
			$('#btn_import').prop('disabled', false);
		}
    });

$(document).ready( function () {
	load_datatable('#sheet_table', false, false, false);
});

$(document).ready(function() {
	$('#save_form')
	.each(function() {
	    $(this).data('serialized', $(this).serialize())
	})
	.on('change input', 'input, select, textarea', function(e) {
	    var $form = $(this).closest("form");
		var state = $form.serialize() === $form.data('serialized');
		$('#save').attr('disabled', state);
	})
	$('#save').attr('disabled', true);
	}
);
// save the changes
function parse_serialize(serialize){
	var out = {}
	var elements = serialize.split('&');
	for (var idx = 0; idx < elements.length; idx++ ){
		var items = elements[idx].split('=')
		out[items[0]] = items[1];
	}
	return out;
}

$(document).ready( function () {
	$(document).on('click', '#save', function() {
		if (! confirm("Are you sure you want to save all the changes?")) {
			return null;
		} else {
			var $form = $('#save_form').closest("form");
			var serialize = $form.serialize();
			var first_serialize = $form.data('serialized');
			var serialize_obj = parse_serialize(serialize);
			var first_serialize_obj = parse_serialize(first_serialize);
			var data = {};
			for (var [key, value] of Object.entries(serialize_obj)) {
				if (value != first_serialize_obj[key]) {
					var split_id = key.split('_');
					var sheet_id = split_id[1];
					if (! data[sheet_id]) {
						data[sheet_id] = {};
					}
					if (split_id[2] == 'type') {
						data[sheet_id]['sheet_type'] = value;
					} else if (split_id[2] == 'active') {
						data[sheet_id]['is_active'] = '1';
					} else if (split_id[2] == 'resource') {
						if (split_id.length == 3) {
							continue;
						}
						if (! data[sheet_id]['resource']) {
							data[sheet_id]['resource'] = {'remove': [], 'add': []};
						}
						data[sheet_id]['resource']['add'].push(value);
					}
				}
				delete first_serialize_obj[key];
			}
			for (var [key, value] of Object.entries(first_serialize_obj)) {
				if (value != serialize_obj[key]) {
					var split_id = key.split('_');
					var sheet_id = split_id[1];
					
					if (! data[sheet_id]) {
						data[sheet_id] = {};
					}
					if (split_id[2] == 'type') {
						data[sheet_id]['sheet_type'] = value;
					} else if (split_id[2] == 'active') {
						data[sheet_id]['is_active'] = '0';
					} else if (split_id[2] == 'resource') {
						if (split_id.length == 3) {
							continue;
						}
						if (! data[sheet_id]['resource']) {
							data[sheet_id]['resource'] = {'remove': [], 'add': []};
						}
						data[sheet_id]['resource']['remove'].push(value);
					}
				}
			}
			$('#overlay_loader').show();
			$.ajax({
		        url: SAVE_SHEET_SETTING,
		        type: "POST",
		        data: encodeURIComponent(JSON.stringify(data)),
		        success: function (resp) {
		        	var result = resp.result;
					if (result[0]) {
						location.reload();
					} else {
						custom_alert(result[1], 'error');
					}
				 }
			 });
		}
	})
});
function get_sync_sheet_data(handle_output) {
	var data = {};
	var out = "";
	$.ajax({
		   url: GET_SYNC_SHEET,
		   type: "GET",
		   data: encodeURIComponent(JSON.stringify(data)),
		   success: function(resp){
			   var result = resp.result;
				handle_output(result);
		      }
	   });
}

$(document).ready( function () {
	$('#sync_sheet').click(function() {
		get_template_content('components/sync_smartsheet/sync_table.html', function(template) {
			var tbody = '<td colspan="5">' + LOADING_2_LINE + '</td>';
			var content = eval('`' + template + '`')
			$('#overlay').html(content);
			$('#overlay').show();
			get_sync_sheet_data(function(sync_data) {
				var sheet_types = sync_data['sheet_types'];
				var sheets = sync_data['sheets'];
				tbody = '';
				var count = 0; 
				for (const [key, value] of Object.entries(sheets)) {
					count += 1;
					var is_active = sheets[key].is_active;
					var is_valid = sheets[key].is_valid;
					var missing_cols = sheets[key].missing_cols;
					var check = '';
					var is_disable_active = '';
					if (is_active == 1) {
						check = 'checked';
					}
					var valid_icon = `<input type='checkbox' class='is-valid-checkbox dp-none'><i class="fas fa-exclamation-circle cl-red"  data-html="true" data-toggle="tooltip" data-placement="left" title="Missing: ${missing_cols}"></i>`;
					if (is_valid == 1) {
						valid_icon = `<input type='checkbox' class='is-valid-checkbox dp-none' checked><i class="fas fa-check-circle cl-green" ></i>`;
					} else {
						check = '';
						is_disable_active = 'disabled';
					}
					var type = sheets[key].sheet_type;
					tbody += '<tr>';
					tbody += `<td class="count">${count}</td>`;
					tbody += `<td class="sheet-name">${key}</td>`;
					tbody += `<td class="sheet-type"><select class="sheet-type-select">`;
					for (const [sheet_type, sheet_type_id] of Object.entries(sheet_types)) {
						var is_selected = '';
						if (type == sheet_type) {
							is_selected = 'selected';
						}
						tbody += `<option value='${sheet_type}' ${is_selected}>${sheet_type}</option>`;
					}
					tbody += `</select></td>`;
					tbody += `<td class="is-active"><input type='checkbox' ${check} ${is_disable_active} class='is-active-checkbox'></td>`;
					tbody += `<td class="is-valid">${valid_icon}</td>`;
					tbody += '</tr>';
				}
				content = eval('`' + template + '`')
				$('#overlay').html(content);
				$('#sync_sheet_back').prop('disabled', false);
				$('#sync_sheet_save').prop('disabled', false);
			});
			
		});
	})
	$(document).on('click', '#sync_sheet_save', function() {
		$('#overlay_loader').show();
		var info = get_data_from_sync_sheet_table();
		var data = {};
		data['info'] = info;
		$.ajax({
		   url: UPDATE_SYNC_SHEET,
		   type: "POST",
		   data: encodeURIComponent(JSON.stringify(data)),
		   success: function(resp){
				$('#overlay_loader').hide();
			    var result = resp.result;
				if (result[0]) {
					custom_alert(result[1], 'success');
					location.reload();
				} else {
					custom_alert(result[1], 'error');
				}
		   }
	   });
	});
})

function get_data_from_sync_sheet_table() {
	var table = $('#sync_sheet_table');
	var output = [];
	table.find('tr').each (function() {
		var sheet_name = null;
		var sheet_type = null;
		var is_active = null;
		var is_valid = null;
		$(this).find('td').each (function() {
			var class_name = $(this).attr('class');
		  	if (class_name == 'sheet-name') {
				sheet_name = $(this).html();
			} else if (class_name == 'sheet-type'){
				$(this).find('.sheet-type-select').each (function() {
					sheet_type = $(this).val();
				});
			} else if (class_name == 'is-active'){
				$(this).find('.is-active-checkbox').each (function() {
					is_active = $(this).prop('checked');
					if (is_active) {
						is_active = 1;
					} else {
						is_active = 0;
					}
				});
			} else if (class_name == 'is-valid') {
				$(this).find('.is-valid-checkbox').each (function() {
					is_valid = $(this).prop('checked');
					if (is_valid) {
						is_valid = 1;
					} else {
						is_valid = 0;
					}
				});
			}
		});
		if ( ! (sheet_name == null && sheet_type == null && is_active == null && is_valid == null)) {
			output.push([sheet_name, sheet_type, is_active, is_valid]);
		}
	});
	return output;
}