$(document).ready( function () {
	load_datatable('#other_setting_table', false, false, false);
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
			data['info'] = {};
			for (var [key, value] of Object.entries(serialize_obj)) {
				if (value != first_serialize_obj[key]) {
					data['info'][decodeURIComponent(key)] = value;
				}
			}
			$('#overlay_loader').show();
			$.ajax({
		        url: SAVE_OTHER_SETTING,
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