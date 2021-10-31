from WrappersBinance import Kline
class WebsocketHandler:
    def __init__(self,interval = '1m', last = [None], compose = False):
        
        
        self.last = [None for i in range(5)]
        self.interval = int(interval[:-1])
        self.i = 0

    def process_kline(self,  interval, kline : Kline, func, compose = True):
       
        if None not in self.last:
            if(kline.open_dt.minute == 59):
                print("RECEIVED : {}, OLD ONE : {}".format(kline, self.last[4]))
            if(kline.open_dt.minute == 0):
                print("RECEIVED : {}, OLD ONE : {}".format(kline, self.last[4]))
       
        if compose:
            
            if self.i ==0:
                if self.last[0] == None:
                    self.last[self.i] = kline
                if kline.open_dt.minute - self.last[0].open_dt.minute >= 1:
                    self.i +=1
                else:
                    self.last[self.i] = kline

            elif self.i<5:
                if self.last[self.i] == None:
                    self.last[self.i] = kline

                if kline.open_dt.minute - self.last[self.i].open_dt.minute >= 1:
                    self.i +=1
                else:
                    self.last[self.i] = kline


            if interval == '5m' and None not in self.last:
                if kline.open_dt.minute - self.last[self.i - 1].open_dt.minute >= 5 \
                    and None not in self.last:
                    func([self.last[4]])
                    func(self.last)
                    self.last = kline

                elif self.last[self.i-1].open_dt.minute == 55 and kline.open_dt.minute == 0 \
                    and None not in self.last:
                    func(self.last)
                    self.last = kline

                else:
                    self.last = kline

            if interval == '1m' and None not in self.last:
                if kline.open_dt.minute - self.last[4].open_dt.minute >= 1 \
                        or (self.last[4].open_dt.minute == 59 and kline.open_dt.minute == 0):
                    
                    if(kline.open_dt.minute == 59 or self.last[4].open_dt.minute == 59):
                        print("RECEIVED : {}, OLD ONE : {}".format(kline, self.last[4]))
                    if(kline.open_dt.minute == 0 or self.last[4].open_dt.minute == 0):
                        print("RECEIVED : {}, OLD ONE : {}".format(kline, self.last[4]))
                        
                        
                    func([self.last[4]])
                    if self.last[0].open_dt.minute % 5 == 0:
                        func(self.last)
                    self.shiftKlines(kline)
                else:
                    self.last[4] = kline
        else:
            if self.last == None and interval == '5m':
                if kline.open_dt.minute % 5 == 0:
                    self.last = kline
            elif self.last == None:
                self.last = kline
                
            if interval == '5m' and self.last != None:
                if kline.open_dt.minute == self.last.open_dt.minute + 5 or kline.open_dt == 0 and self.last.open_dt == 55:
                    func(self.last)
                    self.last = kline
                else:
                    self.last = kline
                    
            if interval == '1m' and None not in self.last:
                if kline.close_dt.minute - self.last.close_dt.minute >= 1 \
                        or (self.last.close_dt.minute == 59 and kline.close_dt == 0):
                    func(self.last)
                    self.last = kline
                else:
                    self.last = kline
            
            


    

    def shiftKlines(self,kline):
        for idx, x in enumerate(self.last[:-1]):
            self.last[idx] = self.last[idx+1]

        self.last[-1] = kline
