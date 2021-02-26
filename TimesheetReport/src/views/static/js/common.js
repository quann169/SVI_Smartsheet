$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });
});



$('input[type="file"]').change(function(e){
        var file_name = e.target.files[0].name;
        $('.custom-file-label').html(file_name);
    });

function load_datatable (id) {
	$(id).DataTable({
		 "dom": '<"top"if>rt<"bottom"lp><"clear">'
	});
}

function get_form_submit(form_id) {
	var data = $(form_id).serializeArray().reduce(function(obj, item){
        obj[item.name] = item.value.trim();
        return obj;
    }, {});
    return data
};

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

function custom_alert(message, type) {
	alert(message);
}

