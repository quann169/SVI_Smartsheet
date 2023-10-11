function showExportPopup(){
    $('#overlay').show();
    get_template_content('components/export/export.html', function(template) {
        var content = template;
        $('#overlay').html(content);
        $('#overlay').show();
    });
}
function export_file (form_id, options) {
	$('#notify').hide();
	$('#overlay_loader').show();
	var data = get_data_from_form(form_id);
	if (! data) {
		return null;
	}
    data['options'] = options;
    data['cost'] = options['project']['cost'];
    $.ajax({
	   url: EXPORT,
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
	      }
   });
}
function getExportOptions() {
    var list_checkbox = $('.exportoption__content').find('input[type="checkbox"]');
    var options = {};
    options['detail'] = {'task_filter': []};
    options['resource'] = {'task_filter': [], 'filter': []};
    var cost = $('#project_cost').val();
    options['project'] = {'task_filter': [], 'filter': [], 'cost': cost};
    list_checkbox.each(function(){
        if (this.checked) {
            switch(this.id) {
                case 'detail_current':
                    options['detail']['task_filter'].push('current');
                    break;
                case'detail_final':
                    options['detail']['task_filter'].push('final');
                    break;
                case 'detail_both':
                    options['detail']['task_filter'].push('both');
                    break;
                case 'resource_current':
                    options['resource']['task_filter'].push('current');
                    break;
                case 'resource_final':
                    options['resource']['task_filter'].push('final');
                    break;
                case 'resource_both':
                    options['resource']['task_filter'].push('both');
                    break;
                case 'resource_weekly':
                    options['resource']['filter'].push('weekly');
                    break;
                case 'resource_monthly':
                    options['resource']['filter'].push('monthly');
                    break;
                case 'project_current':
                    options['project']['task_filter'].push('current');
                    break;
                case 'project_final':
                    options['project']['task_filter'].push('final');
                    break;
                case 'project_both':
                    options['project']['task_filter'].push('both');
                    break;
                case 'project_weekly':
                    options['project']['filter'].push('weekly');
                    break;
                case 'project_monthly':
                    options['project']['filter'].push('monthly');
                    break;
            }
        }
    });
    return options;
}
$(document).ready(function () {
	$('#export').click(function(event) {
		showExportPopup();
		
	});
    $(document).on('click', '#confirm_export', function(){
        var options = getExportOptions();
        export_file('form', options);
    })
});