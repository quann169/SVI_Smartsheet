import sys
sys.path.append('..')
from Enum import Enum
from pprint import pprint
class Row():
	
	#get all info of a row (dictionary)
	def getInfoInRow(cells, dictHeader, count):
		dictInfo  ={}
		index = 0
		for colum in cells:
			if index in dictHeader.keys():
				value = 'NaN'
				if (Enum.GenSmartsheet.DISPLAY_VALUE in colum) and not ('%' in colum[Enum.GenSmartsheet.DISPLAY_VALUE]):
					value = colum[Enum.GenSmartsheet.DISPLAY_VALUE]
				elif Enum.GenSmartsheet.VALUE in colum:
					value = colum[Enum.GenSmartsheet.VALUE]
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
	def getDataRow(row, dictHeader, count):
		info = {}
		info[Enum.GenSmartsheet.ID] = row[Enum.GenSmartsheet.ID]
		if Enum.GenSmartsheet.PARENT_ID in row:
			info[Enum.GenSmartsheet.PARENT_ID] = row[Enum.GenSmartsheet.PARENT_ID]
		else:
			info[Enum.GenSmartsheet.PARENT_ID] = ''
		
		if Enum.GenSmartsheet.SIBLING_ID in row:
			info[Enum.GenSmartsheet.SIBLING_ID] = row[Enum.GenSmartsheet.SIBLING_ID]
		else:
			info[Enum.GenSmartsheet.SIBLING_ID] = ''
		info['info'] = Row.getInfoInRow(row[Enum.GenSmartsheet.CELLS], dictHeader, count)
		return info
		
	#find empty row 
	def isRowEmpty(row):
		for i in row[Enum.GenSmartsheet.CELLS]:
# 			print(row, '----------------------------')
			if ('value' in i):
				if i[Enum.GenSmartsheet.VALUE] not in [True, False]:
					if str(i[Enum.GenSmartsheet.VALUE]).strip() != '':
						
						return 1
		return 0

		#get Id  by task name
		
	#get header name of sheet (order)
	def getHeaders(sheet_name, sheet, dictHeaderConfig):
		dictHeader = {}
		# listHeader = []
		Datacolums = sheet.columns
# 		pprint(Datacolums)
		index = 0
		# listIndex = []
		for title in Datacolums:
			headerName_ = title[Enum.GenSmartsheet.TITLE].replace('%', '')
			headerName = headerName_.strip()
			if headerName in dictHeaderConfig.values():
				for key, value in dictHeaderConfig.items():
					#remove % in header
					headerName1_ = value.replace('%', '')
					headerName1 = headerName1_.strip()
					if headerName1 == headerName:
						dictHeader[index] = key
						# listHeader.append(key)
						# listIndex.append(index)
				# print(listHeader, index)
				
			index = index + 1
		# return listHeader, listIndex
		return dictHeader
		
	#convert Dict info of row to string 
	def DictInfoToString(id, dictRows):
		st = ''
		info = dictRows[id]['info']
		for i in info.values():
			st = st + str(i) + ' - '
		return st
	
	#list parrent id
	def getParentId(dictRows):
		lists = []
		for row in dictRows:
			if (dictRows[row][Enum.GenSmartsheet.PARENT_ID] != '') and not (dictRows[row][Enum.GenSmartsheet.PARENT_ID] in lists) :
				lists.append(dictRows[row][Enum.GenSmartsheet.PARENT_ID])
		return lists
	
	
	
	
	
	
	
	
	