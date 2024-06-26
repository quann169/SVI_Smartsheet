'''
Created on Feb 22, 2021

@author: toannguyen
'''
from src.models.database.connection_model import Connection
from src.commons.enums import DbHeader, DbTable
from pprint import pprint
from src.commons.utils import get_work_days, split_patern, round_num, convert_date_to_string, \
                                get_start_week_of_date, get_month_name_of_date


class Configuration(Connection):
    def __init__(self):
        Connection.__init__(self)
        self.users              = {}
        self.others_name         = {}
        self.users_full_name    = {}
        self.user_ids           = {}
        self.user_email           = {}
        self.sheets             = {}
        self.sheet_ids          = {}
        self.holidays           = []
        self.time_off           = {}
        self.sheet_type         = {}
        self.sheet_type_ids     = {}
        self.eng_type           = {}
        self.eng_type_ids       = {}
        self.eng_level          = {}
        self.eng_level_ids      = {}
        self.team               = {}
        self.team_ids           = {}
        self.sheet_user         = {}
        self.sheet_user2        = {}
        self.sheet_user3        = {}
        self.type_and_sheet_info = {}
        self.granted            = {}
     
    def get_sheet_config(self, list_sheet_id=None, is_parse=False, is_active=True):
        condition = ''
        if list_sheet_id:
            condition   = 'WHERE `%s`.`%s` IN (%s)'%(DbTable.SHEET, DbHeader.SHEET_ID, ', '.join(list_sheet_id))
        if is_active == True:
            if not len(condition):
                condition   = 'WHERE `%s`="1"'%(DbHeader.IS_ACTIVE)
            else:
                condition   += ' AND `%s`="1"'%(DbHeader.IS_ACTIVE)
        elif is_active == False:
            if not len(condition):
                condition   = 'WHERE `%s`="0"'%(DbHeader.IS_ACTIVE)
            else:
                condition   += ' AND `%s`="0"'%(DbHeader.IS_ACTIVE)
        
        query = """
                SELECT `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`
                FROM `%s`
                INNER JOIN `%s`
                ON `%s`.`%s`=`%s`.`%s`
                %s
                ORDER BY `%s` ASC;
        """%(
            DbTable.SHEET, DbHeader.IS_VALID, 
            DbTable.SHEET, DbHeader.SHEET_ID, 
            DbTable.SHEET, DbHeader.IS_ACTIVE, 
            DbTable.SHEET, DbHeader.SHEET_NAME, 
            DbTable.SHEET, DbHeader.LATEST_MODIFIED, 
            DbTable.SHEET_TYPE, DbHeader.SHEET_TYPE,
            DbTable.SHEET, DbHeader.UPDATED_BY,
            DbTable.SHEET, DbHeader.UPDATED_DATE,
            DbTable.SHEET, DbHeader.PARSED_DATE,
            DbTable.SHEET, 
            DbTable.SHEET_TYPE, 
            DbTable.SHEET, DbHeader.SHEET_TYPE_ID, DbTable.SHEET_TYPE, DbHeader.SHEET_TYPE_ID,
            condition, DbHeader.SHEET_NAME
            )
        
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            if is_parse:
                for row in query_result:
                    self.sheet_ids[row[DbHeader.SHEET_ID]] = {\
                        DbHeader.SHEET_ID                       : row[DbHeader.SHEET_ID],
                        DbHeader.SHEET_NAME                     : row[DbHeader.SHEET_NAME],
                        DbHeader.LATEST_MODIFIED                : row[DbHeader.LATEST_MODIFIED],
                        DbHeader.SHEET_TYPE                     : row[DbHeader.SHEET_TYPE],
                        DbHeader.PARSED_DATE                    : row[DbHeader.PARSED_DATE],
                        DbHeader.IS_ACTIVE                      : row[DbHeader.IS_ACTIVE],
                        DbHeader.IS_VALID                       : row[DbHeader.IS_VALID]
                        }
                    self.sheets[row[DbHeader.SHEET_NAME]] = {\
                        DbHeader.SHEET_ID                       : row[DbHeader.SHEET_ID],
                        DbHeader.SHEET_NAME                     : row[DbHeader.SHEET_NAME],
                        DbHeader.LATEST_MODIFIED                : row[DbHeader.LATEST_MODIFIED],
                        DbHeader.SHEET_TYPE                     : row[DbHeader.SHEET_TYPE],
                        DbHeader.PARSED_DATE                    : row[DbHeader.PARSED_DATE],
                        DbHeader.IS_ACTIVE                      : row[DbHeader.IS_ACTIVE],
                        DbHeader.IS_VALID                       : row[DbHeader.IS_VALID]
                        }
                    if not self.type_and_sheet_info.get(row[DbHeader.SHEET_TYPE]):
                        self.type_and_sheet_info[row[DbHeader.SHEET_TYPE]] =  {}
                    self.type_and_sheet_info[row[DbHeader.SHEET_TYPE]][row[DbHeader.SHEET_NAME]] = {}
            return query_result
        else:
            return result
    
    def get_sheet_type_info(self, is_parse=False, is_active=False):
        condition   = ''
        # if is_active:
        # condition   = 'WHERE `%s`="1"'%(DbHeader.IS_ACTIVE)
        query = """
                SELECT `%s`, `%s`
                FROM `%s` %s;
        """%(
            DbHeader.SHEET_TYPE_ID, DbHeader.SHEET_TYPE,
            DbTable.SHEET_TYPE, condition
            )
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            if is_parse:
                for row in query_result:
                    sheet_type_id   = row[DbHeader.SHEET_TYPE_ID]
                    sheet_type_name = row[DbHeader.SHEET_TYPE]
                    self.sheet_type[sheet_type_name] = sheet_type_id
                    self.sheet_type_ids[sheet_type_id] = sheet_type_name
            return query_result
        else:
            return result
    
    def get_sheet_user_info(self):
        query = """
                SELECT `%s`.`%s`, 
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`
                FROM `%s` 
                INNER JOIN `%s`
                ON `%s`.`%s`=`%s`.`%s`
                INNER JOIN `%s`
                ON `%s`.`%s`=`%s`.`%s`;
        """%(
            DbTable.SHEET, DbHeader.SHEET_NAME,
            DbTable.PROJECT_USER, DbHeader.SHEET_ID,
            DbTable.PROJECT_USER, DbHeader.USER_ID,
            DbTable.USER, DbHeader.USER_NAME,
            DbTable.PROJECT_USER,
            DbTable.SHEET,
            DbTable.SHEET, DbHeader.SHEET_ID, DbTable.PROJECT_USER, DbHeader.SHEET_ID,
            DbTable.USER,
            DbTable.USER, DbHeader.USER_ID, DbTable.PROJECT_USER, DbHeader.USER_ID,
            )
        query_result    = self.db_query(query)
        
        if query_result:
            for row in query_result:
                sheet_id    = row[DbHeader.SHEET_ID]
                user_id     = row[DbHeader.USER_ID]
                user_name     = row[DbHeader.USER_NAME]
                if not self.sheet_user.get(sheet_id):
                    self.sheet_user[sheet_id] = []
                self.sheet_user[sheet_id].append(user_id)
                
                if not self.sheet_user2.get(sheet_id):
                    self.sheet_user2[sheet_id] = []
                self.sheet_user2[sheet_id].append(user_name)
                
                if not self.sheet_user3.get(user_id):
                    self.sheet_user3[user_id] = []
                self.sheet_user3[user_id].append(sheet_id)
                
    def add_sheet(self):
        query   = """INSERT INTO `%s` (`%s`, `%s`, `%s`, `%s`, `%s`, `%s`) VALUES ("%s", "%s", "%s", "%s", "%s", "%s");
        """%(DbTable.SHEET, DbHeader.SHEET_TYPE_ID, DbHeader.SHEET_NAME, DbHeader.LATEST_MODIFIED, \
             DbHeader.UPDATED_BY, DbHeader.IS_ACTIVE, DbHeader.IS_VALID,\
             self.sheet_type_id, self.sheet_name, self.latest_modified, self.updated_by, self.is_active, self.is_valid
             )
        self.db_execute(query)
    
    def is_exist_sheet(self):
        query   = """SELECT `%s` FROM `%s` WHERE `%s`="%s";
        """%( DbHeader.SHEET_ID, DbTable.SHEET, DbHeader.SHEET_NAME, self.sheet_name)
        query_result    = self.db_query(query)
        if query_result:
            return True
        else:
            return False
    
    def update_sheet(self, ):
        query   = """UPDATE `%s` SET `%s`="%s", `%s`="%s", `%s`="%s", `%s`="%s"  WHERE `%s`="%s";
        """%( DbTable.SHEET, DbHeader.SHEET_TYPE_ID, self.sheet_type_id, DbHeader.UPDATED_BY, self.updated_by, \
              DbHeader.IS_VALID, self.is_valid, \
              DbHeader.IS_ACTIVE, self.is_active, DbHeader.SHEET_NAME, self.sheet_name)
        self.db_execute(query)
    
    def update_sheet_active(self, ):
        query   = """UPDATE `%s` SET `%s`="%s", `%s`="%s"  WHERE `%s`="%s";
        """%( DbTable.SHEET, DbHeader.UPDATED_BY, self.updated_by, DbHeader.IS_ACTIVE, self.is_active, DbHeader.SHEET_ID, self.sheet_id)
        self.db_execute(query)
    
    def update_type_of_sheet(self, ):
        query   = """UPDATE `%s` SET `%s`="%s", `%s`="%s"  WHERE `%s`="%s";
        """%( DbTable.SHEET, DbHeader.UPDATED_BY, self.updated_by, DbHeader.SHEET_TYPE_ID, self.sheet_type_id, DbHeader.SHEET_ID, self.sheet_id)
        self.db_execute(query)
    
    def inactive_all_sheet(self, ):
        query   = """UPDATE `%s` SET `%s`="0";
        """%( DbTable.SHEET, DbHeader.IS_ACTIVE)
        self.db_execute(query)
       
    def update_latest_modified_of_sheet(self):
        query   = '''UPDATE 
                        `%s` 
                    SET 
                        `%s`="%s"
                    WHERE 
                        `%s`="%d";'''%(\
                    DbTable.SHEET,\
                    DbHeader.LATEST_MODIFIED, self.latest_modified, \
                    DbHeader.SHEET_ID, self.sheet_id)
        self.db_execute(query)
    
    def update_parsed_date_of_sheet(self):
        query   = '''UPDATE 
                        `%s` 
                    SET 
                        `%s`="%s"
                    WHERE 
                        `%s`="%d";'''%(\
                    DbTable.SHEET,\
                    DbHeader.PARSED_DATE, self.parsed_date, \
                    DbHeader.SHEET_ID, self.sheet_id)
        self.db_execute(query)
        
    def get_all_user_information(self):
        query   = """
                SELECT
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`
                FROM
                    `%s`; 
        """%(
            DbHeader.USER_ID,
            DbHeader.USER_NAME,
            DbHeader.FULL_NAME,
            DbHeader.EMAIL,
            DbHeader.OTHER_NAME,
            DbHeader.IS_ACTIVE,
            DbHeader.UPDATED_BY,
            DbHeader.UPDATED_DATE,
            DbHeader.ENG_LEVEL_ID,
            DbHeader.ENG_TYPE_ID,
            DbHeader.TEAM_ID,
            DbHeader.LEADER_ID,
            DbTable.USER,
            )
        query_result    = self.db_query(query)
        if query_result:
            for row in query_result:
                user_obj    = DbUsers(row)
                self.users[user_obj.user_name] = user_obj
                self.users_full_name[user_obj.full_name] = user_obj
                self.user_ids[user_obj.user_id] = user_obj
                self.user_email[user_obj.email] = user_obj
                for name in user_obj.other_name:
                    name = name.strip()
                    if name:
                        self.others_name[name] = user_obj.user_id
        else:
            pass
    
    def get_user_by_email(self, email):
        query = """
                SELECT `%s`, `%s`, `%s`, `%s`
                FROM `%s`
                WHERE `%s`="%s";
        """%(
            DbHeader.USER_ID, DbHeader.USER_NAME, DbHeader.FULL_NAME, DbHeader.OTHER_NAME,
            DbTable.USER, DbHeader.EMAIL, email
            )
        query_result    = self.db_query(query)
        result          = (None, None)
        if query_result:
            result = (query_result[0][DbHeader.USER_ID], query_result[0][DbHeader.USER_NAME])
        return result
    
    def get_role_by_user_id(self, user_id):
        query = """SELECT `%s`.`%s` FROM `%s` INNER JOIN `%s` on `%s`.`%s`=`%s`.`%s` WHERE `%s`.`%s`="%s";"""%(
            DbTable.ROLE, DbHeader.ROLE_NAME, DbTable.ROLE, DbTable.USER_ROLE, DbTable.ROLE, DbHeader.ROLE_ID, \
            DbTable.USER_ROLE, DbHeader.ROLE_ID, DbTable.USER_ROLE, DbHeader.USER_ID, str(user_id)
            )
        query_result    = self.db_query(query)
        result = None
        list_role = []
        if query_result:
            result = query_result[0][DbHeader.ROLE_NAME]
            for row in query_result:
                list_role.append(row[DbHeader.ROLE_NAME])
        return result, list_role
    
    def get_user_role(self):
        query = """SELECT `%s`.`%s`, `%s`.`%s`, `%s`.`%s`, `%s`.`%s` 
        FROM `%s` 
        INNER JOIN `%s` ON `%s`.`%s`=`%s`.`%s`
        INNER JOIN `%s` ON `%s`.`%s`=`%s`.`%s`;"""%(
            DbTable.ROLE, DbHeader.ROLE_NAME, DbTable.ROLE, DbHeader.ROLE_ID, 
            DbTable.USER, DbHeader.USER_NAME, DbTable.USER, DbHeader.USER_ID, 
            DbTable.USER_ROLE, DbTable.ROLE, 
            DbTable.ROLE, DbHeader.ROLE_ID, DbTable.USER_ROLE, DbHeader.ROLE_ID,
            DbTable.USER, 
            DbTable.USER, DbHeader.USER_ID, DbTable.USER_ROLE, DbHeader.USER_ID
            )
        query_result    = self.db_query(query)
        result = []
        if query_result:
            result = query_result
        return result
    
    def get_list_role(self):
        query = """SELECT `%s`, `%s` FROM `%s`;"""%(
             DbHeader.ROLE_NAME, DbHeader.ROLE_ID, DbTable.ROLE)
        query_result    = self.db_query(query)
        result = []
        if query_result:
            result = query_result
        return result
        
    
        
    def add_list_timeoff(self, list_record):
        query   = '''INSERT INTO `%s` 
                        (`%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`)
                    '''%(DbTable.TIME_OFF,\
                    DbHeader.TIME_OFF_ID, DbHeader.USER_ID, DbHeader.DEPARTMENT, DbHeader.TYPE, DbHeader.START_DATE, DbHeader.END_DATE, DbHeader.WORK_DAYS, DbHeader.STATUS, DbHeader.UPDATED_BY)
        query   += '''
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ;'''
        self.db_execute_many(query, list_record)
    
    def get_list_timeoff(self, is_parse=False, start_date=None, end_date=None):
        self.get_list_holiday(is_parse=True)
        condition   = ""
        if start_date != None and end_date != None:
            condition = '''WHERE `%s`>="%s" AND `%s`<="%s" 
                                OR `%s`>="%s" AND `%s`<="%s"
                                OR "%s">=`%s` AND "%s"<=`%s`
                                OR "%s">=`%s` AND "%s"<=`%s`'''%(
                                    DbHeader.START_DATE, start_date, DbHeader.START_DATE, end_date,
                                    DbHeader.END_DATE, start_date, DbHeader.END_DATE, end_date,
                                    start_date, DbHeader.START_DATE, end_date, DbHeader.START_DATE,
                                    start_date, DbHeader.END_DATE, end_date,  DbHeader.END_DATE
                                    )
        
        query = """
                SELECT `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`
                FROM `%s`
                INNER JOIN `%s`
                ON `%s`.`%s`=`%s`.`%s`
                %s 
                ORDER BY `%s`.`%s` DESC ;
        """%(
            DbTable.TIME_OFF, DbHeader.TIME_OFF_ID, 
            DbTable.USER, DbHeader.USER_NAME, 
            DbTable.USER, DbHeader.USER_ID, 
            DbTable.TIME_OFF, DbHeader.DEPARTMENT, 
            DbTable.TIME_OFF, DbHeader.TYPE,
            DbTable.TIME_OFF, DbHeader.START_DATE,
            DbTable.TIME_OFF, DbHeader.END_DATE,
            DbTable.TIME_OFF, DbHeader.WORK_DAYS,
            DbTable.TIME_OFF, DbHeader.STATUS,
            DbTable.TIME_OFF, 
            DbTable.USER, 
            DbTable.TIME_OFF, DbHeader.USER_ID, DbTable.USER, DbHeader.USER_ID,
            condition,
            DbTable.TIME_OFF, DbHeader.START_DATE
            )
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            if is_parse:
                for row in query_result:
                    timeoff_obj     = TimeOff(row, self.holidays)
                    try:
                        unuse   = self.time_off[timeoff_obj.user_id]
                    except KeyError:
                        self.time_off[timeoff_obj.user_id]  = []
                    
                    for date, week in timeoff_obj.dates:
                        self.time_off[timeoff_obj.user_id].append([date, week, timeoff_obj.timeoff_per_day, timeoff_obj])
            return query_result
        else:
            return result
    
    def get_list_holiday(self, is_parse=False):
        query = """
                SELECT `%s`
                FROM `%s`
                ORDER BY `%s` DESC;
        """%(
            DbHeader.DATE,
            DbTable.HOLIDAY,
            DbHeader.DATE
            )
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            if is_parse:
                for row in query_result:
                    if row[DbHeader.DATE]:
                        self.holidays.append(convert_date_to_string(row[DbHeader.DATE], format_str='%Y-%m-%d'))
            return query_result
        else:
            return result
    
    def get_list_granted(self, is_parse=False):
        query = """
                SELECT `%s`.`%s`, `%s`.`%s`, `%s`.`%s`, 
                    `%s`.`%s`, `%s`.`%s`, `%s`.`%s`, `%s`.`%s`
                FROM `%s`
                INNER JOIN `%s`
                ON `%s`.`%s`=`%s`.`%s`
                ORDER BY `%s`.`%s` DESC, `%s`.`%s` DESC;
        """%(
            DbTable.GRANTED_CONFIG, DbHeader.GRANTED_NAME,
            DbTable.GRANTED_CONFIG, DbHeader.GRANTED_CONFIG_ID,
            DbTable.GRANTED_CONFIG, DbHeader.GRANTED_NUMBER,
            DbTable.GRANTED_CONFIG, DbHeader.UPDATED_BY,
            DbTable.GRANTED_CONFIG, DbHeader.UPDATED_DATE,
            DbTable.SHEET, DbHeader.SHEET_NAME,
            DbTable.SHEET, DbHeader.SHEET_ID,
            DbTable.GRANTED_CONFIG,
            DbTable.SHEET,
            DbTable.GRANTED_CONFIG, DbHeader.SHEET_ID,
            DbTable.SHEET, DbHeader.SHEET_ID,
            DbTable.GRANTED_CONFIG, DbHeader.GRANTED_NAME,
            DbTable.SHEET, DbHeader.SHEET_NAME,
            )
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            if is_parse:
                for row in query_result:
                    sheet_name = row[DbHeader.SHEET_NAME]
                    config_id = row[DbHeader.GRANTED_CONFIG_ID]
                    sheet_id = row[DbHeader.SHEET_ID]
                    granted_name = row[DbHeader.GRANTED_NAME]
                    granted_number = row[DbHeader.GRANTED_NUMBER]
                    updated_date = row[DbHeader.UPDATED_DATE]
                    updated_by = row[DbHeader.UPDATED_BY]
                    if not self.granted.get(granted_name):
                        self.granted[granted_name] = {}
                    if not self.granted[granted_name].get(sheet_name):
                        self.granted[granted_name][sheet_name] = {}
                    self.granted[granted_name][sheet_name][DbHeader.GRANTED_NUMBER] = int(granted_number)
                    self.granted[granted_name][sheet_name][DbHeader.SHEET_ID] = sheet_id
                    self.granted[granted_name][sheet_name][DbHeader.UPDATED_BY] = updated_by
                    self.granted[granted_name][sheet_name][DbHeader.UPDATED_DATE] = updated_date
                    self.granted[granted_name][sheet_name][DbHeader.GRANTED_CONFIG_ID] = config_id
            return query_result
        else:
            return result
    
    def add_granted_config(self, list_record):
        query   = '''INSERT INTO `%s` 
                        (`%s`, `%s`, `%s`, `%s`)
                    '''%(DbTable.GRANTED_CONFIG,\
                    DbHeader.GRANTED_NAME, DbHeader.SHEET_ID, DbHeader.GRANTED_NUMBER, \
                    DbHeader.UPDATED_BY)
        query   += '''
                    VALUES
                        (%s, %s, %s, %s)
                    ;'''
        self.db_execute_many(query, list_record)
    
    def remove_granted_config_by_name(self, list_name):
        if len(list_name):
            query   = """DELETE FROM `%s` WHERE `%s` in %s;
            """%(DbTable.GRANTED_CONFIG, DbHeader.GRANTED_NAME, str(list_name))
            self.db_execute(query)
            
    def remove_all_timeoff_information(self):
        query   = '''DELETE FROM `%s`;'''%(\
                    DbTable.TIME_OFF
                    )
        self.db_execute(query)
    
    def add_holiday(self, date):
        query   = """INSERT INTO `%s` (`%s`) VALUES ("%s");
        """%(DbTable.HOLIDAY, DbHeader.DATE, date)
        self.db_execute(query)
    
    def is_exist_holiday(self, date):
        query   = """SELECT `%s` FROM `%s` WHERE `%s`="%s";
        """%( DbHeader.HOLIDAY_ID, DbTable.HOLIDAY, DbHeader.DATE, date)
        query_result    = self.db_query(query)
        if query_result:
            return True
        else:
            return False
    
    def get_list_resource(self):
        query = """
                SELECT `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`
                FROM `%s`
                INNER JOIN `%s`
                ON `%s`.`%s`=`%s`.`%s`
                INNER JOIN `%s`
                ON `%s`.`%s`=`%s`.`%s`
                INNER JOIN `%s`
                ON `%s`.`%s`=`%s`.`%s`
                ORDER BY `%s`.`%s`;
        """%(
            DbTable.USER, DbHeader.LEADER_ID, 
            DbTable.USER, DbHeader.USER_ID, 
            DbTable.USER, DbHeader.USER_NAME, 
            DbTable.USER, DbHeader.FULL_NAME, 
            DbTable.USER, DbHeader.EMAIL,
            DbTable.USER, DbHeader.IS_ACTIVE,
            DbTable.USER, DbHeader.OTHER_NAME,
            DbTable.TEAM, DbHeader.TEAM_NAME,
            DbTable.ENG_LEVEL, DbHeader.LEVEL,
            DbTable.ENG_TYPE, DbHeader.ENG_TYPE_NAME,
            DbTable.TEAM, 
            DbTable.USER, 
            DbTable.TEAM, DbHeader.TEAM_ID, DbTable.USER, DbHeader.TEAM_ID,
            DbTable.ENG_LEVEL, 
            DbTable.ENG_LEVEL, DbHeader.ENG_LEVEL_ID, DbTable.USER, DbHeader.ENG_LEVEL_ID,
            DbTable.ENG_TYPE, 
            DbTable.ENG_TYPE, DbHeader.ENG_TYPE_ID, DbTable.USER, DbHeader.ENG_TYPE_ID,
            DbTable.USER, DbHeader.USER_NAME
            )
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            return query_result
        else:
            return result
    
    def get_team_info(self, is_parse=False):
        query = """
                SELECT `%s`, `%s`, `%s`
                FROM `%s`;
        """%(
            DbHeader.TEAM_ID, DbHeader.TEAM_NAME, DbHeader.TEAM_LEAD_ID,
            DbTable.TEAM
            )
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            if is_parse:
                for row in query_result:
                    team_id   = row[DbHeader.TEAM_ID]
                    team_name = row[DbHeader.TEAM_NAME]
                    lead_id   = row[DbHeader.TEAM_LEAD_ID]
                    self.team[team_name] = team_id
                    self.team_ids[team_id] = team_name
            return query_result
        else:
            return result
    
    def get_eng_level_info(self, is_parse=False):
        query = """
                SELECT `%s`, `%s`
                FROM `%s`;
        """%(
            DbHeader.ENG_LEVEL_ID, DbHeader.LEVEL,
            DbTable.ENG_LEVEL
            )
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            if is_parse:
                for row in query_result:
                    eng_level_id   = row[DbHeader.ENG_LEVEL_ID]
                    eng_level_name = row[DbHeader.LEVEL]
                    self.eng_level[eng_level_name] = eng_level_id
                    self.eng_level_ids[eng_level_id] = eng_level_name
            return query_result
        else:
            return result
    
    def get_eng_type_info(self, is_parse=False):
        query = """
                SELECT `%s`, `%s`
                FROM `%s`;
        """%(
            DbHeader.ENG_TYPE_ID, DbHeader.ENG_TYPE_NAME,
            DbTable.ENG_TYPE
            )
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            if is_parse:
                for row in query_result:
                    eng_type_id   = row[DbHeader.ENG_TYPE_ID]
                    eng_type_name = row[DbHeader.ENG_TYPE_NAME]
                    self.eng_type[eng_type_name] = eng_type_id
                    self.eng_type_ids[eng_type_id] = eng_type_name
            return query_result
        else:
            return result
           
    def add_resource(self):
        query   = """INSERT INTO `%s` (`%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`)
                    VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s");
        """%(DbTable.USER, DbHeader.USER_NAME, DbHeader.FULL_NAME, DbHeader.EMAIL, DbHeader.IS_ACTIVE, DbHeader.OTHER_NAME,\
             DbHeader.UPDATED_BY, DbHeader.ENG_LEVEL_ID, DbHeader.ENG_TYPE_ID, DbHeader.TEAM_ID,\
             self.user_name, self.full_name, self.email, self.is_active, self.other_name, self.updated_by, 
             self.eng_level_id, self.eng_type_id, self.team_id
             )
        self.db_execute(query)
    
    def is_exist_resource(self):
        query   = """SELECT `%s` FROM `%s` WHERE `%s`="%s";
        """%( DbHeader.USER_ID, DbTable.USER, DbHeader.USER_NAME, self.user_name)
        query_result    = self.db_query(query)
        if query_result:
            return True
        else:
            return False
    
    def update_resource(self, ):
        query   = """UPDATE `%s` SET `%s`="%s", `%s`="%s" , `%s`="%s" , `%s`="%s" , `%s`="%s" , `%s`="%s" , `%s`="%s" , `%s`="%s"
                    WHERE `%s`="%s";
        """%( DbTable.USER, DbHeader.FULL_NAME, self.full_name, DbHeader.EMAIL, self.email,
              DbHeader.IS_ACTIVE, self.is_active, DbHeader.OTHER_NAME, self.other_name,
              DbHeader.UPDATED_BY, self.updated_by, DbHeader.ENG_LEVEL_ID, self.eng_level_id,
              DbHeader.ENG_TYPE_ID, self.eng_type_id, DbHeader.TEAM_ID, self.team_id,
               DbHeader.USER_NAME, self.user_name)
        self.db_execute(query)
    
    def inactive_all_resource(self, ):
        query   = """UPDATE `%s` SET `%s`="0";
        """%( DbTable.USER, DbHeader.IS_ACTIVE)
        self.db_execute(query)
    
    def active_resource(self, user_name):
        query   = """UPDATE `%s` SET `%s`="1" WHERE `%s`="%s";
        """%( DbTable.USER, DbHeader.IS_ACTIVE, DbHeader.USER_NAME, user_name)
        self.db_execute(query)
        
    def update_resource_leader(self, list_record):
        query   = '''UPDATE `user` SET
                        `leader_id`=%s WHERE `user_id`=%s;
                    '''
        self.db_execute_many(query, list_record)
        
    def remove_all_user_of_sheet(self, list_id=[]):
        condition_list = []
        for sheet_id in  list_id:
            condition_list.append('`%s`="%s"'%(DbHeader.SHEET_ID, str(sheet_id)))
        condition   = ' OR '.join(condition_list)
        query   = '''DELETE FROM `%s` WHERE %s;'''%(\
                    DbTable.PROJECT_USER, condition 
                    )
        self.db_execute(query)
    
    def remove_users_of_sheet(self, list_record):
        
        query   = 'DELETE FROM `%s` WHERE `%s`='%(DbTable.PROJECT_USER, DbHeader.SHEET_ID) \
                    + '%s AND ' + '`%s`='%(DbHeader.USER_ID) + '%s;'
        self.db_execute_many(query, list_record)
    
    def add_user_of_sheet(self, list_record):
        query   = '''INSERT INTO `%s` 
                        (`%s`, `%s`)
                    '''%(DbTable.PROJECT_USER,\
                    DbHeader.SHEET_ID, DbHeader.USER_ID)
        query   += '''
                    VALUES
                        (%s, %s)
                    ;'''

        self.db_execute_many(query, list_record)
    
    def get_analyze_config(self):
        query   = """SELECT `%s`, `%s` FROM `%s`;
        """%( DbHeader.CONFIG_NAME, DbHeader.CONFIG_VALUE, DbTable.ANALYSIS_CONFIG)
        query_result    = self.db_query(query)
        result = {}
        
        if query_result:
            for row in query_result:
                result[row[DbHeader.CONFIG_NAME]] = row[DbHeader.CONFIG_VALUE]
        return result
    
    def update_analyze_config(self):
        query   = """UPDATE `%s` SET `%s`="%s", `%s`="%s" WHERE `%s`="%s";
        """%( DbTable.ANALYSIS_CONFIG, DbHeader.CONFIG_VALUE, self.config_value, DbHeader.UPDATED_BY, self.updated_by,\
              DbHeader.CONFIG_NAME, self.config_name)
        self.db_execute(query)
    
    def get_sheet_loading_smartsheet(self): 
        query   = """SELECT `%s`, `%s` FROM `%s` WHERE `%s`="1";
        """%( DbHeader.SHEET_NAME, DbHeader.SHEET_ID, DbTable.SHEET, DbHeader.IS_LOADING)
        query_result    = self.db_query(query, shareable=False)
        result = {}
        if query_result:
            for row in query_result:
                result[row[DbHeader.SHEET_ID]] = row[DbHeader.SHEET_NAME]
        return result
    
    def update_is_loading_of_sheet(self):
        query   = """UPDATE `%s` SET `%s`="%s"
                    WHERE `%s`="%s";
        """%( DbTable.SHEET, DbHeader.IS_LOADING, str(self.is_loading),
               DbHeader.SHEET_ID, self.sheet_id)
        self.db_execute(query)
    
    def get_other_config_info(self, is_parse=True):
        query   = """SELECT `%s`, `%s`, `%s` FROM `%s`;"""%( 
            DbHeader.OTHER_CONFIG_ID, DbHeader.CONFIG_NAME, DbHeader.CONFIG_VALUE, DbTable.OTHER_CONFIG)
        query_result    = self.db_query(query)
        if is_parse:
            result = {}
            if query_result:
                for row in query_result:
                    result[row[DbHeader.CONFIG_NAME]] = row[DbHeader.CONFIG_VALUE]
        else:
            result = []
            if query_result:
                result = query_result
        return result
    
    def check_exist_config_info(self):
        query   = """SELECT `%s` FROM `%s` WHERE `%s`="%s";"""%( 
            DbHeader.OTHER_CONFIG_ID, DbTable.OTHER_CONFIG, DbHeader.CONFIG_NAME, self.config_name)
        query_result    = self.db_query(query)
        if query_result:
            return True
        else:
            return False
    
    def update_other_config_info(self):
        query   = """UPDATE `%s` SET `%s`="%s"
                    WHERE `%s`="%s";
        """%( DbTable.OTHER_CONFIG, DbHeader.CONFIG_VALUE, self.config_value,
               DbHeader.CONFIG_NAME, self.config_name)
        self.db_execute(query)
    
    def add_other_config_info(self):
        query   = """INSERT INTO `%s` (`%s`, `%s`)
                    VALUES ("%s", "%s");
        """%(DbTable.OTHER_CONFIG, DbHeader.CONFIG_VALUE, DbHeader.CONFIG_NAME, self.config_value, self.config_name)
        self.db_execute(query)
    
    def get_user_version(self):
        query   = """SELECT `%s`, `%s`, `%s` FROM `%s`;"""%( 
            DbHeader.VERSION, DbHeader.USER_VERSION_ID, DbHeader.USER_ID, DbTable.USER_VERSION)
        query_result    = self.db_query(query)
        result = {}
        if query_result:
            for row in query_result:
                result[row[DbHeader.USER_ID]] = [row[DbHeader.USER_VERSION_ID], row[DbHeader.VERSION]]
        return result
    
    def check_exist_user_version(self):
        query   = """SELECT `%s` FROM `%s` WHERE `%s`="%s";"""%( 
            DbHeader.USER_VERSION_ID, DbTable.USER_VERSION, DbHeader.USER_ID, self.user_id)
        query_result    = self.db_query(query)
        if query_result:
            return True
        else:
            return False
    
    def update_user_version(self):
        query   = """UPDATE `%s` SET `%s`="%s"
                    WHERE `%s`="%s";
        """%( DbTable.USER_VERSION, DbHeader.VERSION, self.version,
               DbHeader.USER_ID, self.user_id)
        self.db_execute(query)
    
    def add_user_version(self):
        query   = """INSERT INTO `%s` (`%s`, `%s`)
                    VALUES ("%s", "%s");
        """%(DbTable.USER_VERSION, DbHeader.USER_ID, DbHeader.VERSION, self.user_id, self.version)
        self.db_execute(query)
    
    def check_exist_role(self, role_name):
        query   = """SELECT `%s` FROM `%s` WHERE `%s`="%s";"""%( 
            DbHeader.ROLE_ID, DbTable.ROLE, DbHeader.ROLE_NAME, role_name)
        query_result    = self.db_query(query)
        if query_result:
            return True
        else:
            return False
        
    def add_role(self, role_name):
        query   = """INSERT INTO `%s` (`%s`)
                    VALUES ("%s");
        """%(DbTable.ROLE, DbHeader.ROLE_NAME, role_name)
        self.db_execute(query)
    
    def remove_role(self, role_name):
        query   = """DELETE FROM `%s` WHERE `%s`="%s";
        """%(DbTable.ROLE, DbHeader.ROLE_NAME, role_name)
        self.db_execute(query)
    
    def check_exist_user_role(self, user_id, role_id):
        query   = """SELECT `%s` FROM `%s` WHERE `%s`="%s" AND `%s`="%s";"""%( 
            DbHeader.USER_ROLE_ID, DbTable.USER_ROLE, DbHeader.ROLE_ID, role_id, DbHeader.USER_ID, user_id)
        query_result    = self.db_query(query)
        if query_result:
            return True
        else:
            return False
        
    def add_user_role(self, user_id, role_id):
        query   = """INSERT INTO `%s` (`%s`, `%s`)
                    VALUES ("%s", "%s");
        """%(DbTable.USER_ROLE, DbHeader.ROLE_ID, DbHeader.USER_ID, role_id, user_id)
        self.db_execute(query)
    
    def remove_user_role(self, user_id, role_id):
        query   = """DELETE FROM `%s` WHERE `%s`="%s" AND `%s`="%s";
        """%(DbTable.USER_ROLE, DbHeader.ROLE_ID, role_id, DbHeader.USER_ID, user_id)
        self.db_execute(query)
    
    def add_productivity_config(self, list_record):
        query   = '''INSERT INTO `%s` 
                        (`%s`, `%s`, `%s`, `%s`, `%s`)
                    '''%(DbTable.PRODUCTIVITY_CONFIG,\
                    DbHeader.WEEK, DbHeader.SHEET_TYPE_ID, DbHeader.USER_ID, \
                    DbHeader.WORK_HOUR, DbHeader.UPDATED_BY)
        query   += '''
                    VALUES
                        (%s, %s, %s, %s, %s)
                    ;'''
        self.db_execute_many(query, list_record)
    
    def remove_productivity_config_by_date(self, list_week):
        if len(list_week):
            query   = """DELETE FROM `%s` WHERE `%s` in %s;
            """%(DbTable.PRODUCTIVITY_CONFIG, DbHeader.WEEK, str(list_week))
            self.db_execute(query)
            
        
    def get_productivity_config(self, start_date=None, end_date=None):
        condition = ''
        if start_date and  end_date:
            condition = "WHERE `%s`.`%s`>='%s' AND `%s`.`%s`<='%s'"%(
                DbTable.PRODUCTIVITY_CONFIG, DbHeader.WEEK, start_date,
                DbTable.PRODUCTIVITY_CONFIG, DbHeader.WEEK, end_date)
        query = """
                SELECT `%s`.`%s`, 
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`
                FROM `%s` 
                INNER JOIN `%s`
                ON `%s`.`%s`=`%s`.`%s`
                INNER JOIN `%s`
                ON `%s`.`%s`=`%s`.`%s`
                %s
                ORDER BY `%s`.`%s`, `%s`.`%s`, `%s`.`%s`;
        """%(
            DbTable.SHEET_TYPE, DbHeader.SHEET_TYPE,
            DbTable.USER, DbHeader.USER_NAME,
            DbTable.PRODUCTIVITY_CONFIG, DbHeader.WEEK,
            DbTable.PRODUCTIVITY_CONFIG, DbHeader.WORK_HOUR,
            DbTable.PRODUCTIVITY_CONFIG, DbHeader.UPDATED_BY,
            DbTable.PRODUCTIVITY_CONFIG,
            DbTable.SHEET_TYPE,
            DbTable.SHEET_TYPE, DbHeader.SHEET_TYPE_ID, DbTable.PRODUCTIVITY_CONFIG, DbHeader.SHEET_TYPE_ID,
            DbTable.USER,
            DbTable.USER, DbHeader.USER_ID, DbTable.PRODUCTIVITY_CONFIG, DbHeader.USER_ID,
            condition,
            DbTable.PRODUCTIVITY_CONFIG, DbHeader.WEEK,
            DbTable.SHEET_TYPE, DbHeader.SHEET_TYPE,
            DbTable.USER, DbHeader.USER_NAME
            )
        query_result    = self.db_query(query)
        result = {}
        if query_result:
            for row in query_result:
                sheet_type = row[DbHeader.SHEET_TYPE]
                resource = row[DbHeader.USER_NAME]
                week = row[DbHeader.WEEK]
                work_hour = row[DbHeader.WORK_HOUR]
                work_hour   = round_num(work_hour)
                if not result.get(week):
                    result[week] = {}
                if not result[week].get(resource):
                    result[week][resource] = {}
                result[week][resource][sheet_type] = work_hour
        return result
    
    def check_exist_productivity_config(self):
        query   = """SELECT `%s` FROM `%s` WHERE `%s`="%s" AND `%s`="%s" AND `%s`="%s";"""%( 
            DbHeader.PRODUCTIVITY_CONFIG_ID, DbTable.PRODUCTIVITY_CONFIG, 
            DbHeader.USER_ID, self.user_id, DbHeader.SHEET_TYPE_ID, self.sheet_type_id, \
            DbHeader.WEEK, self.week)
        query_result    = self.db_query(query)
        if query_result:
            return True
        else:
            return False
    
    def update_productivity_config(self):
        query   = """UPDATE `%s` SET `%s`="%s", `%s`="%s"
                    WHERE `%s`="%s" AND `%s`="%s" AND `%s`="%s";
        """%( DbTable.PRODUCTIVITY_CONFIG, DbHeader.WORK_HOUR, self.work_hour, 
              DbHeader.UPDATED_BY, self.updated_by,
              DbHeader.USER_ID, self.user_id, 
              DbHeader.SHEET_TYPE_ID, self.sheet_type_id, 
              DbHeader.WEEK, self.week, 
              )
        self.db_execute(query)
        
class DbTask(Connection):
    def __init__(self):
        Connection.__init__(self)
    
    def remove_all_task_information_by_project_id(self):
        query   = '''DELETE FROM
                        `%s`
                    WHERE
                        `%s`="%d";'''%(\
                    DbTable.TASK, \
                    DbHeader.SHEET_ID, self.sheet_id
                    )
        self.db_execute(query)
    
    def add_task(self, list_record):
        query   = '''INSERT INTO `%s` 
                        (`%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`)
                    '''%(DbTable.TASK,\
                    DbHeader.SHEET_ID, DbHeader.USER_ID, DbHeader.SIBLING_ID, DbHeader.PARENT_ID, DbHeader.SELF_ID, DbHeader.TASK_NAME, DbHeader.DATE, DbHeader.START_DATE, DbHeader.END_DATE,\
                    DbHeader.DURATION, DbHeader.COMPLETE, DbHeader.PREDECESSORS, DbHeader.COMMENT, DbHeader.ACTUAL_END_DATE, DbHeader.STATUS, DbHeader.IS_CHILDREN, DbHeader.ALLOCATION)
        query   += '''
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ;'''

        self.db_execute_many(query, list_record)
    
    def get_tasks(self):
        query = """
                SELECT `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`
                FROM `%s`
                WHERE
                `%s`="%s" AND `%s`>="%s" AND `%s`<="%s";
        """%(
            DbHeader.TASK_ID, DbHeader.USER_ID,  DbHeader.SIBLING_ID, DbHeader.PARENT_ID, DbHeader.SELF_ID, DbHeader.TASK_NAME, DbHeader.DATE, DbHeader.ALLOCATION, DbHeader.IS_CHILDREN,
            DbHeader.START_DATE, DbHeader.END_DATE,  DbHeader.DURATION, DbHeader.COMPLETE, DbHeader.PREDECESSORS, DbHeader.COMMENT, DbHeader.ACTUAL_END_DATE, DbHeader.STATUS, 
            DbTable.TASK,
            DbHeader.SHEET_ID, self.sheet_id, DbHeader.DATE, self.start_date, DbHeader.DATE, self.end_date
            )
        
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            return query_result
        else:
            return result
    
    def get_all_tasks(self):
        query = """
                SELECT `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`
                FROM `%s`
                WHERE
                `%s`>="%s" AND `%s`<="%s";
        """%(
            DbHeader.SHEET_ID, DbHeader.TASK_ID, DbHeader.USER_ID,  DbHeader.SIBLING_ID, DbHeader.PARENT_ID, DbHeader.SELF_ID, DbHeader.TASK_NAME, DbHeader.DATE, DbHeader.ALLOCATION, DbHeader.IS_CHILDREN,
            DbHeader.START_DATE, DbHeader.END_DATE,  DbHeader.DURATION, DbHeader.COMPLETE, DbHeader.PREDECESSORS, DbHeader.COMMENT, DbHeader.ACTUAL_END_DATE, DbHeader.STATUS, 
            DbTable.TASK,
            DbHeader.DATE, self.start_date, DbHeader.DATE, self.end_date
            )
        
        query_result    = self.db_query(query)
        result          = {}
        if query_result:
            for row in query_result:
                if not result.get(row[DbHeader.SHEET_ID]):
                    result[row[DbHeader.SHEET_ID]] = []
                result[row[DbHeader.SHEET_ID]].append(row)
            return result
        else:
            return result
        
    def add_final_task(self, list_record):
        query   = '''INSERT INTO `%s` 
                        (`%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`)
                    '''%(DbTable.TASK_FINAL,\
                    DbHeader.SHEET_ID, DbHeader.USER_ID, DbHeader.SIBLING_ID, DbHeader.PARENT_ID, DbHeader.SELF_ID, DbHeader.TASK_NAME, DbHeader.DATE, DbHeader.START_DATE, DbHeader.END_DATE,\
                    DbHeader.DURATION, DbHeader.COMPLETE, DbHeader.PREDECESSORS, DbHeader.COMMENT, DbHeader.ACTUAL_END_DATE, DbHeader.STATUS, DbHeader.IS_CHILDREN, DbHeader.ALLOCATION)
        query   += '''
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ;'''

        self.db_execute_many(query, list_record)
        
    def get_final_tasks(self):
        query = """
                SELECT `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`
                FROM `%s`
                WHERE
                `%s`="%s" AND `%s`>="%s" AND `%s`<="%s";
        """%(
            DbHeader.TASK_FINAL_ID, DbHeader.USER_ID,  DbHeader.SIBLING_ID, DbHeader.PARENT_ID, DbHeader.SELF_ID, DbHeader.TASK_NAME, DbHeader.DATE, DbHeader.ALLOCATION, DbHeader.IS_CHILDREN,
            DbHeader.START_DATE, DbHeader.END_DATE,  DbHeader.DURATION, DbHeader.COMPLETE, DbHeader.PREDECESSORS, DbHeader.COMMENT, DbHeader.ACTUAL_END_DATE, DbHeader.STATUS, 
            DbTable.TASK_FINAL,
            DbHeader.SHEET_ID, self.sheet_id, DbHeader.DATE, self.start_date, DbHeader.DATE, self.end_date
            )
        
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            return query_result
        else:
            return result    
    
    def get_all_final_tasks(self):
        query = """
                SELECT `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`
                FROM `%s`
                WHERE
                `%s`>="%s" AND `%s`<="%s";
        """%(
            DbHeader.SHEET_ID, DbHeader.TASK_FINAL_ID, DbHeader.USER_ID,  DbHeader.SIBLING_ID, DbHeader.PARENT_ID, DbHeader.SELF_ID, DbHeader.TASK_NAME, DbHeader.DATE, DbHeader.ALLOCATION, DbHeader.IS_CHILDREN,
            DbHeader.START_DATE, DbHeader.END_DATE,  DbHeader.DURATION, DbHeader.COMPLETE, DbHeader.PREDECESSORS, DbHeader.COMMENT, DbHeader.ACTUAL_END_DATE, DbHeader.STATUS, 
            DbTable.TASK_FINAL,
            DbHeader.DATE, self.start_date, DbHeader.DATE, self.end_date
            )
        
        query_result    = self.db_query(query)
        result          = {}
        if query_result:
            for row in query_result:
                if not result.get(row[DbHeader.SHEET_ID]):
                    result[row[DbHeader.SHEET_ID]] = []
                result[row[DbHeader.SHEET_ID]].append(row)
            return result
        else:
            return result
        
    def remove_final_task_information(self):
        query   = '''DELETE FROM
                        `%s`
                    WHERE
                        `%s`="%s" AND `%s`>="%s" AND `%s`<="%s";'''%(\
                    DbTable.TASK_FINAL, \
                    DbHeader.SHEET_ID, self.sheet_id, DbHeader.DATE, self.start_date, DbHeader.DATE, self.end_date
                    )
        
        self.db_execute(query)
    
    def move_task_to_final(self):
        query   = '''INSERT INTO `%s` 
                            (`%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`)
                        SELECT
                            `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`
                        FROM
                            `%s`
                        WHERE
                            `%s`="%s" AND `%s`>="%s" AND `%s`<="%s";'''%(\
                    DbTable.TASK_FINAL,\
                    
                    DbHeader.SHEET_ID, DbHeader.USER_ID, DbHeader.SIBLING_ID, DbHeader.PARENT_ID, \
                    DbHeader.SELF_ID, DbHeader.TASK_NAME, DbHeader.DATE, DbHeader.START_DATE, DbHeader.END_DATE,\
                    DbHeader.DURATION, DbHeader.COMPLETE, DbHeader.PREDECESSORS, DbHeader.COMMENT, \
                    DbHeader.ACTUAL_END_DATE, DbHeader.STATUS, DbHeader.IS_CHILDREN, DbHeader.ALLOCATION, \
                    
                    DbHeader.SHEET_ID, DbHeader.USER_ID, DbHeader.SIBLING_ID, DbHeader.PARENT_ID, \
                    DbHeader.SELF_ID, DbHeader.TASK_NAME, DbHeader.DATE, DbHeader.START_DATE, DbHeader.END_DATE,\
                    DbHeader.DURATION, DbHeader.COMPLETE, DbHeader.PREDECESSORS, DbHeader.COMMENT, \
                    DbHeader.ACTUAL_END_DATE, DbHeader.STATUS, DbHeader.IS_CHILDREN, DbHeader.ALLOCATION, \

                    DbTable.TASK,\
                    DbHeader.SHEET_ID, self.sheet_id, DbHeader.DATE, self.start_date, DbHeader.DATE, self.end_date)
        
        self.milestone_id = self.db_execute(query)
    
    def add_final_date(self, list_record=None, date=None, sheet_id=None, from_date=None, to_date=None):
        if list_record:
            query   = '''INSERT INTO `%s` 
                            (`%s`, `%s`, `%s`, `%s`)
                        '''%(DbTable.FINAL_DATE,\
                        DbHeader.DATE, DbHeader.SHEET_ID, DbHeader.START_DATE, DbHeader.END_DATE)
            query   += '''
                        VALUES
                            (%s, %s, %s, %s)
                        ;'''
            self.db_execute_many(query, list_record)
        else:
            query   = '''INSERT INTO `%s` 
                            (`%s`, `%s`, `%s`, `%s`)
                        VALUES
                            ('%s', '%s', '%s', '%s')
                        ;'''%(DbTable.FINAL_DATE,\
                        DbHeader.DATE, DbHeader.SHEET_ID, DbHeader.START_DATE, DbHeader.END_DATE, \
                        date, sheet_id, from_date, to_date)
            id = self.db_execute_2(query)
            return id
        
    def get_final_date(self):
        query = """
                SELECT `%s`, `%s`
                FROM `%s`
                WHERE
                `%s`>="%s" AND `%s`<="%s";
        """%(
            DbHeader.DATE, DbHeader.SHEET_ID, 
            DbTable.FINAL_DATE,
             DbHeader.DATE, self.start_date, DbHeader.DATE, self.end_date
            )
        
        query_result    = self.db_query(query)
        result          = {}
        if query_result:
            for row in query_result:
                if not result.get(row[DbHeader.SHEET_ID]):
                    result[row[DbHeader.SHEET_ID]] = []
                date_str = convert_date_to_string(row[DbHeader.DATE], '%Y-%m-%d')
                result[row[DbHeader.SHEET_ID]].append(date_str)
        return result  
    
    def get_analyze_item(self):
        query = """
            SELECT `%s`, `%s`
            FROM `%s`;
        """%(DbHeader.ANALYZE_ITEM_ID, DbHeader.ITEM_NAME, DbTable.ANALYZE_ITEM)
        query_result = self.db_query(query)
        result = {}
        if query_result:
            for row in query_result:
                result[row[DbHeader.ITEM_NAME]] = row[DbHeader.ANALYZE_ITEM_ID]
        return result
    
    def add_final_evidence(self, final_date_id, analyze_item_id, is_approve, counter, comment, updated_by):
        query   = '''INSERT INTO `%s` 
                        (`%s`, `%s`, `%s`, `%s`, `%s`, `%s`)
                    VALUES
                        ('%s', '%s', '%s', '%s', '%s', '%s')
                    ;'''%(DbTable.FINAL_EVIDENCE,\
                    DbHeader.FINAL_DATE_ID, DbHeader.ANALYZE_ITEM_ID, DbHeader.IS_APPROVE, \
                    DbHeader.COUNTER, DbHeader.COMMENT, DbHeader.UPDATED_BY,\
                    final_date_id, analyze_item_id, is_approve, counter, comment, updated_by)
        self.db_execute(query)
        
        
class DbUsers(Connection):
    def __init__(self, info=None):
        Connection.__init__(self)
        self.user_id        = None
        self.user_name      = None
        self.full_name      = None
        self.email          = None
        self.other_name     = None
        self.is_active      = None
        self.updated_by     = None
        self.updated_date   = None
        self.eng_level_id   = None
        self.eng_type_id    = None
        self.team_id        = None
        self.leader_id        = None
        self. add_info(info)
        
    def add_info(self, info):
        if info:
            self.user_id        = int(info[DbHeader.USER_ID])
            self.user_name      = info[DbHeader.USER_NAME]
            self.full_name      = info[DbHeader.FULL_NAME]
            self.email          = info[DbHeader.EMAIL]
            self.other_name     = split_patern(info[DbHeader.OTHER_NAME], ';|,')
            self.is_active      = int(info[DbHeader.IS_ACTIVE])
            self.updated_by     = info[DbHeader.UPDATED_BY]
            self.updated_date   = info[DbHeader.UPDATED_DATE]
            self.eng_level_id   = int(info[DbHeader.ENG_LEVEL_ID])
            self.eng_type_id    = int(info[DbHeader.ENG_TYPE_ID])
            self.team_id        = int(info[DbHeader.TEAM_ID])
            if isinstance(info[DbHeader.LEADER_ID], int):
                self.leader_id        = int(info[DbHeader.LEADER_ID])

class TimeOff(Connection):
    def __init__(self, info=None, holidays=[]):
        Connection.__init__(self)
        self.time_off_id    = None
        self.user_name      = None
        self.department     = None
        self.type           = None
        self.start_date     = None
        self.end_date       = None
        self.work_days      = None
        self.timeoff_per_day = None
        self.status         = None
        self.user_id        = 0
        self.dates          = []
        self.add_info(info, holidays)
        
    def add_info(self, info, holidays):
        if info:
            self.time_off_id    = info[DbHeader.TIME_OFF_ID]
            self.user_name      = info[DbHeader.USER_NAME]
            self.department     = info[DbHeader.DEPARTMENT]
            self.type           = info[DbHeader.TYPE]
            self.start_date     = info[DbHeader.START_DATE]
            self.end_date       = info[DbHeader.END_DATE]
            self.work_days      = int(info[DbHeader.WORK_DAYS])
            self.status         = info[DbHeader.STATUS]
            self.user_id        = info[DbHeader.USER_ID]
            
            self.dates          = get_work_days(from_date=self.start_date, to_date=self.end_date, holidays=holidays)
            self.timeoff_per_day    = round_num(int(self.work_days / len(self.dates)))
            
class Log(Connection):
    def __init__(self, table_name=None):
        Connection.__init__(self)
        self.table_name = table_name
        
    def get_action(self):
        query   = """SELECT `%s`, `%s`  FROM `%s`;"""%( 
            DbHeader.ACTION_ID, DbHeader.ACTION_NAME, DbTable.ACTION)
        query_result    = self.db_query(query)
        result = ()
        if query_result:
            result = query_result
        return result
    
    def get_action_id(self):
        query   = """SELECT `%s` FROM `%s` WHERE `%s`='%s';"""%( 
            DbHeader.ACTION_ID, DbTable.ACTION, DbHeader.ACTION_NAME, self.action_name)
        query_result    = self.db_query(query)
        result = None
        if query_result:
            result = query_result[0][DbHeader.ACTION_ID]
            self.action_id = result
        return result
        
    def add_log(self):
        query   = '''INSERT INTO `%s`
                (`%s`, `%s`, `%s`, `%s`, `%s`)
                VALUES 
                ("%s", "%s", "%s", "%s", "%s");
                '''%(
                    DbTable.LOG, DbHeader.SHEET_ID, DbHeader.ACTION_ID, \
                    DbHeader.OLD_VALUE, DbHeader.NEW_VALUE, DbHeader.UPDATED_BY, 
                    self.sheet_id, self.action_id, self.old_value, self.new_value, self.updated_by)
        
        self.db_execute(query)
        
    def get_log(self, from_date, to_date, action_ids):
        condition = ''
        if action_ids:
            condition = ' AND ('
            list_oparator = []
            for action_id in action_ids:
                list_oparator.append(" `%s`.`%s`='%d' "%(DbTable.ACTION, DbHeader.ACTION_ID, action_id))
            condition +=  ' OR '.join(list_oparator) + ')'
        query   = """SELECT `%s`.`%s`, 
                            `%s`.`%s`, 
                            `%s`.`%s`, 
                            `%s`.`%s`, 
                            `%s`.`%s`, 
                            `%s`.`%s`, 
                            `%s`.`%s`, 
                            `%s`.`%s`
                    FROM `%s`
                    INNER JOIN `%s` ON `%s`.`%s`=`%s`.`%s`
                    LEFT JOIN `%s` ON `%s`.`%s`=`%s`.`%s`
                    WHERE `%s`.`%s`>='%s' AND `%s`.`%s`<='%s' %s;
            ;"""%( 
            DbTable.SHEET, DbHeader.SHEET_NAME,\
            DbTable.SHEET, DbHeader.SHEET_ID,\
            DbTable.ACTION, DbHeader.ACTION_ID,\
            DbTable.ACTION, DbHeader.ACTION_NAME,\
            DbTable.LOG, DbHeader.OLD_VALUE,\
            DbTable.LOG, DbHeader.NEW_VALUE,\
            DbTable.LOG, DbHeader.UPDATED_DATE,\
            DbTable.LOG, DbHeader.UPDATED_BY,\
            DbTable.LOG, \
            DbTable.ACTION, DbTable.ACTION, DbHeader.ACTION_ID, DbTable.LOG, DbHeader.ACTION_ID,\
            DbTable.SHEET, DbTable.SHEET, DbHeader.SHEET_ID, DbTable.LOG, DbHeader.SHEET_ID,\
            DbTable.LOG, DbHeader.UPDATED_DATE, from_date, DbTable.LOG, DbHeader.UPDATED_DATE, to_date, \
            condition)
        query_result    = self.db_query(query)
        result = ()
        if query_result:
            result = query_result
        return result
    
class DbEffectiveRate(Connection):
    def __init__(self):
        Connection.__init__(self)
        
    def remove_all_task_information_by_project_id(self):
        query   = '''DELETE FROM
                        `%s`
                    WHERE
                        `%s`="%d";'''%(\
                    DbTable.EFFECTIVE_RATE, \
                    DbHeader.SHEET_ID, self.sheet_id
                    )
        self.db_execute(query)
        
    def add_task(self, list_record):
        query   = '''INSERT INTO `%s` 
                        (`%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`)
                    '''%(DbTable.EFFECTIVE_RATE,\
                    DbHeader.SHEET_ID, DbHeader.USER_ID, DbHeader.TASK_NAME, DbHeader.START_DATE, DbHeader.END_DATE, DbHeader.ACTUAL_START_DATE, \
                    DbHeader.ACTUAL_END_DATE, DbHeader.ACTUAL_DURATION, DbHeader.DURATION, DbHeader.PREFIX_NAME, DbHeader.EFFECTIVE_RATE)
        query   += '''
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ;'''

        self.db_execute_many(query, list_record)
        
    def get_tasks(self, sheet_id):
        query = """
                SELECT `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`
                FROM `%s`
                WHERE
                `%s`="%s";
        """%(
            DbHeader.SHEET_ID, DbHeader.USER_ID, DbHeader.TASK_NAME, DbHeader.START_DATE, DbHeader.END_DATE, DbHeader.ACTUAL_START_DATE, \
            DbHeader.ACTUAL_END_DATE, DbHeader.ACTUAL_DURATION, DbHeader.DURATION, DbHeader.PREFIX_NAME, DbHeader.EFFECTIVE_RATE,
            DbTable.EFFECTIVE_RATE,
            DbHeader.SHEET_ID, sheet_id
            )
        
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            return query_result
        else:
            return result