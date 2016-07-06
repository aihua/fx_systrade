#!/usr/bin/python
from math import log

INIT_BALANCE = 500000
balance = INIT_BALANCE
MARGIN_RATE = 0.04
HALF_SPREAD = 0.015 #0.015
BUY_LOTS = 1000 #1000
WON_PIPS = 0.3

def get_tuned_percent(baseline_price):
    #return 1
    return 1/((baseline_price/140)*2)
    #return (140 - (baseline_price - 80))/140

def get_baseline_lots(portfolio, cur_price):
    return BUY_LOTS
#    return BUY_LOTS * (balance/INIT_BALANCE) * 0.8

"""
main
"""
rates_fd = open('./hoge.csv', 'r')
exchange_dates = []
exchange_rates = []
for line in rates_fd:
    splited = line.split(",")
    if splited[2] != "High" and splited[0] != "<DTYYYYMMDD>"and splited[0] != "204/04/26" and splited[0] != "20004/04/26":
        time = splited[0].replace("/", "-") + " " + splited[1]
        val = float(splited[2])
        exchange_dates.append(time)
        exchange_rates.append(val)

data_len = len(exchange_rates)

print "data size: " + str(data_len)

center_val = int(exchange_rates[0])
traps = []

start = 80
end = 120
step = 0.1
for price in xrange(100*start, 100*end, int(100*step)):
    traps.append([price/100, False, False, 0])

positions = 0
for cur in xrange(1, data_len):
    is_print = False
    diff = exchange_rates[cur] - exchange_rates[cur-1]

    #if no position, buy it
    for idx in xrange(len(traps)):
        if traps[idx][0] > (exchange_rates[cur-1]+HALF_SPREAD) \
           and traps[idx][0] <= (exchange_rates[cur]+HALF_SPREAD) \
           and traps[idx][1] == False \
           and positions <= 40:
            traps[idx][1] = True
            traps[idx][3] = exchange_rates[cur]

    # close position
    for idx in xrange(len(traps)):
        if traps[idx][1] == True:
            if (exchange_rates[cur]-HALF_SPREAD) - traps[idx][3] > WON_PIPS:
                balance += ((exchange_rates[cur]-HALF_SPREAD) - traps[idx][3]) \
                           * get_baseline_lots(portfolio, traps[idx][3]) \
                           * get_tuned_percent(traps[idx][3])
                traps[idx][1] = False
                traps[idx][2] = False
                traps[idx][3] = 0
                is_print = True

    margin_used = 0
    profit_or_loss = 0
    positions = 0
    for idx in xrange(len(traps)):
        if traps[idx][1] == True:
            margin_used += (traps[idx][3] *\
                            get_baseline_lots(portfolio, traps[idx][3]) \
                              * get_tuned_percent(traps[idx][3])) * MARGIN_RATE
            profit_or_loss += ((exchange_rates[cur]-HALF_SPREAD) - traps[idx][3]) \
                              * get_baseline_lots(portfolio, traps[idx][3]) \
                              * get_tuned_percent(traps[idx][3])
            positions += 1
            
    portfolio = balance + profit_or_loss - margin_used

    if portfolio < 0:
        print exchange_dates[cur] + " " + str(positions) + " " + str(margin_used) + " " + str(portfolio) + " " + str(balance)
        print "dead"
        break

    # print current status
    if is_print == True:
        print exchange_dates[cur] + " " + str(positions) + " " + str(margin_used) + " " + str(portfolio) + " " + str(balance)
