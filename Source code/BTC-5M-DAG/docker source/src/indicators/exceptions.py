class MissingData(Exception):
    '''
    Raised when some of the data needed to run 
    the script is missing
    '''
    pass

class MaxRetry(Exception):
    '''
    Raised when limit of retries has been reached
    '''
    pass