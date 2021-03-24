'''
Created on Feb 22, 2021

@author: toannguyen
'''

class MsgError:
    E001    = "Other Date time format: {}"
    E002    = "No sheet name '{}' on smartsheet"
    E003    = "Missing parameter"


class MsgWarning:
    W001    = 'Skip ID duplicate id :{}'


class Msg:
    M001    = 'Import successfully'
    M002    = 'Get data successfully'
    M003    = 'Add to final task successfully'

class AnalyzeItem:
    A001 = 'No resource missing working hours' 
    A002 = 'No resource redundant working hours' 
    A003 = 'All resource enough working hours' 
    A004 = 'Resource overlap working hours'
    A005 = 'No conflict with final date'  
    A006 = 'Continuity with final date' 