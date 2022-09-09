'''
Created on Feb 5, 2021

@author: toannguyen
'''
    
class OtherKeys:
    
    METHOD_POST         = 'POST'
    METHOD_GET          = 'GET'
    LOGGING_DEBUG        = 'debug'
    LOGGING_INFO         = 'info'
    LOGGING_WARNING      = 'warning'
    LOGGING_ERROR        = 'error'
    LOGGING_EXCEPTION    = 'exception'
    LOGGING_CRITICAL     = 'critical'
    
class SessionKey:
    USERNAME        = 'username'
    PASSWORD        = 'password'
    SHEETS          = 'sheets'
    FROM            = 'from'
    TO              = 'to'
    IS_LOGIN        = 'is_login'

class Template:
    
    BREADCRUMB          = 'components/breadcrumb.html'
    NAVBAR              = 'components/navbar.html'
    SIDEBAR             = 'components/sidebar.html'
    BUTTON              = 'components/button.html'
    INPUT               = 'components/input.html'
    CHECKBOX            = 'components/checkbox.html'
    SELECT              = 'components/select.html'
    MODAL               = 'components/modal.html'
    
    HOME                = 'screens/home/home.html'
    ANALYZE             = 'screens/analyze/analyze.html'
    PREVIEW             = 'screens/preview/preview.html'
    LAYOUT              = 'screens/layout/layout.html'

    LOGIN               = 'screens/auth/login.html'
    
    ERROR_404           = 'screens/error/404.html'
    ERROR_500           = 'screens/error/500.html'
    
    
class Route:
    
    INDEX   = '/'
    HOME   = '/home'
    ANALYZE   = '/analyze'
    PREVIEW   = '/preview'
    START_ANALYZE = '/start-analyze'
    
    LOGIN   = '/login'
    LOGOUT   = '/logout'
    AUTH   = '/auth'
    
    
    
    