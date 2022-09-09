'''
Created on Feb 22, 2021

@author: toannguyen
'''

class MsgError:
    E001    = "Other Date time format: {}"
    E002    = "No sheet name '{}' on smartsheet"
    E003    = "Missing parameter"
    E004    = "Incorrect username or password"
    E005    = "You don't have permission to access"
    

class MsgWarning:
    W001    = 'Skip ID duplicate id :{}'
    W002    = "Can not found <span class='bold cl-orange'>'{}'</span> in list resource" 

class Msg:
    M001    = 'Import successfully'
    M002    = 'Get data successfully'
    M003    = 'Add to final task successfully'
    

class AnalyzeItem:
    A001 = 'No. resource lack of working hours' 
    A002 = 'No. resource have redundant working hours' 
    A003 = 'No. resource have enough working hours' 
    A004 = 'No conflict with final date'  
    A005 = 'Continuity with final date'
    A006 = 'No. resource in project have enough task' 
    A007 = 'No. tasks are not mapping with resource' 