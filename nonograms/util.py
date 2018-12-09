class InconsistencyException(RuntimeError):
    pass

class TimeoutException(RuntimeError):
    pass

class Direction:
    ROW = 0
    COLUMN = 1
