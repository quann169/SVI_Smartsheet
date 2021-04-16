function draw_stack_column_chart(id, data, label_angle) {
	if (label_angle == undefined) {
		var label_angle = 0;
	}
	var title_text = data.title;
	var info = data.info;
	var column = data.column;
	var row_type = data.type;
	var chart_data = []
	var chart_type = 'stackedColumn';
	var color_maping = ['#5c9ad2', '#dc847c', '#ffd963', '#deccec', '#a367dc', '#a8d18d'];
	for (var i = 0; i < row_type.length; i++) {
		var temp = {
				type: chart_type,
				legendText: row_type[i],
				showInLegend: "true",
				color: color_maping[i], 
				indexLabel: "#percent",
				percentFormatString: "#",
				toolTipContent: "#percent%",
				dataPoints: []
			};
			
		for (var j = 0; j < column.length; j++) {
			
			temp['dataPoints'].push({ y: info[row_type[i]][column[j]]['value'] , label: column[j], x: info[row_type[i]][column[j]]['x']});
			
		}
		chart_data.push(temp);
	}
    var chart = new CanvasJS.Chart(id,
	{
		title:{
			text: title_text
		},
		axisY:{
           interval: 10,
		   //valueFormatString: ("#'%'") 
		 },
		axisX:{
	        labelAngle: label_angle,
			interval: 1,
	    	labelFormatter: function(e) {
		      	return e.label ? e.label : "";
		      }
	      },
		data: chart_data
	});
	chart.render();
}

function get_list_herder(id) {
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

function creat_productivity_data(row_data, headers, group_id, title) {
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
			var name = row_data[idx3][group_id].trim();
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
			if (! data[name].hasOwnProperty(header_1)  ) {
				data[name][header_1] = {'total': 0};
			}
			if (! data[name][header_1].hasOwnProperty(header_2)) {
				data[name][header_1][header_2] = 0;
			}
			data[name][header_1][header_2] += val_num;
			data[name][header_1]['total'] += val_num;
		}
	}
	
	// caculate percent
	for (var [group, value] of Object.entries(data)) {
		for (var [week, value2] of Object.entries(value)) {
			var total = value2['total'];
			for (var [type_name, value3] of Object.entries(value2)) {
				if (type_name != 'total') {
					var percent = value3 * 100 / total;
					data[group][week][type_name] = percent;
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
		for (var i = 0; i < list_group.length; i++){
			count += 1;
			var group = list_group[i];
			for (var idx6=0; idx6 < list_col.length; idx6++ ) {
				var week = list_col[idx6];
				var day = week.split('-')[1] + '-' + week.split('-')[2];
				var percent = data[group][week][type_name];
				out['info'][type_name][group + ' ' + day] = {'value': percent, 'x': count};
				count += 1;
				if (! list_col2.includes(group  + ' ' + day)) {
					list_col2.push(group + ' ' + day);
				}
			}
		}
	}
	out['column'] = list_col2;
	out['type'] = list_type;
	return out;	
	
}

$(document).ready(function() {
	$('#view_chart').click(function(){
		var table_id = '#productivity';
		var headers = get_list_herder('#productivity');
		var tr = $(table_id).find('tr');
		var row_data = [];
		tr.each(function() {
			var td = $(this).find('td');
			var sum_td = td.length;
			if (sum_td) {
				var tmp_data = [];
				td.each(function() {
					var value = $(this).html();
					tmp_data.push(value);
				});
				row_data.push(tmp_data)
			}
		});
		
		var content = `
		<div class='productivity-block' align='center'>
			<div class='productivity-taskbar' align='center' class='b-bottom '><b>Chart</b><a class='close-p' style='transform: translate(-165%, 0%) !important;' onclick='close_overlay();'><i class='fas fa-times '></i></a></div>
			<div class='productivity-ctn'>
				<div id="team_productivity" style="height: 400px; width: 100%;">
				</div><br>
				<div id="field_productivity" style="height: 400px; width: 100%;">
				</div><br>
				<div id="seniority_productivity" style="height: 400px; width: 50%;">
				</div><br>
				<div id="headcount" style="height: 400px; width: 30%;">
				</div>
			</div>
		</div>
		`
		$('#overlay').html(content);
		$('#overlay').show();
		
		
		var team_productivity = creat_productivity_data(row_data, headers, 2, 'Team Productivity');
		draw_stack_column_chart('team_productivity', team_productivity, 90);
		
		var field_productivity = creat_productivity_data(row_data, headers, 5, 'Field Productivity');
		draw_stack_column_chart('field_productivity', field_productivity, 90);
		
		var seniority_productivity = creat_productivity_data(row_data, headers, 4, 'Seniority Productivity');
		draw_stack_column_chart('seniority_productivity', seniority_productivity, 90);
		
		var headcount_productivity = creat_productivity_data(row_data, headers, -1, 'Headcount');
		draw_stack_column_chart('headcount', headcount_productivity, 0);
	})
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
	$(document).on('click', '.remove-row', function(event) {
		var tr = $(this).closest('tr');
		tr.remove();
	});
	$(document).on('click', '.add-row', function(event) {
		var tr = $(this).closest('tr');
		var td = tr[0].cells;
		var sum_col = td.length;
		var ctn = `<tr><td ><a><i class="fas fa-plus-circle add-row"></i></a></td>
			<td ><a><i class="fas fa-minus-circle remove-row"></i></a></td>`;
			for (var idx = 2; idx < sum_col; idx++) {
				ctn += '<td contenteditable="true"></td>'
			}
		ctn += `</tr>`;
			
		tr.after(ctn);
	});
});