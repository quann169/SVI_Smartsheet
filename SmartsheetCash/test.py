# import binascii
# def hash(text):
#     str_text = str(text)
#     result = int(binascii.hexlify(str_text.encode('utf8')), 16)
#     result = str(result)
#     return result
#
# def unhash(text):
#     result = binascii.unhexlify('%x' % int(text))
#     result = result.decode('ascii')
#     return result
# #
# # old_text = ['toannguyen', 'quannguyen', 'hongnguyen', 'vantran', 'minhvo', 'nhuanhoang']
# # allow_users = '96830833101318548532395723290332873809692487412203847445088478895661354285724309799547875163246469356368406995326312382724944222943541079277012308977880576460958747173394743809876109149'
# #
# # new_text = ['toannguyen', 'thuytran', 'quannguyen', 'hongnguyen', 'vantran', 'minhvo', 'nhuanhoang']
# # allow_users = '7671728981342872620210102993050997045886989800758580601983359963924811674517969346637467828156109367861642103384239310634773467909107489611364431888103697159970229775892790077774991004749374282128032063938797971293'
# #
# new_text = ['toannguyen', 'thuytran', 'quannguyen', 'hongnguyen', 'vantran', 'minhvo', 'thuyptran']
# allow_users = '29967691333370596172695714816605457210496053909213205476497499859081295603585817760302608703734802218209539466344684807167083859019951131294392312062905067031133710062081211241308558612309496846210271438697277277'
# #
#
# #
# print(unhash(allow_users))
# print(hash(new_text))
#
#
# # def convert_number_to_currency(input_number):
# #     if isinstance(input_number, float) or isinstance(input_number, int):
# #         result = "${:,.0f}".format(input_number)
# #     else:
# #         if not input_number:
# #             result = ''
# #         else:
# #             try:
# #                 result = result = "${:,.0f}".format(float(input_number))
# #             except:
# #                 result = ''
# #     return result
# #
# # print('ss ' + convert_number_to_currency(1000000))
# # print('ss ' + convert_number_to_currency(1000000.09))
# # print('ss ' + convert_number_to_currency('1000000'))
# # print('ss ' + convert_number_to_currency(''))
# # print('ss ' + convert_number_to_currency('1000000.09'))
from smartsheet import smartsheet, sheets, models
from pprint import pprint
token = 'P6fpGjQfIjRVBXUhbR0DC2D8BlkJ7uD7a2bkJ'#'nls2smz4rzdckgfp9pcem9sg8y'#'R7p3JRiczmi4UkG4NueZXty4gCa6uTw5e5e6Z'
smartsheet_obj = smartsheet.Smartsheet(token)
master_sheet_obj = sheets.Sheets(smartsheet_obj)
list_sheet = master_sheet_obj.list_sheets(include_all=True)

for sheet in list_sheet.data:
    print(sheet.name)
