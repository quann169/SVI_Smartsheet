from pprint import pprint
from decimal import Decimal
timesheet_info = {'CAD_Operation_Support': {'resource': {'Nguyen Vo': {'eng_type': 'Jr. '
                                                                  'Engineer',
                                                      'team': 'CAD',
                                                      'timesheet': {'2021-08-02': {'href': '/detail-timesheet?%7B%27from%27%3A%20%272021-08-02%27%2C%20%27to%27%3A%20%272021-08-06%27%2C%20%27filter%27%3A%20%27weekly%27%2C%20%27task_filter%27%3A%20%27both%27%2C%20%27sheets%27%3A%20%5B5%5D%2C%20%27users%27%3A%20%5B%27Nguyen%20Vo%27%5D%2C%20%27granted_list%27%3A%20%27%27%2C%20%27cost%27%3A%20%27normal%27%2C%20%27mode%27%3A%20%27view%27%7D',
                                                                                   'max_hour': 40,
                                                                                   'work_hour': Decimal('40')},
                                                                    '2021-08-09': {'href': '/detail-timesheet?%7B%27from%27%3A%20%272021-08-09%27%2C%20%27to%27%3A%20%272021-08-13%27%2C%20%27filter%27%3A%20%27weekly%27%2C%20%27task_filter%27%3A%20%27both%27%2C%20%27sheets%27%3A%20%5B5%5D%2C%20%27users%27%3A%20%5B%27Nguyen%20Vo%27%5D%2C%20%27granted_list%27%3A%20%27%27%2C%20%27cost%27%3A%20%27normal%27%2C%20%27mode%27%3A%20%27view%27%7D',
                                                                                   'max_hour': 40,
                                                                                   'work_hour': Decimal('40')}},
                                                      'total': 0,
                                                      'user_id': 136},
                                        'Toan Nguyen': {'eng_type': 'Jr. '
                                                                    'Engineer',
                                                        'team': 'CAD',
                                                        'timesheet': {'2021-08-02': {'href': '/detail-timesheet?%7B%27from%27%3A%20%272021-08-02%27%2C%20%27to%27%3A%20%272021-08-06%27%2C%20%27filter%27%3A%20%27weekly%27%2C%20%27task_filter%27%3A%20%27both%27%2C%20%27sheets%27%3A%20%5B5%5D%2C%20%27users%27%3A%20%5B%27Toan%20Nguyen%27%5D%2C%20%27granted_list%27%3A%20%27%27%2C%20%27cost%27%3A%20%27normal%27%2C%20%27mode%27%3A%20%27view%27%7D',
                                                                                     'max_hour': 40,
                                                                                     'work_hour': Decimal('40')},
                                                                      '2021-08-09': {'href': '/detail-timesheet?%7B%27from%27%3A%20%272021-08-09%27%2C%20%27to%27%3A%20%272021-08-13%27%2C%20%27filter%27%3A%20%27weekly%27%2C%20%27task_filter%27%3A%20%27both%27%2C%20%27sheets%27%3A%20%5B5%5D%2C%20%27users%27%3A%20%5B%27Toan%20Nguyen%27%5D%2C%20%27granted_list%27%3A%20%27%27%2C%20%27cost%27%3A%20%27normal%27%2C%20%27mode%27%3A%20%27view%27%7D',
                                                                                     'max_hour': 40,
                                                                                     'work_hour': Decimal('8')}},
                                                        'total': 0,
                                                        'user_id': 134}},
                           'sheet_id': 5,
                           'sheet_type': 'NRE',
                           'total': {'2021-08-02': 0, '2021-08-09': 0},
                           'total_row': 0},
 'QCS_Project': {'resource': {'Toan Nguyen': {'eng_type': 'Jr. Engineer',
                                              'team': 'CAD',
                                              'timesheet': {'2021-08-02': {'href': '',
                                                                           'max_hour': 40,
                                                                           'work_hour': 0},
                                                            '2021-08-09': {'href': '/detail-timesheet?%7B%27from%27%3A%20%272021-08-09%27%2C%20%27to%27%3A%20%272021-08-13%27%2C%20%27filter%27%3A%20%27weekly%27%2C%20%27task_filter%27%3A%20%27both%27%2C%20%27sheets%27%3A%20%5B18%5D%2C%20%27users%27%3A%20%5B%27Toan%20Nguyen%27%5D%2C%20%27granted_list%27%3A%20%27%27%2C%20%27cost%27%3A%20%27normal%27%2C%20%27mode%27%3A%20%27view%27%7D',
                                                                           'max_hour': 40,
                                                                           'work_hour': Decimal('32')}},
                                              'total': 0,
                                              'user_id': 134}},
                 'sheet_id': 18,
                 'sheet_type': 'NRE',
                 'total': {'2021-08-02': 0, '2021-08-09': 0},
                 'total_row': 0}}

timeoff_info = {
        'Toan Nguyen': {'2021-08-02': 8, '2021-08-09': 4},
    }
# group timesheet by resource to calculate cost
timesheet_by_resource = {}
for sheet_name, sheet_data in timesheet_info.items():
    if sheet_data.get('resource'):
        for resource, resource_data in sheet_data['resource'].items():
            if resource_data.get('timesheet'):
                for col_name, col_data in resource_data['timesheet'].items():
                    max_hour = col_data['max_hour']
                    work_hour = col_data['work_hour']
                    if not timesheet_by_resource.get(resource):
                        timesheet_by_resource[resource] = {}
                    resource_data_2 = timesheet_by_resource[resource]
                    if not resource_data_2.get(col_name):
                        timeoff = 0
                        if timeoff_info.get(resource) and timeoff_info[resource].get(col_name):
                            timeoff = timeoff_info[resource].get(col_name)
                        resource_data_2[col_name] = {'sheets': [],
                                                     'max_hour': max_hour,
                                                     'work_hour': [],
                                                     'timeoff': timeoff}
                    col_data_2 = resource_data_2[col_name]
                    col_data_2['sheets'].append(sheet_name)
                    col_data_2['work_hour'].append(work_hour)
#calculate cost and update the input data
for resource, resource_data_3 in timesheet_by_resource.items():
    for col_name, col_data_3 in resource_data_3.items():
        sheets = col_data_3['sheets']
        timeoff = col_data_3['timeoff']
        work_hours = col_data_3['work_hour']
        max_hour = col_data_3['max_hour']
        sum_real_hour = sum(work_hours)
        total = timeoff + sum_real_hour
        if total > max_hour:
            standar_hour = max_hour - timeoff
            percent_number = standar_hour / sum_real_hour
            for idx in range(0, len(sheets)):
                sheet_name = sheets[idx]
                work_hour = work_hours[idx]
                cost = percent_number * work_hour
                timesheet_info[sheet_name]['resource'][resource]['timesheet'][col_name]['work_hour'] = cost

pprint(timesheet_info)     
                          