const roundNum = 1000;
function draw_stack_column_chart(id, data, label_angle, type) {
	let tooltip = $('#tooltip').prop('checked');
	let lenCategoryLv1 = parseInt(data.category.length / 2) + 1;
	let lenCategoryLv2 = data.category[0].categories.length;
	let series_list = [];
	let enableStackLabel = false;
	var listIdxShowStackLabel = [];
	if (type == 'chart2'){
		enableStackLabel = true;
		// find list index to show stacklabel
		let center_num = parseInt(lenCategoryLv2 / 2) + 1;
		if (lenCategoryLv2 % 2 == 0) {
			center_num = parseInt(lenCategoryLv2 / 2);
		}
		var count  = -1;
		for (let idx1 = 0; idx1 < lenCategoryLv1; idx1++) {
			listIdxShowStackLabel.push(count + center_num);
			count  += lenCategoryLv2 + 1;
		}
	}
	
	let dataLabel =  {
		enabled: true,
		color: '#000',
		align: 'center',
		// y: 10, // 10 pixels down from the top
		style: {
			// fontSize: '10px',
			textShadow: false,
			textOutline: false,
			fontWeight: '500',
			fontFamily: "Calibri (Body)",
		},
		formatter:function(){
			let min = 1;
			if (type == 'chart2') {
				min = 0.1;
			}
			if(this.y > min) {
				if (type == 'chart2') {
					let num = (this.y / this.total) * (100);
					let label = Math.round(num ) + '%';
					return label;
				} else {
					let label = Math.round(this.y) + '%';
					return label;
				}
			} 	
		}
	}
	var color_maping = ['#007BA9', '#fdd86c', '#a8d18d', '#f45b5b', '#d0cecf', '#abdbe3', '#fd7e14'];
	let sheet_type_order = ["NRE", "RnD", "TRN", "Non-WH", "Operating", "Support", "Pre-sale"];
	for (let idx = sheet_type_order.length - 1; idx >= 0; idx--) {
		let type = sheet_type_order[idx];
		let tmp_series = {stacked: '1', name: type, data: [], color: color_maping[idx], label: 'sss',  dataLabels: dataLabel};
		for (let idx1 = 0; idx1 < data.category.length; idx1++) {
			let name = data.category[idx1].name;
			let list_category = data.category[idx1].categories;
			for (let idx2 = 0; idx2 < list_category.length; idx2++){
				let date = list_category[idx2];
				let text = name + ' ' + date;
				if (! data.info[type][text]) {
					tmp_series.data.push(0);
				} else {
					let value = data.info[type][text].value;
					tmp_series.data.push(value);
				}
			}
		}
		series_list.push(tmp_series);
	}
	if (label_angle == undefined) {
		var label_angle = 0;
	}
	let chart = Highcharts.chart(id, {
		chart: {
			type: 'column'
		},
		title: {
			text: data.title
		},
		xAxis: {
			tickWidth: 0,
			labels: {
				groupedOptions: [{
					style: {
						padding: '5px',
						fontWeight: '500',
						fontFamily: "Calibri (Body)",
					},
					rotation: 0,
				}],
				style: {
					fontWeight: '500',
					fontFamily: "Calibri (Body)",
				},
				rotation: label_angle
			},
			  categories: data.category
		},
		tooltip: {
            enabled: tooltip
        },
		
		yAxis: {
			allowDecimals: false,
			min: 0,
			title: {
				text: ''
			},
			labels: {
				formatter:function(){
					if (type == 'chart1') {
						let label = this.value + '%';
						return label;
					} else {
						return this.value;
					}
				}
			},
			stackLabels: {
                    enabled: enableStackLabel,
					formatter: function() {
						if (this.total > 0 ){
							let x = this.x;
							if (listIdxShowStackLabel.indexOf(x) != -1) {
								return this.total;
							}
							
						}
					}
                }
		},
		legend: {
			itemHiddenStyle: {
				color: '#ffffff'
			}
		},
		
		plotOptions: {
			column: {
				stacking: 'normal'
			},
			series: {
				enableMouseTracking: tooltip,
				grouping: false,
				groupPadding: 0,
				pointPadding: 0,
			  }
		},
	
		series: series_list
	});
}
function get_list_header(id) {
	var tr = $(id).find('tr');
	var head_num = 0;
	var headers = {};
	var num_col = null;
	tr.each(function() {
		var th = $(this).find('th');
		var sum_th = th.length;
		if (sum_th) {
			head_num += 1;
			var tmp_list = [];
			if (num_col && sum_th < num_col) {
				var delta = num_col - sum_th;
				var prev_num = head_num - 1;
				var prev_list = headers[prev_num.toString()];
				
				tmp_list = prev_list.slice(0, delta);
			}
			th.each(function() {
				var colspan = $(this).attr('colspan');
				var rowspan = $(this).attr('rowspan');
				var name = $(this).html();
					if (colspan > 0) {
						for (var idx = 0; idx < colspan; idx++) {
							tmp_list.push(name);
						}
					} else {
						tmp_list.push(name);
					}
			});
			headers[head_num.toString()] = tmp_list;
			num_col = tmp_list.length;
		}
	});
	return headers;
}

function creat_productivity_data(row_data, headers, group_id, title, max_hours, type) {
	var out = {}
	var data = {};
	out['title'] = title;
	var list_col = [];
	var list_type = [];
	//create list column
	for (var idx = 6; idx < headers['1'].length; idx++) {
		if (! list_col.includes(headers['1'][idx])) {
			list_col.push(headers['1'][idx]);
		}
	}
	// create list column 2
	for (var idx2 = 6; idx2 < headers['2'].length; idx2++) {
		if (! list_type.includes(headers['2'][idx2])) {
			list_type.push(headers['2'][idx2]);
		}
	}

	// group data
	for (var idx3=0; idx3 < row_data.length; idx3++) {
		if (group_id == -1) {
			name = '';
		} else {
			if (row_data[idx3][group_id] == 0) {
				name = '';
			} else {
				var name = row_data[idx3][group_id].trim();
				}
		}
		// skip empty group
		if (name == '' && group_id != -1) {
			continue
		}
		if (! data.hasOwnProperty(name) ) {
			data[name] = {};
		} 
		for (var idx4 = 6; idx4 < headers['2'].length; idx4++) {
			var header_1 = headers['1'][idx4];
			var header_2 = headers['2'][idx4];
			var value = row_data[idx3][idx4];
			var val_num = parseFloat(value);
			var std_hour = max_hours[idx4];
			if (! data[name].hasOwnProperty(header_1)  ) {
				data[name][header_1] = {};
				data[name][header_1]['total'] = {};
			}
			if (! data[name][header_1].hasOwnProperty(header_2)) {
				data[name][header_1][header_2] = 0;
			}
			if (val_num > std_hour) {
				val_num = std_hour;
			}
			data[name][header_1][header_2] += val_num;
			if (! data[name][header_1]['total'].hasOwnProperty(header_2)) {
				data[name][header_1]['total'][header_2] = 0;
			}
			data[name][header_1]['total'][header_2] += std_hour;
			
		}
	}
	// 
	if (type == 'chart2') {
		for (var [group, value] of Object.entries(data)) {
			for (var [week, value2] of Object.entries(value)) {
				let remainHours = value2['total']['NRE'];
				for (var [type_name, value3] of Object.entries(value2)) {
					if (type_name != 'total') {
						if (type_name == 'Non-WH') {
							data[group][week][type_name] = remainHours;
						} else {
							remainHours = remainHours - value3;
							if (remainHours < 0) {
								remainHours = 0;
							}
						}
					} 
				}
			}
		}
	}
	// caculate percent
	for (var [group, value] of Object.entries(data)) {
		for (var [week, value2] of Object.entries(value)) {
			for (var [type_name, value3] of Object.entries(value2)) {
				if (type_name != 'total') {
					var total = value2['total'][type_name];
					var percent = value3 * 100 / total;
					data[group][week][type_name] = Math.round(percent * roundNum) / roundNum;
				} 
			}
		}
	}
	out['info'] = {};
	var list_group = Object.keys(data);
	var list_col2 = []
	
	for (var idx5=0; idx5 < list_type.length; idx5++ ) {
		var type_name = list_type[idx5];
		
		if (! out['info'].hasOwnProperty(type_name)) {
			out['info'][type_name] = {};
		}
		var count  = 0;
		var category_list = [];
		for (var i = 0; i < list_group.length; i++){
			count += 1;
			var group = list_group[i];
			var tmp_category = {};
			for (var idx6=0; idx6 < list_col.length; idx6++ ) {
				var week = list_col[idx6];
				var day = week.split('-')[1] + '-' + week.split('-')[2];
				var stdHour = max_hours[idx6*7 + 6];
				var percent = data[group][week][type_name];
				var total = data[group][week]['total'][type_name];
				var label = '';
				if (percent) {
					label = percent.toString();
				}
				// chart1/chart2 format
				if (type == 'chart1'){
					var value = percent;
				} else if (type == 'chart2') {
					var resourceNum = total / stdHour;
					var value = (percent / 100) * (resourceNum) ;
					value = Math.round(value * roundNum) / roundNum;
				}
				out['info'][type_name][group + ' ' + day] = {'value': value, 'x': count, 'label': label};
				count += 1;
				if (! list_col2.includes(group  + ' ' + day)) {
					list_col2.push(group + ' ' + day);
				}
				if (! tmp_category.hasOwnProperty('categories')) {
					tmp_category = {name: group, categories: []}
				}
				tmp_category.categories.push(day);
			}
			category_list.push(tmp_category);
			if (i < list_group.length - 1) {
				category_list.push({name: '', categories: ['']});
			}
			
		}
	}
	
	out['column'] = list_col2;
	out['type'] = list_type;
	out['category'] = category_list;
	return out;	
	
}
function get_data_productivity() {
	var table_id = '#productivity';
	var headers = get_list_header('#productivity');
	var tr = $(table_id).find('tr');
	var row_data = [];
	var max_hours = []
	var is_go = true;
	tr.each(function() {
		var td = $(this).find('td');
		var sum_td = td.length;
		var tmp = [];
		if (sum_td) {
			var tmp_data = [];
			td.each(function() {
				var value = $(this).html();
				if (value.trim() == '') {
					value = 0;
				}
				tmp_data.push(value);
				var max_h = $(this).data('target');
				tmp.push(max_h);
			});
			if (! max_hours.length) {
				max_hours = tmp;
			}
			row_data.push(tmp_data)
		}
	});
	var result = [headers, row_data, max_hours];
	return result;
}
function drawChart(type){
	var table_info = get_data_productivity();
	var headers = table_info[0];
	var row_data = table_info[1];
	var  max_hours = table_info[2];
	var team_productivity = creat_productivity_data(row_data, headers, 2, 'Team Productivity', max_hours, type);
	draw_stack_column_chart('team_productivity', team_productivity, 90, type);
	
	var field_productivity = creat_productivity_data(row_data, headers, 5, 'Field Productivity', max_hours, type);
	draw_stack_column_chart('field_productivity', field_productivity, 90, type);
	
	var seniority_productivity = creat_productivity_data(row_data, headers, 4, 'Seniority Productivity', max_hours, type);
	draw_stack_column_chart('seniority_productivity', seniority_productivity, 90, type);
	
	var headcount_productivity = creat_productivity_data(row_data, headers, -1, 'Headcount', max_hours, type);
	draw_stack_column_chart('headcount', headcount_productivity, 0, type);
}

$(document).ready(function() {
	$('#view_chart').click(function(){
		var content = `
		<div class='productivity-block' align='center'>
			<div class='productivity-taskbar' align='center' class='b-bottom '><b>Chart</b><a class='close-p' style='transform: translate(-165%, 0%) !important;' onclick='close_overlay();'><i class='fas fa-times '></i></a></div>
			<div class='productivity-ctn'>
			    <div class='chart-option'>
					<input type='checkbox' id='tooltip' checked class='mr-2'><label class='mr-2 my-0' for='tooltip'>Tooltip</label>
					<button id='reload_chart' class='mr-2'>Reload</button>
					<select id='chart_option'>
						<option value='chart1'>Percent</option>
						<option value='chart2'>Headcount</option>
					</select>
				</div>
				<div id="team_productivity" style="height: 700px; width: 95%; resize: both; border: 1px solid #aaa;">
				</div><br>
				<div id="field_productivity" style="height: 700px; width: 95%; resize: both; border: 1px solid #aaa;">
				</div><br>
				<div id="seniority_productivity" style="height: 700px; width: 50%; resize: both; border: 1px solid #aaa;">
				</div><br>
				<div id="headcount" style="height: 600px; width: 30%; resize: both; border: 1px solid #aaa;">
				</div><br><br><br><br>
			</div>
		</div>
		`
		$('#overlay').html(content);
		$('#overlay').show();
		drawChart('chart1');
	})
})

$(document).on('change', '#chart_option', function () {
	let type = $(this).val();
	drawChart(type);
})

$(document).on('click', '#reload_chart', function () {
	let type = $('#chart_option').val();
	drawChart(type);
})

function load_timesheet_report() {
	var data = colect_config_date();
	if (data) {
		var method_get_url = encodeURIComponent(JSON.stringify(data));
		location.href = RESOURCE_PRODUCTIVITY + '?' + method_get_url;
	}
}

$(document).ready(function () {
	$('#load').click(function(event) {
		load_timesheet_report();
	});
	$('#task_filter').change(function(event) {
		load_timesheet_report();
	});
	$('#export_productivity').click(function(event) {
		export_productivity();
	});
	$(document).on('click', '.remove-row', function(event) {
		var tr = $(this).closest('tr');
		tr.remove();
	});
	$(document).on('click', '.add-row', function(event) {
		var table_id = '#productivity';
		var headers = get_list_header('#productivity');
		var tr = $(table_id).find('tr');
		var max_hours = []
		tr.each(function() {
			var td = $(this).find('td');
			var sum_td = td.length;
			var tmp = [];
			if (sum_td) {
				var tmp_data = [];
				td.each(function() {
					var max_h = $(this).data('target');
					tmp.push(max_h);
				});
				if (! max_hours.length) {
					max_hours = tmp;
				}
			}
		});
		var tr2 = $(this).closest('tr');
		var td2 = tr2[0].cells;
		var sum_col = td2.length;
		var ctn = `<tr><td ><a><i class="fas fa-plus-circle add-row"></i></a></td>
			<td ><a><i class="fas fa-minus-circle remove-row"></i></a></td>`;
			for (var idx = 2; idx < sum_col; idx++) {
				ctn += '<td contenteditable="true" data-target="' + max_hours[idx] + '"></td>'
			}
		ctn += `</tr>`;
			
		tr2.after(ctn);
	});
});
function toggleDropdown() {
  document.getElementById("dropd_ctn").classList.toggle("show");
}
window.onclick = function(event) {
	var parent_elm = document.getElementById("drp_div");
    var child_elm = event.target;
    var contain = parent_elm.contains(child_elm);
  if (! contain) {
    var dropdowns = document.getElementsByClassName("dropdown-content");
    for (var i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}

$(document).ready(function () {
	$('#timesheet_form').submit(function(event) {
		event.preventDefault();
		var up_file = upload_file('#timesheet_form');
		$('#overlay_loader').show();
		if (up_file != null && up_file[0] == 1) {
			var file_name	= $('#excel').get(0).files[0].name;
			var submit = get_form_submit('#timesheet_form');
			var from_date 	= submit['from_date'];
			var to_date 	= submit['to_date'];
			var data = {}
			data['file_name'] = file_name;
			data[SESSION_FROM] = from_date;
			data[SESSION_TO] = to_date;
			$.ajax({
			   url: IMPORT_PRODUCTIVITY,
			   type: "POST",
			   data: encodeURIComponent(JSON.stringify(data)),
			   success: function(resp){
				   var result = resp.result;
					if (result[0]) {
						var ctn = '';
						for (var idx = 0 ; idx < result[1].length; idx++) {
							ctn += `<td ><a><i class="fas fa-plus-circle add-row"></i></a></td>
								<td ><a><i class="fas fa-minus-circle remove-row"></i></a></td>`;
							for (var idx2=0; idx2 < result[1][idx].length; idx2++) {
								var hour = result[1][idx][idx2][0];
								var std_hour = result[1][idx][idx2][1];
								ctn += '<td contenteditable="true" data-target="' + std_hour + '">' + hour + '</td>'
							}
							ctn += '</tr>';
						}
						var tbody = document.getElementById("pr_body");
						if ($('#overwite').prop('checked')) {
							tbody.innerHTML = '';
						}
						tbody.innerHTML += ctn;
						$('#overlay_loader').hide();
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

function export_productivity () {
	$('#notify').hide();
	$('#overlay_loader').show();
	var table_info = get_data_productivity();
	var headers = table_info[0];
	var row_data = table_info[1];
	var  max_hours = table_info[2];
	var data = {};
	data['headers'] = headers;
	data['data'] = row_data;
    $.ajax({
	   url: EXPORT_PRODUCTIVITY,
	   type: "POST",
	   data: encodeURIComponent(JSON.stringify(data)),
	   success: function(resp){
		   var result = resp.result;
			if (result[0]) {
					var file_name = result[1];
					var data2 = {}
					data2[SESSION_FILE_NAME] = file_name;
					var method_url = encodeURIComponent(JSON.stringify(data2));
					var link = DOWNLOAD_FILE + '?' + method_url;
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