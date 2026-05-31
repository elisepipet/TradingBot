#!/usr/env python3

# EPITECH 2024 Projet: Trade

# exemple de phrases envoyés par les bots
# update game next_candles USDT_BTC,1620550800,58400,57589.94,58159.59,57952.52,168676077.6

import sys
import math
from datetime import datetime

class Trade:
    def __init__(self):
        self.player_names = ""
        self.your_bot = ""
        self.timebank = 0
        self.time_per_move = 0
        self.candles_interval = 0
        self.candles_format = []
        self.candles_total = 0
        self.candles_given = 0
        self.stack = 0
        self.transaction_fee_percent = 0
        self.strings_infos = []
        self.positions_info = [0, 1, 2, 3, 4, 5, 6]
        self.position = None
        self.stacks = {}
        self.values = []
        self.IndicOBV = ""
        self.capital = 0
        self.crash = 0

    def Settings(self, line):
        line = line.split("\n")[0]
        line_tab = line.split(" ")
        if (line_tab[1] == "player_names"):
            self.player_names = line_tab[2]
        if (line_tab[1] == "your_bot"):
            self.your_bot = line_tab[2]
        if (line_tab[1] == "timebank"):
            self.timebank = int(line_tab[2])
        if (line_tab[1] == "time_per_move"):
            self.time_per_move = int(line_tab[2])
        if (line_tab[1] == "candle_interval"):
            self.candles_interval = int(line_tab[2])
        if (line_tab[1] == "candle_format"):
            self.candles_format = line_tab[2].split(",")
        if (line_tab[1] == "candles_total"):
            self.candles_total = int(line_tab[2])
        if (line_tab[1] == "candles_given"):
            self.candles_given = int(line_tab[2])
        if (line_tab[1] == "initial_stack"):
            self.stack = int(line_tab[2])
        if (line_tab[1] == "transaction_fee_percent"):
            self.transaction_fee_percent = float(line_tab[2])
        self.crash = 0
        self.OBV = 0.0
        return
    
    def UpdateCandlesValues(self, line):
        line = line.split("\n")[0]
        line_tab = line.split(" ")
        infos = line_tab[3].split(",")
        pos = 0
        file = {}
        for str in self.candles_format:
            if (str == 'date'):
                info = datetime.fromtimestamp(int(infos[self.positions_info[pos]]))
                file['date'] = info
                pos += 1
                continue
            if (str == 'pair'):
                file['pair'] = infos[self.positions_info[pos]]
                pos += 1
                continue
            file[str] = float(infos[self.positions_info[pos]])
            pos += 1
        self.values.append(file)
        self.pair = file['pair']
        self.OBV = self.CalculOBV()
        return

    def CalculOBV(self):
        if (len(self.values) < 7):
            return 0.0
        vol = float(self.values[-1]['volume'])
        if (self.values[-1]['close'] < self.values[-2]['close']):
            self.IndicOBV = "baisse"
            return float(self.OBV + vol)
        elif (self.values[-1]['close'] > self.values[-2]['close']):
            self.IndicOBV = "hausse"
            return float(self.OBV + vol)
        else:
            return 0.0

    def AverageLossAndGain(self):
        loss = []
        gain = []
        nb = len(self.values)
        for i in range (1, nb):
            a = self.values[i]['close'] - self.values[i - 1]['close']
            if (a < 0):
                loss.append(abs(a))
            elif (a > 0):
                gain.append(a)
            else:
                continue
        return (sum(loss[14:]) / 14), (sum(gain[14:]) / 14)

    def UpdateStacks(self, line):
        file = {}
        line_tab = line.split(" ")
        info = line_tab[3].split(",")
        for i in info:
            a = i.split(":")
            file[a[0]] = float(a[1])
        self.stacks = file

    def RSI(self):
        w, l = self.AverageLossAndGain()
        
        rs = w / l if l != 0 else float('inf')
        return 100 - (100 / (1 + rs))

    def DetectCrashMarket(self):
        if len(self.values) < 14:
            return False
        nb = 0

        recent_candles = self.values[-14:]
        sma = sum(candle['close'] for candle in recent_candles) / 14
        close_prices = [candle['close'] for candle in recent_candles]
        std_dev = (sum((price - sma) ** 2 for price in close_prices) / 14) ** 0.5
        rsi = self.RSI()
        if (recent_candles[-1]['close'] < sma - 2 * std_dev and rsi < 30):
            self.crash += 1
            return True
        for i in range (1, 14):
            if (close_prices[-i] < close_prices[-i + 1] or close_prices[-i] < sma):
                nb += 1
        if nb >= 13:
            self.crash += 1
            return True
        for i in range (1, 14):
            if (close_prices[-i] > close_prices[-i + 1] or close_prices[-i] > sma):
                nb += 1
        if nb >= 13:
            return False
        self.crash += 1
        return True
    
    def AverageMobile(self, nb):
        list_price_close = []
        for i in range (1, nb):
            list_price_close.append(float(self.values[-i]['close']))
        return sum(list_price_close) / len(list_price_close)

    def AverageVol(self):
        vol = [candle['volume'] for candle in self.values]
        return sum(vol) / len(vol)

    def CalculPotentielCapital(self):
        self.capital = self.stacks['BTC'] * self.values[-1]['close'] + self.stacks['USDT']

    def MakeADecision(self):
        nb = ((self.stacks['USDT'] * 0.4) / self.values[-1]['close'])
        nb = round(nb, 3)
        ok = self.DetectCrashMarket()
        a = self.CalculPotentielCapital()
        LAver = self.AverageMobile(10)
        curr_Vol = self.values[-1]['volume']
        avVol = self.AverageVol()

        if (self.stacks['USDT'] > (self.stack + 10)):
            print("pass", flush=True)
            return

        if (((self.IndicOBV == "hausse" and self.values[-1]['close'] > LAver and curr_Vol > avVol) or ok == True or self.capital > self.stack) and self.stacks['BTC'] != 0):
            print("sell", self.pair, self.stacks['BTC'], flush=True)
        elif (nb <= 0 or ok == True):
            print("pass", flush=True)
            return
        elif ((self.IndicOBV == "baisse" and self.values[-1]['close'] < LAver and curr_Vol < avVol) and ok == False):
            print("buy", self.pair, nb, flush=True)
        else:
            print("pass", flush=True)
        return

trade = Trade()

for s in sys.stdin:
    if (s.split(" ")[0] == "settings"):
        trade.Settings(s)
        continue
    if (s.split(" ")[2] == "next_candles"):
        trade.UpdateCandlesValues(s)
        continue
    if (s.split(" ")[:2] == ["action","order"]):
        trade.MakeADecision()
        continue
    if (s.split(" ")[2] == "stacks"):
        trade.UpdateStacks(s)
        continue