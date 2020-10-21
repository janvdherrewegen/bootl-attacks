from dataclasses import dataclass


@dataclass
class Glitch:
    ''' Class for recording a glitch '''
    offset: float
    width: float
    v_op: float
    v_fault: float
    return_code: int

