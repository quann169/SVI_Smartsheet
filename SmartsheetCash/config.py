###################################################################################
###############################   COMMON CFG   ####################################
###################################################################################
token = 'nls2smz4rzdckgfp9pcem9sg8y'
allow_users = '29967691333370596172695714816605457210496053909213205476497499859081295603585817760302608703734802218209539466344684807167083859019951131294392312062905067031133710062081211241308558612309496846210271438697277277'
expired_time = 60*24#1 day

groups = [
    {#Group 1: index is 0
        'mapping_headers' : [#('src header', 'des header')
                ('Số chứng từ',  'Invoice No'),
                ('Diễn giải', 'Descriptions'),
                ('Chi', 'Payable (VND)'),
                ('Ngày thanh toán', 'Pay Date'),
                ('', 'Pay by'),
                ('', 'Supplier\'s code'),
        ],
        'source': {
            'sheet_name': 'Office Cash - DN/Hue',
            'headers': {
                'Ref ID':                   {}, 
                'Số chứng từ':              {'compare_index': 0, 'data_type': 'integer'}, 
                'Ngày HĐ':                  {}, 
                'Ngày thanh toán':          {'is_date': True, 'compare_index': 2, 'is_none_empty': True}, 
                'Diễn giải':                {'compare_index': 1, 'is_none_empty': True}, 
                'Thu':                      {'data_type': 'currency'}, 
                'Chi':                      {'is_none_empty': True,  'modified_index': 0 , 'data_type': 'currency'}, 
                'Tồn':                      {'data_type': 'currency'}, 
                'Loại HĐ':                  {}, 
                'Phân loại CP':             {}, 
                'Ngày UD nhận':             {}, 
                }
        },
        'destination': {
            'sheet_name': 'Copy of SVI 2022',
            'headers': {
                'ID':                       {}, 
                'Descriptions':             {'compare_index': 1,'is_none_empty': True}, 
                'Invoice No':               {'compare_index': 0, 'data_type': 'integer'}, 
                'Payment':                  {}, 
                'Supplier\'s code':         {'default_value': 'CASH'}, 
                'Amount on Invoice (VND)':  {'data_type': 'currency'}, 
                'Payable (VND)':            {'is_none_empty': True,  'modified_index': 0 , 'data_type': 'currency'}, 
                'Office Place':             {}, 
                'Pay Date':                 {'is_date': True,  'compare_index': 2, 'is_none_empty': True}, 
                'Invoice Date':             {}, 
                'Categories':               {}, 
                'Pay by':                   {'mapping_values': ['DN office cash', 'Hue office cash'], 'default_value': 'DN office cash'}, 
            }
            
        },   
    },
    
    

]


###################################################################################
###############################  Extent options ####################################
###################################################################################

recipient_mail = ['toannguyen@savarti.com']
cc_mail = ['toannguyen@savarti.com']
subject = 'Commit Office Cash'
