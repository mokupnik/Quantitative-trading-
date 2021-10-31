from client import BinanceClient
from consts import BinancePasswords
import sys
sys.path.append('..')
from influxAPI.influx import InfluxClient

worker = InfluxClient()
bc = BinanceClient(BinancePasswords.api_key, BinancePasswords.api_secret)

def function_compose_write(last):
    if len(last) == 1:
        kline = last[0]
        measurement = 'kline1m'
    else:
        kline = bc.Factory.composeKlines(last)
        measurement = 'kline5m'
    worker.save(kline.instrument, measurement, kline.open_dt, **kline.to_dict())

def write_not_composed(kline):
       measurement = 'kline5m'
       worker.save(kline.instrument, measurement, kline.open_dt, **kline.to_dict())


def main():
    instrument = sys.argv[1]
    bc.get_live_klines(instrument, function_compose_write)

main()

