class InvalidFrameError(ValueError):
    '''Invalid byte at the beginning of the frame'''
    pass

class InvalidHeaderError(ValueError):
    '''Invalid header byte'''
    pass

class InvalidFooterError(ValueError):
    '''Invalid footer byte'''
    pass

class InvalidChecksumError(ValueError):
    '''Checksum is wrong'''
    pass

class NoResponseError(ValueError):
    '''No response received'''
    pass

class NoAckError(ValueError):
    '''Message was received successfully but status was not ACK'''
    pass

