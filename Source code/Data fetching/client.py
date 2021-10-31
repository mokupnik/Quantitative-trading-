import binance.client
from binance.websockets import BinanceSocketManager
from consts import BinancePasswords
from BinanceFactory import BinanceFactory
from WebsocketHandlers import WebsocketHandler


class BinanceClient():
    INTERVAL_1MINUTE = binance.client.Client.KLINE_INTERVAL_1MINUTE
    INTERVAL_5MINUTE = binance.client.Client.KLINE_INTERVAL_5MINUTE

    def __init__(self, api_key, api_secret, id = 1):
        self.key = api_key
        self.secret = api_secret
        self.Client = binance.client.Client(api_key, api_secret)
        self.Websocket = BinanceSocketManager(self.Client)
        self.WebsocketHandler = WebsocketHandler()
        self.Factory = BinanceFactory()

    def get_historical_klines(self, instrument, sdate, edate = None, interval = INTERVAL_5MINUTE):

        if edate:
            return map(lambda x: self.Factory.create_kline(x, instrument),
                       self.Client.get_historical_klines(instrument, interval, sdate, edate))
        else:
            return map(lambda x: self.Factory.create_kline(x, instrument),
                       self.Client.get_historical_klines(instrument, interval, sdate))

    def get_historical_klines_generator(self, instrument, sdate, edate =None, interval = INTERVAL_5MINUTE):
        '''
        Preffered way to get klines
        Params:
            sdate : Starting date
            edate : Ending date
        '''
        if edate:
            for k in self.Client.get_historical_klines_generator(instrument, interval, sdate, edate):
                yield self.Factory.create_kline(k, instrument)
        else:
            for k in self.Client.get_historical_klines_generator(instrument, interval, sdate, edate):
                yield self.Factory.create_kline(k, instrument)



    def get_live_klines(self, instrument,func, interval = INTERVAL_1MINUTE):
        conn_key = self.Websocket.start_kline_socket(instrument,
                                                     lambda y: self.WebsocketHandler.process_kline(interval,
                                                                                                self.Factory.create_kline_websocket(y, instrument),
                                                                                                lambda x : func(x)),
                                                     interval)
        self.Websocket.start()
        print(conn_key)
        return conn_key



