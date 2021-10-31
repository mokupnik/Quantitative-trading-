class IRespond:
    pass

class Kline(IRespond):
    def __init__(self,open_time, close_time, open_dt, close_dt, open, close, high, low, vol, instrument):
        self.open_time = open_time
        self.close_time = close_time
        self.open_dt = open_dt
        self.close_dt = close_dt
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.vol = vol
        self.instrument = instrument

    def __str__(self):
        return "Open_time: {}, Open_dt: {}, Close_dt: {} Open: {}, Close: {}, High: {}, Vol : {}".format(self.open_time,
                                                                                            self.open_dt,
                                                                                            self.close_dt,
                                                                                            self.open,
                                                                                            self.close,
                                                                                            self.high,
                                                                                            self.vol)
    def to_dict(self):
        fields={
            "open": float(self.open),
           "close": float(self.close),
           "high": float(self.high),
           "low" : float(self.low),
           "vol" : float(self.vol)
           }
        return fields
        

