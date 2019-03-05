
class Header():
	TASK_NAME = "TaskName"
	DURATION = "Duration"
	START_DATE = "StartDate"
	END_DATE = "EndDate"
	ASSIGNED_TO = "AssignedTo"
	COMPLETE = "Complete"
	ALLOCATION = "Allocation"

class UserInfoConfig():
	POSITION = 'Position'
	LIST_MAIL = 'Other info'
	SENIORITY_LEVEL = 'Seniority level'
	
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
	IS_GREATER = 'gold'
	IS_LESS = 'coral'
	IS_HEADER = 'gray_ega'
	IS_USER_NAME = 'gray25'
	IS_SHEET_NAME = 'ice_blue'
	BACK_GROUND = 'white'
	IS_POSITION = 'light_turquoise'

class HeaderExcelAndKeys():
	SHEET_NAME = 'Sheet Name'
	USER_NAME = 'User Name'
	SENIORITY_POSITION = 'Seniority Position'
	TOTAL_MONTH = 'Total Month'
	TOTAL_WEEK = 'Total Week'
	START_ROW = 2
	START_COLUM = 2
 