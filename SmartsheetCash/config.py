###################################################################################
###############################   COMMON CFG   ####################################
###################################################################################
token = 'nls2smz4rzdckgfp9pcem9sg8y'
allow_users = '2374285119137596532370533582700611491069148536764788583422261336860047390616416134681523160828232659813870562139419161996001154735292621087325380971270110928436303081531274838619016283754398839264991930665370227548715495330485682315417495389'
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
                'Số chứng từ':              {'compare_index': 0, 'data_type': 'integer'}, 
                'Ngày HĐ':                  {}, 
                'Ngày thanh toán':          {'is_date': True, 'compare_index': 2, 'is_none_empty': True}, 
                'Diễn giải':                {'compare_index': 1, 'is_none_empty': True}, 
                'Thu':                      {'data_type': 'currency'}, 
                'Chi':                      {'is_none_empty': True,  'modified_index': 0 , 'data_type': 'currency'}, 
                'Tồn':                      {'data_type': 'currency'}, 
                'Loại HĐ':                  {}, 
                'Phân loại CP':             {}, 
                }
        },
        'destination': {
            'sheet_name': 'Copy of SVI 2023',
            'headers': {
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
    {#Group 2: index is 1
        'mapping_headers' : [#('src header', 'des header')
                ('Số chứng từ',  'Invoice No'),
                ('Diễn giải', 'Descriptions'),
                ('Chi', 'Payable (VND)'),
                ('Ngày thanh toán', 'Pay Date'),
                ('', 'Pay by'),
                ('', 'Supplier\'s code'),
        ],
        'source': {
            'sheet_name': 'Office Cash - HCM',
            'headers': {
                'Số chứng từ':              {'compare_index': 0, 'data_type': 'integer'}, 
                'Ngày HĐ':                  {}, 
                'Ngày thanh toán':          {'is_date': True, 'compare_index': 2, 'is_none_empty': True}, 
                'Diễn giải':                {'compare_index': 1, 'is_none_empty': True}, 
                'Thu':                      {'data_type': 'currency'}, 
                'Chi':                      {'is_none_empty': True,  'modified_index': 0 , 'data_type': 'currency'}, 
                'Tồn':                      {'data_type': 'currency'}, 
                'Loại HĐ':                  {}, 
                'Phân loại CP':             {}, 
                }
        },
        'destination': {
            'sheet_name': 'Copy of SVI 2023',
            'headers': {
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
                'Pay by':                   {'mapping_values': ['SG office cash'], 'default_value': 'SG office cash'}, 
            }
            
        },   
    },

{#Group 3: index is 2
        'mapping_headers' : [#('src header', 'des header')
                ('Số chứng từ',  'Invoice No'),
                ('Diễn giải', 'Descriptions'),
                ('Chi', 'Payable (VND)'),
                ('Ngày thanh toán', 'Pay Date'),
                ('', 'Pay by'),
                ('', 'Supplier\'s code'),
        ('Nguồn chi', 'Nguồn chi'),
        ],
        'source': {
            'sheet_name': 'Cost of living - HCM',
            'headers': {
                'Số chứng từ':              {'compare_index': 0, 'data_type': 'integer'}, 
                'Ngày HĐ':                  {}, 
                'Ngày thanh toán':          {'is_date': True, 'compare_index': 2, 'is_none_empty': True}, 
                'Diễn giải':                {'compare_index': 1, 'is_none_empty': True}, 
                'Thu':                      {'data_type': 'currency'}, 
                'Chi':                      {'is_none_empty': True,  'modified_index': 0 , 'data_type': 'currency'}, 
                'Tồn':                      {'data_type': 'currency'}, 
                'Loại HĐ':                  {}, 
                'Phân loại CP':             {}, 
        'Nguồn chi':            {'compare_index': 3, 'is_none_empty': True},     
                }
        },
        'destination': {
            'sheet_name': 'Copy of SVI 2023',
            'headers': {
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
                'Pay by':                   {'mapping_values': ['SG office cash'], 'default_value': 'SG office cash'}, 
        'Nguồn chi':            {'compare_index': 3,'is_none_empty': True},    
            }
            
        },   
    },
{#Group 4: index is 3
        'mapping_headers' : [#('src header', 'des header')
                ('Số chứng từ',  'Invoice No'),
                ('Diễn giải', 'Descriptions'),
                ('Chi', 'Payable (VND)'),
                ('Ngày thanh toán', 'Pay Date'),
                ('', 'Pay by'),
                ('', 'Supplier\'s code'),
        ('Nguồn chi', 'Nguồn chi'),
        ],
        'source': {
            'sheet_name': 'Cost of living - DN',
            'headers': {
                'Số chứng từ':              {'compare_index': 0, 'data_type': 'integer'}, 
                'Ngày HĐ':                  {}, 
                'Ngày thanh toán':          {'is_date': True, 'compare_index': 2, 'is_none_empty': True}, 
                'Diễn giải':                {'compare_index': 1, 'is_none_empty': True}, 
                'Thu':                      {'data_type': 'currency'}, 
                'Chi':                      {'is_none_empty': True,  'modified_index': 0 , 'data_type': 'currency'}, 
                'Tồn':                      {'data_type': 'currency'}, 
                'Loại HĐ':                  {}, 
                'Phân loại CP':             {}, 
        'Nguồn chi':            {'compare_index': 3, 'is_none_empty': True},     
                }
        },
        'destination': {
            'sheet_name': 'Copy of SVI 2023',
            'headers': {
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
                'Pay by':                   {'mapping_values': ['Cost of living - DN'], 'default_value': 'Cost of living - DN'}, 
        'Nguồn chi':            {'compare_index': 3,'is_none_empty': True},    
            }
            
        },   
    },
{#Group 5: index is 4
        'mapping_headers' : [#('src header', 'des header')
                ('Số chứng từ',  'Invoice No'),
                ('Diễn giải', 'Descriptions'),
                ('Chi', 'Payable (VND)'),
                ('Ngày thanh toán', 'Pay Date'),
                ('', 'Pay by'),
                ('', 'Supplier\'s code'),
        ('Nguồn chi', 'Nguồn chi'),
        ],
        'source': {
            'sheet_name': 'Cost of living - Hue',
            'headers': {
                'Số chứng từ':              {'compare_index': 0, 'data_type': 'integer'}, 
                'Ngày HĐ':                  {}, 
                'Ngày thanh toán':          {'is_date': True, 'compare_index': 2, 'is_none_empty': True}, 
                'Diễn giải':                {'compare_index': 1, 'is_none_empty': True}, 
                'Thu':                      {'data_type': 'currency'}, 
                'Chi':                      {'is_none_empty': True,  'modified_index': 0 , 'data_type': 'currency'}, 
                'Tồn':                      {'data_type': 'currency'}, 
                'Loại HĐ':                  {}, 
                'Phân loại CP':             {}, 
        'Nguồn chi':            {'compare_index': 3, 'is_none_empty': True},     
                }
        },
        'destination': {
            'sheet_name': 'Copy of SVI 2023',
            'headers': {
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
                'Pay by':                   {'mapping_values': ['Cost of living - Hue'], 'default_value': 'Cost of living - Hue'}, 
        'Nguồn chi':            {'compare_index': 3,'is_none_empty': True},    
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
