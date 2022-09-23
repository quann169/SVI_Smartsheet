###################################################################################
###############################   COMMON CFG   ####################################
###################################################################################
token = 'nls2smz4rzdckgfp9pcem9sg8y'
allow_users = '96830833101318548532395723290332873809692487412203847445088478895661354285724309799547875163246469356368406995326312382724944222943541079277012308977880576460958747173394743809876109149'
expired_time = 60*24#1 day

#mapping header to update data from src to des sheet
mapping_headers = [#('src header', 'des header')
    ('Số chứng từ',  'Invoice No'),
    ('Diễn giải', 'Descriptions'),
    ('Chi', 'Payable (VND)'),
    ('Ngày thanh toán', 'Pay Date'),
    ]


###################################################################################
###############################  SRC SHEET CFG ####################################
###################################################################################
#Source Sheet CFG
src_sheets = ['Office Cash - DN/Hue']

src_headers = ['Ref ID', 'Số chứng từ', 'Ngày HĐ', 'Ngày thanh toán', 'Diễn giải', 'Thu', 'Chi', 'Tồn', 'Loại HĐ',
               'Phân loại CP', 'Ngày UD nhận']
src_date_header = 'Ngày thanh toán'
src_compare_headers = ['Số chứng từ', 'Diễn giải', 'Ngày thanh toán']

#rule to detect row is a data
src_empty_headers = ['Thu']#required header blank
src_none_empty_headers = ['Ngày thanh toán', 'Chi', 'Diễn giải']#required header none blank


#headers check modified
src_check_modified_headers = ['Chi']


###################################################################################
###############################  DES SHEET CFG ####################################
###################################################################################

des_sheets = 'Copy of SVI 2022'
des_headers = ['ID', 'Descriptions', 'Invoice No', 'Payment', 'Supplier\'s code', 
               'Amount on Invoice (VND)', 'Payable (VND)', 
               'Office Place', 'Pay Date', 'Invoice Date', 'Categories', 'Pay by']
des_date_header = 'Pay Date'

des_compare_headers = ['Invoice No', 'Descriptions', 'Pay Date']

#rule to detect row is a data
des_empty_headers = []#required header blank
des_none_empty_headers = ['Pay Date', 'Payable (VND)', 'Descriptions']#required header none blank


#Config to detect data of des sheet should be compare with src sheet 

des_mapping_src_sheet = {
    'Pay by': {'DN office cash': 'Office Cash - DN/Hue',
               'Hue office cash': 'Office Cash - DN/Hue',
               'SG office cash': 'Office Cash - SG',
               },
    
    }#'header name': {'value1': 'src sheet name'}


#headers check modified
des_check_modified_headers = ['Payable (VND)']




###################################################################################
###############################  Extent options ####################################
###################################################################################

#skip feature 'remove all attachments of destination row before add attachments'
skip_remove_attachments = False
recipient_mail = ['toannguyen@savarti.com']
cc_mail = ['nhuanhoang@savarti.com']
subject = 'Commit Office Cash'
