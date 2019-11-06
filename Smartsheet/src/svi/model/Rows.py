import sys
# sys.path.append('..')
from svi.enum import Enum
from pprint import pprint
from decimal import Decimal
class Row():
	def __init__(self):
		pass
	#get all info of a row (dictionary)
	def getInfoInRow(self, cells, dictHeader, count):
		dictInfo  ={}
		index = 0
		for colum in cells:
			if index in dictHeader.keys():
				value = 'NaN'
				
# 				print (dictHeader[index], colum.display_value, colum.value)
				if (colum.display_value != None) and not ('%' in colum.display_value):
					value = colum.display_value
				elif (colum.display_value != None) and ('%' in colum.display_value) and dictHeader[index] == 'Allocation':
					numStr_ = colum.display_value.strip()
					numStr = numStr_.replace('%', '')
					try:
						value = Decimal(numStr)/100
					except:
						print ("Invalid format data: Header %s value %s"%(dictHeader[index], colum.display_value))
						value = 0
# 					print (numStr_, value)
				elif colum.value != None:
					if not ('%' in str(colum.value)):
						value = colum.value
					elif ('%' in colum.value) and dictHeader[index] == 'Allocation':
						numStr_2 = colum.value.strip()
						numStr2 = numStr_2.replace('%', '')
						try:
							value = Decimal(numStr2)/100
						except:
							print ("Invalid format data: Header %s value %s"%(dictHeader[index], colum.value))
							value = 0
					else:
						value = colum.value
# 				print (dictHeader[index], colum.value, colum.display_value, value)
# 				if dictHeader[index] == 'Allocation':
# 					print (value, colum.display_value, colum.value, 'ssss')
				if value == '':
					value = 'NaN'
				dictInfo[dictHeader[index]] = value
# 				if 'Allocation' == dictHeader[index]:
# 					print(dictInfo[dictHeader[index]], colum, value)
			index = index + 1
		dictInfo['line'] = count
# 		pprint(dictInfo)
		return dictInfo
		
	#get all info of all row (dictionary)
	def getDataRow(self, row, dictHeader, count):
		info = {}
		info[Enum.GenSmartsheet.ID] = row.id

		if row.parent_id != None:
			info[Enum.GenSmartsheet.PARENT_ID] = row.parent_id
		else:
			info[Enum.GenSmartsheet.PARENT_ID] = ''
		
		if row.sibling_id:
			info[Enum.GenSmartsheet.SIBLING_ID] = row.sibling_id
		else:
			info[Enum.GenSmartsheet.SIBLING_ID] = ''
		info['info'] = self.getInfoInRow(row.cells, dictHeader, count)
		
		return info
		
	#find empty row 
	def isRowEmpty(self, row):
		for i in row[Enum.GenSmartsheet.CELLS]:
# 			print(row, '----------------------------')
			if ('value' in i):
				if i[Enum.GenSmartsheet.VALUE] not in [True, False]:
					if str(i[Enum.GenSmartsheet.VALUE]).strip() != '':
						
						return 1
		return 0

		#get Id  by task name
		
	#get header name of sheet (order)
	def getHeaders(self, sheet_name, sheet, dictHeaderConfig):
		dictHeader = {}
		# listHeader = []
		Datacolums = sheet.columns
# 		pprint(Datacolums)
		index = 0
		# listIndex = []
		for title in Datacolums:
			headerName_ = title.title.replace('%', '')
			headerName = headerName_.strip()
			if headerName in dictHeaderConfig.values():
				for key, value in dictHeaderConfig.items():
					#remove % in header
					headerName1_ = value.replace('%', '')
					headerName1 = headerName1_.strip()
					if headerName1 == headerName:
						if key in dictHeader.values():
							print ('Duplicate colum %s in sheet name %s'%(key, sheet_name))
							sys.exit()
						else:
							dictHeader[index] = key
						# listHeader.append(key)
						# listIndex.append(index)
				# print(listHeader, index)
				
			index = index + 1
		# return listHeader, listIndex
		return dictHeader
		
	#convert Dict info of row to string 
	def DictInfoToString(self, id, dictRows):
		st = ''
		info = dictRows[id]['info']
		for i in info.values():
			st = st + str(i) + ' - '
		return st
	
	#list parrent id
	def getParentId(self, dictRows):
		lists = []
		for row in dictRows:
			if (dictRows[row][Enum.GenSmartsheet.PARENT_ID] != '') and not (dictRows[row][Enum.GenSmartsheet.PARENT_ID] in lists) :
				lists.append(dictRows[row][Enum.GenSmartsheet.PARENT_ID])
		return lists
	
	
	
	
	
	
	
	
	