



function load_timesheet_report() {
	var data = colect_config_date();
	if (data) {
		var method_get_url = encodeURIComponent(JSON.stringify(data));
		location.href = REPORT + '?' + method_get_url;
	}
}

$(document).ready(function () {
	$('#load').click(function(event) {
		load_timesheet_report();
	});
	$('.remove-row').click(function(event) {
		var tr = $(this).closest('tr');
		tr.remove();
	});
	
	
	$('#send_mail').click(function(event) {
		var data = {}; 
		var rows = $('#report_timesheet').find('tr');
		var  week = null;
		rows.each(function() {
			var email, resource, work_hours, timeoff, total, detail, comment, resource_mail;
			if ($(this).hasClass('week')) {
				week = $(this).find('td:first-child').html();
			} else if ($(this).hasClass('report-content')) {
				var td = $(this).find('td');
				td.each(function() {
					if ($(this).hasClass('email')) {
						email = $(this).html();
					} else if ($(this).hasClass('resource')) {
						resource = $(this).html();
					} else if ($(this).hasClass('work-hours')) {
						work_hours = $(this).html();
					} else if ($(this).hasClass('timeoff')) {
						timeoff = $(this).html();
					} else if ($(this).hasClass('total')) {
						total = $(this).html();
					} else if ($(this).hasClass('detail')) {
						detail = $(this).html();
					} else if ($(this).hasClass('comment')) {
						comment = $(this).html();
					} else if ($(this).hasClass('resource-mail')) {
						resource_mail = $(this).html();
					}
				})
				if (data[email] == undefined) {
					data[email] = {};
				}
				if (data[email][week] == undefined) {
					data[email][week] = [];
				}
				data[email][week].push([resource, work_hours, timeoff, total, detail, comment, resource_mail]);
			}
		});
		if (Object.keys(data).length){
			var popup_ctn = create_send_mail_popup(data);
			$('#overlay').html(popup_ctn);
			$('#overlay').show();
		} else {
			custom_alert('No data to send report.', 'error');
		}
	});
	$(document).on('click', '.e-span', function(){
		$('.mail-ctn').hide();
		var target_id = $(this).data("target");
		$('.e-span').attr('style', 'font-weight: none; color: black;');
		$(target_id).show();
		$(this).attr('style', 'font-weight: bold; color: blue;')
	});
	
	$(document).on('change', '.select-email', function(){
		var is_enable = false;
		$('.select-email').each(function() {
			if ($(this).prop('checked')) {
				is_enable = true;
				return null;
			}
		});
		$('#send').prop('disabled', !is_enable);
	});
	
});

function create_send_mail_popup(data) {
	var popup_ctn = `<div class='review-e-popup'>
		<div class='review-e-title'>
			<span>Send Report</span>
		</div>
		<div  class='review-e-menu'>
			<ul><li class='bold'>Send To</li>`
	var count = 0;
	var ctn = '';
	var template = get_template_content_asyn('components/sending_mail/report_timesheet.html');
	for (var [key, value] of Object.entries(data)) {
		count += 1;
		var active = 'font-weight: none; color: black;';
		if (count == 1) {
			active = 'font-weight: bold; color: blue;';
		}
		popup_ctn += '<li>';
		popup_ctn += "<input class='select-email' type='checkbox' data-target='#cnt_" + count + "' >";
		popup_ctn += "<span class='e-span' id='cnt_" + count + "_cb' data-target='#cnt_" + count + "' style='" + active + "'>" + key + "</span>";	
		popup_ctn += '</li>';
		var cc_recepient = {};
		var content = '';
		for (var [week, tb_info] of Object.entries(data[key])) {
			var row_info = data[key][week];
			content += '<b >Week: <span class="cl-red">' + week + '</span></b><br>';
			content += "<table class='e-rpt-tb'><thead>";
			content += "<tr><th>No.</th><th>Resource</th><th>Working hours</th><th>Off work</th>";
			content += "<th>Total</th><th>Detail</th><th>Comment</th></tr></thead>";
			content += "<tbody>";
			
			for (let idx = 0; idx < row_info.length; idx++) {
				var resource = row_info[idx][0];
				var w_hours = row_info[idx][1];
				var timeoff = row_info[idx][2];
				var total = row_info[idx][3];
				var detail = row_info[idx][4];
				var comment = row_info[idx][5];
				var resource_mail = row_info[idx][6];
				cc_recepient[resource_mail] = '';
				content += '<tr>';
				content += '<td>' + (idx + 1) + '</td>';
				content += '<td>' + resource + '</td>';
				content += '<td>' + w_hours + '</td>';
				content += '<td>' + timeoff + '</td>';
				content += '<td>' + total + '</td>';
				content += '<td>' + detail + '</td>';
				content += '<td>' + comment + '</td>';
				content += '</tr>';
			}
			content += "</tbody>";
			content += "</table><br>";
		}
		var mail_content = eval('`' + template + '`');
		var block = 'dp-none';
		if (count == 1) {
			block = 'dp-block';
		}
		var list_cc = Object.keys(cc_recepient);
		var cc_str = list_cc.join('; ');
		ctn += "<div id='cnt_" + count + "_cc' class='cc-content dp-none' >" + cc_str + "</div>";
		ctn += "<div id='cnt_" + count + "' class='mail-ctn " + block + "' contenteditable='true'>" + mail_content + "</div>";
	}
    popup_ctn += `</ul>
	</div>
	<div class='review-e-content' >`;
	popup_ctn += ctn;	
	popup_ctn += `</div>
	<div class='review-e-footer'>
		<button onclick='close_overlay();' id='' class='' data-toggle="tooltip" title="Cancel"><i class="fas fa-arrow-left"></i></button>
		<button onclick='' id='send' class='' data-toggle="tooltip" title="Send" disabled><i class="fas fa-paper-plane"></i></button>
	</div>
</div>`;
	return popup_ctn;
}

$(document).ready(function () {
	$(document).on('click', '#send', function(){
		if (! confirm("Are you sure you want to continue?")) {
			return null;
		}
		$('#overlay_loader').show();
		var data = {};
		$('.select-email').each(function(){
			if ($(this).prop('checked')) {
				var target_id = $(this).data("target");
				var recepient = $(target_id + '_cb').html();
				var cc_recepient = $(target_id + '_cc').html();
				var mail_body = $(target_id).html();
				data[recepient] = {'cc': cc_recepient, 'body': mail_body};
			}
		})
		$.ajax({
			   url: SEND_REPORT,
			   type: "POST",
			   data: encodeURIComponent(JSON.stringify(data)),
			   success: function(resp){
				   var result = resp.result;
					if (result[0]) {
						$('#overlay').hide();
					}
					custom_alert(result[1], 'info');
					$('#overlay_loader').hide();
			      }
		   });
	});
})

