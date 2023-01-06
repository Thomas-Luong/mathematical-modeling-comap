# Tynan McGee, Thomas Luong
# 2/19/2022
# Math Modeling Competition Problem C

# Given a set of data for the price of gold and bitcoin
# on certain dates from 2016-2021, make decisions about whether
# to hold, buy, or sell

import random
import numpy as np
import matplotlib.pyplot as plt
import csv

from sympy import E

def get_data_list():
    # get the gold list and bitcoin list, modify
    # them so that they line up, and return them
    # retrieve the data from the files
    bitcoin_list = []
    gold_list = []
    with open('BCHAIN-MKPRU.csv', 'r') as bitcoin_data, open('LBMA-GOLD.csv', 'r') as gold_data:
        bitcoin_list.extend(list(csv.reader(bitcoin_data)))
        gold_list.extend(list(csv.reader(gold_data)))
    
    # modify gold list to make the dates line up with the bitcoin list
    for i in range(len(bitcoin_list)):
        if gold_list[i][1] == '':
            gold_list[i] = False
        # check if the dates are the same
        elif bitcoin_list[i][0] != gold_list[i][0]:
            gold_list.insert(i, False)
    # remove headers
    bitcoin_list.pop(0)
    gold_list.pop(0)
    return bitcoin_list, gold_list

def get_std_dev(running_changes, todays_change):
    # get the standard deviation, xbar, and num of deviations away from xbar
    # and return them
    s30 = 0
    xbar30 = 0
    n30 = 0
    s7 = 0
    xbar7 = 0
    n7 = 0
    nonzero_entries = [i for i in running_changes if i != 0]
    if len(nonzero_entries) != 0:
        s30 = np.std(nonzero_entries)
        xbar30 = sum(nonzero_entries) / len(nonzero_entries)
        s7 = np.std(nonzero_entries[-7:])
        xbar7 = sum(nonzero_entries[-7:]) / len(nonzero_entries[-7:])
        if s30 != 0:
            n30 = (todays_change - xbar30) / s30
            n7 = (todays_change - xbar7) / s7
    return s30, xbar30, n30, s7, xbar7, n7
    
def buy_or_sell_1(n):
    # strategy 1 for buying or selling, based on
    # number of standard deviations away from the mean
    buy = False
    sell = False
    # strategy 1:
    if n > 1 and n < 2:
        pass
        # buy = True
    elif n > 2:
        buy = True
    #######
    if n < -1 and n > -2:
        pass
        # sell = True
    elif n < -2:
        sell = True
    return buy, sell

def buy_or_sell_2(s, xb):
    # strategy 2 for whether to buy or sell, based on
    # size of standard deviation and sign of the mean
    buy = False
    sell = False
    if s < 20:
        # prices have been mostly stable
        if xb < -1:  # price has been going down by 1
            buy = True
        elif xb > 1:  # price has been going up by 1
            sell = True
    return buy, sell

def buy_or_sell_3(s, xb, price):
    # strategy 3 for whether to buy or sell, based on
    # semi-randomly predicted future price
    buy = False
    sell = False
    r = random.random()  # between 0 and 1
    # r = random.uniform(-1,1)  # between -1 and 1
    predicted_change = xb + (s*r)
    pct_change = predicted_change / price
    if pct_change > 0.05:
        buy = True
    elif pct_change < -0.05:
        sell = True
    return buy, sell, pct_change

def buy_or_sell_4(s30, xb30, s7, xb7, price):
    # strategy 4, using a separate 30-day average alongside the
    # 7-day average
    buy = False
    sell = False
    r = random.random()
    predicted_change7 = xb7+ (s7*r)
    pct_change7 = predicted_change7 / price
    predicted_change30 = xb30+ (s30*r)
    pct_change30 = predicted_change30 / price
    if pct_change7 - pct_change30 > -0.05:
        buy = True
    elif pct_change7 - pct_change30 < 0.05:
        sell = True
    return buy, sell, pct_change7 - pct_change30
        

def sell(C, num_on_hand, price, commission_price, bought_price, bought_factor):
    # figure out whether to sell based on how much you'd gain
    sold = False
    amount_to_gain = num_on_hand*(price - commission_price)
    if amount_to_gain > bought_factor*bought_price:
        C += amount_to_gain
        num_on_hand = 0
        sold = True
    return C, num_on_hand, sold

def buy(C, price, commission_pct, commission_price, proportion_factor):
    # figure out how much to buy and how much it costs
    amount = C / (proportion_factor*(price*(1+commission_pct)))
    price_of_buy = amount*commission_price + amount*price
    return amount, price_of_buy

def do_everything(C, N, running_changes, price, change, commission_pct, price_bought):
    bought = False
    sold = False
    visual = 0
    # get std dev, xbar, and num of devations away
    std_dev_30, xbar_30, deviations_away_30, std_dev_7, xbar_7, deviations_away_7 = get_std_dev(running_changes, change)
    # decide whether to buy or sell
    am_buying, are_selling = buy_or_sell_1(deviations_away_7)
    # am_buying, are_selling = buy_or_sell_2(std_dev_7, xbar_7)
    # am_buying, are_selling, visual = buy_or_sell_3(std_dev_7, xbar_7, price)
    # am_buying, are_selling, visual = buy_or_sell_4(std_dev_30, xbar_30, std_dev_7, xbar_7, price)
    # figure out how much money we'll have after selling
    commission = commission_pct*price
    to_buy = 0
    if are_selling:
        C, N, sold = sell(C, N, price, commission, price_bought, 1)
    if am_buying and C > 1e-5:
        to_buy, price_bought = buy(C, price, commission_pct, commission, 1)
        bought = True
    # if am_buying and C < 1e-5:
    #     print('sad')
    # update C based on the amount to buy
    C = C - to_buy*commission - to_buy*price
    N += to_buy
    # keep track of running average (changes)
    del running_changes[0]
    running_changes.append(change)

    return C, N, running_changes, price_bought, bought, sold, visual

def optimal(C, N, price, change, commission_pct, optimal_days, day_num):
    to_buy = False
    to_sell = False
    if day_num in optimal_days:
        if C < 1e-5:
            to_sell = True
        else:
            to_buy = True

    commission_price = commission_pct*price
    if to_buy:
        amount, price_of_buy = buy(C, price, commission_pct, commission_price, 1)
        C = C - amount*commission_price - amount*price
        N += amount
    elif to_sell:
        C, N, sold = sell(C, N, price, commission_price, 0, 1)
    return C, N, to_buy, to_sell
    
    
    
    
# =========================================================
# =========================================================
# =========================================================

def main():
    ending_stats = []
    optimal_days = [
        1,
        274,
        310,
        356,
        370,
        462,
        513,
        541,
        576,
        602,
        657,
        688,
        826,
        1020,
        1051,
        1063,
        1194,
        1253,
        1280,
        1582,
        1601,
        1626,
        1633,
        1646,
        1658,
        1677,
        1689,
        1702,
        1775,
        1823
    ]
    for l in range(len(optimal_days)):
        optimal_days[l] -= 1
        
    for i in range(1):
        # C = $USD, G = troy ounces of gold, B = # of bitcoins
        C, G, B = 1000, 0, 0
        portfolio = [C, G, B]
        ab = 0.02  # commission price of btc
        ag = 0.01  # commission price of gold
        gold_change = 0
        btc_change = 0
        btc_list, gold_list = get_data_list()
        btc_price = float(btc_list[0][1])
        gold_price = float(gold_list[1][1])
        portfolio_history = [portfolio]
        btc_running_changes = [0] * 30
        gold_running_changes = [0] * 30
        btc_price_bought = 0
        gold_price_bought = 0
        day_number = 0
        btc_bought_days = []
        btc_sold_days = []
        gold_bought_days = []
        gold_sold_days = []
        visual_y_axis = []
        # print(portfolio)

        for line in zip(btc_list, gold_list):
            # line is a tuple ([btc_date, btc_price], [gold_date, gold_price])
            can_trade_gold = bool(line[1])  # either False or a str
            # can_trade_gold = False
            temp_btc_price = float(line[0][1])
            btc_change = temp_btc_price - btc_price
            btc_price = temp_btc_price
            gold_bought = False
            gold_sold = False
            if can_trade_gold:
                temp_gold_price = float(line[1][1])
                gold_change = temp_gold_price - gold_price
                gold_price = temp_gold_price
                C, G, gold_running_changes, gold_price_bought, gold_bought, gold_sold, visual = do_everything(C, G, gold_running_changes, gold_price, gold_change, ag, gold_price_bought)
            
            C, B, btc_running_changes, btc_price_bought, btc_bought, btc_sold, visual = do_everything(C, B, btc_running_changes, btc_price, btc_change, ab, btc_price_bought)
            # visual_y_axis.append(visual)
            # C, B, btc_bought, btc_sold = optimal(C, B, btc_price, btc_change, ab, optimal_days, day_number)


            # update portfolio if it's different
            portfolio = [C, G, B]
            if portfolio != portfolio_history[-1]:
                print(day_number, portfolio)
                portfolio_history.append(portfolio)
            if btc_bought:
                btc_bought_days.append(day_number)
            if btc_sold:
                btc_sold_days.append(day_number)
            if gold_bought:
                gold_bought_days.append(day_number)
            if gold_sold:
                gold_sold_days.append(day_number)
            day_number += 1

        print(len(portfolio_history))
        ending_stats.append(portfolio)
        # print(i)
    
    # make the plot and show it
    fig, axs = plt.subplots(2, 1)
    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1)
    axs[0].set_title('Gold')
    axs[1].set_title('Bitcoin')
    # ax.set_title('"Optimal" Strategy (ends with $61,396,361)')
    btc_x_axis = [i for i in range(len(btc_list))]
    gold_x_axis = [i for i in range(len(gold_list))]
    btc_y_axis = []
    gold_y_axis = []
    btc_bought_y_axis = []
    btc_sold_y_axis = []
    gold_bought_y_axis = []
    gold_sold_y_axis = []
    for day in btc_list:
        btc_y_axis.append(float(day[1]))
    for i,day in enumerate(gold_list):
        if i == 0:
            gold_y_axis.append(1324.6)
            continue
        if type(day) == bool:
            n = 1
            while type(gold_list[i-n]) == bool:
                n += 1
            gold_y_axis.append(float(gold_list[i-n][1]))
        else:
            gold_y_axis.append(float(day[1]))
    for day in btc_bought_days:
        btc_bought_y_axis.append(btc_y_axis[day])
    for day in btc_sold_days:
        btc_sold_y_axis.append(btc_y_axis[day])
    for day in gold_bought_days:
        gold_bought_y_axis.append(gold_y_axis[day])
    for day in gold_sold_days:
        gold_sold_y_axis.append(gold_y_axis[day])
        
    axs[0].plot(gold_x_axis, gold_y_axis, 'b', label='Price of Gold')
    axs[0].plot(gold_bought_days, gold_bought_y_axis, 'ro', label='Buy')
    axs[0].plot(gold_sold_days, gold_sold_y_axis, 'go', label='Buy')
    axs[0].set_ylabel('Price of Gold (USD)')
    axs[0].set_xlabel('Day # (since 9/11/2016)')

    axs[1].plot(btc_x_axis, btc_y_axis, 'b', label='Price of Bitcoin')
    axs[1].plot(btc_bought_days, btc_bought_y_axis, 'ro', label='Buy')
    axs[1].plot(btc_sold_days, btc_sold_y_axis, 'go', label='Buy')
    axs[1].set_ylabel('Price of Bitcoin (USD)')
    axs[1].set_xlabel('Day # (since 9/11/2016)')

    # ax.plot(btc_x_axis, btc_y_axis, 'b', label='Price of Bitcoin')
    # ax.plot(btc_bought_days, btc_bought_y_axis, 'ro', label='Buy')
    # ax.plot(btc_sold_days, btc_sold_y_axis, 'go', label='Buy')
    # ax.set_ylabel('Price of Bitcoin (USD)')
    # ax.set_xlabel('Day # (since 9/11/2016)')
    # ax.legend(loc='upper left')

    axs[0].legend(loc='upper left')
    axs[1].legend(loc='upper left')
    plt.show()
    
    max_btc = 0
    avg_btc = 0
    for run in ending_stats:
        avg_btc += run[2]
        if run[2] > max_btc:
            max_btc = run[2]
    avg_btc /= len(ending_stats)
    print(avg_btc)
    print(max_btc)

    # print(ending_stats)
        

if __name__ == '__main__':
    main()