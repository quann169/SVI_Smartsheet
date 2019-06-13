
class Header():
	TASK_NAME = "TaskName"
	DURATION = "Duration"
	START_DATE = "StartDate"
	END_DATE = "EndDate"
	ASSIGNED_TO = "AssignedTo"
	COMPLETE = "Complete"
	ALLOCATION = "Allocation"

class UserInfoConfig():
	RESOURCE = 'Resource'
	POSITION = 'Position'
	LIST_MAIL = 'Other Info'
	EXCLUDE = 'Exclude'
	SENIORITY_LEVEL = 'Seniority level'
	TYPE = 'Type'
	ROLE = 'Role'
	MANAGER_EMAIL = 'Manager (Mail)'
	IS_COUNT = 'is_count'
	MAIL = 'Mail'
	FULL_NAME = 'Full Name'	#row, colum to get info from Config.xlsx
	ROW_GET_STATUS_AND_START_END_DATE = 3
	ROW_GET_SHOW_DETAIL = 4
	ROW_GET_SHEET = 7
	ROW_GET_USER_INFO = 2
	COLUM_GET_STATUS = 1
	LIST_USER_SEND_MAIL = ['vantran', 'phuongtruong']
	
class GenSmartsheet():
	TOKEN = "nls2smz4rzdckgfp9pcem9sg8y"
# 	TOKEN = "4clk71azsyh16c21p48bb9cvfi"
	PARENT_ID = 'parent_id'
	SIBLING_ID = 'sibling_id'
	CELLS = "cells"
	VALUE = 'value'
	TITLE = 'title'
	ID = 'id'
	DISPLAY_VALUE = 'display_value'
	LINE = 'line'
	
	
class ListItemKey():
	I001 = "I001"
	I002 = "I002"
	I003 = "I003"
	I004 = "I004"
	
class DateTime():
	LIST_MONTH = {
		1 : 'Jan', 
		2 :'Feb', 
		3 : 'Mar', 
		4 : 'Apr', 
		5 : 'May', 
		6 : 'Jun', 
		7 :'Jul', 
		8 : 'Aug', 
		9: 'Sep', 
		10 : 'Oct', 
		11 : 'Nov', 
		12 : 'Dec'
		}
	LIST_WORK_DAY_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
	START_WEEK = 'Monday'
	
class WorkHourColor:
	IS_EQUAL = 'lime'
	IS_GREATER = 'orange'
	IS_LESS = 'tan'
	IS_HEADER = 'gray_ega'
	IS_USER_NAME = 'gray25'
	IS_SHEET_NAME = 'ice_blue'
	BACK_GROUND = 'white'
	IS_POSITION = 'light_turquoise'

class HeaderExcelAndKeys():
	SHEET_NAME = 'Project'
	USER_NAME = 'User Name'
	SENIORITY_POSITION = 'Seniority Position'
	TYPE = 'Type'
	ROLE = 'Role'
	TOTAL_MONTH = 'Total Month'
	TOTAL_WEEK = 'Total Week'
	START_ROW = 0
	START_COLUM = 0
 
 