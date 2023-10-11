# import os
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
# new_text = ['toannguyen', 'thuytran', 'quannguyen', 'hongnguyen', 'vantran', 'minhvo', 'thuyptran', 'hanguyen']
# allow_users = '2374285119137596532370533582700611491069148536764788583422261336860047390616416134681523160828232659813870562139419161996001154735292621087325380971270110928436303081531274838619016283754398839264991930665370227548715495330485682315417495389'
# #
#
# #
# print(unhash(allow_users))
# print(hash(new_text))
#

l = [[1,2,3], [4,5,6], [7,8,9]]


u = [x for x in l if 5 in x]
print (u)



