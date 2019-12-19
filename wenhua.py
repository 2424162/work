from tqsdk import TqApi,TqSim
from tqsdk import *
from tqsdk.tafunc import *
from tqsdk.ta import ATR

品种 = "SHFE.cu2001"
period = 60
当前状态 = "等待开仓"
def get_open(signal):
    klines = api.get_kline_serial(品种,period,)
    quote = api.get_quote(品种)
    atr = ATR(klines,30)
    TR1 = atr.tr
    ATR1 = atr.atr
    #print(ATR1.values)
    kl = klines.set_index("datetime")
    yes = api.get_kline_serial(品种, 60 * 60 * 24)
    time1 = yes.datetime.iloc[-1]
    day_num = yes.datetime.iloc[-1] - yes.datetime.iloc[-2]
    print(day_num)
    NN = len(klines[(klines['datetime'] > time1) & (klines['datetime'] < time1 + day_num)])
    print('NN',NN)
    H1 = ref(hhv(klines.high, NN), NN) #昨序列
    print(klines.high)
    print("HHV",hhv(klines.high, NN))
    print("H1",H1)
    L1 = ref(llv(klines.low, NN), NN)
    O2 = klines[(klines['datetime'] > time1) & (klines['datetime'] < time1 + day_num)].iloc[0].open
    print(O2)
    if (ATR1.values[-1]>21):
        print('hhaha',ATR1.values[-1])
        KK1 = 3
    else:
        KK1 = 5
    if (ATR1.values[-1]>21):
        KK2 = 3
    else:
        KK2 = 5
    HH = O2 + (H1-L1)*KK1*0.1
    print("____________H1-L1",H1-L1)
    print("HH:",HH,type(HH))
    LL = O2 - (H1-L1)*KK2*0.1
    print('LL',LL)
    DAYBARPOS = len(klines[klines['datetime'] > time1])
    print("daybarpos",DAYBARPOS)
    HH1 = hhv(klines.high,DAYBARPOS)
    LL1 = llv(klines.low,DAYBARPOS)
    UU = HH - LL
    print("HH1:",HH1)
    C = quote.close
    KDTJ = all(((C>=HH).values[-1],(H1!=L1).values[-1],llv(klines.low,NN)>(O2-(H1-L1)*KK1*0.1),UU<55,UU>15))
    KKTJ = all((C<=HH,H1!=L1,hhv(klines.high,NN)<(O2+(H1-L1)*KK1*0.1),UU<55,UU>15))
    SP_1 = all((TR1>18,klines.low<=O2-(H1-L1)*8*0.1))
    BP_1 = all((TR1>18,klines.high>=O2+(H1-L1)*8*0.1))
    dict1 = {"KDTJ":KDTJ,"KKTJ":KKTJ,"SP":SP_1,"BP":BP_1}
    return dict1[signal]

def open_judge():
    global 当前状态
    if 当前状态 == "等待开仓":
        if get_open("KDTJ"):
            api.insert_order(symbol=品种, direction="BUY", offset="OPEN", volume=1)
            BKPRICE = api.get_quote(品种).last_price
            当前状态 = '已开多仓等待平仓'
        if get_open("KKTJ"):
            api.insert_order(symbol=品种,direction="SELL",offest="OPEN",volume=1)
            当前状态 = '已开空仓等待平仓'
            SKPRICE =api.get_quote(品种).last_price
def close_out(品种):
    data = api.get_position(品种)
    多仓1 = data['pos_long_his']
    多仓2 = data['pos_long_today']
    空仓1 = data['pos_short_his']
    空仓2 = data['pos_short_today']
   # 委托此时最低值 = api.get_kline_serial(品种, 指定返回的周期)['close'].tolist()[-1]
  #  f.write("平仓价格:" + str(委托此时最低值) + '\n')

    if 多仓1 != 0:
        api.insert_order(symbol=品种, direction="SELL", offset="CLOSE", volume=多仓1)
    if 多仓2 != 0:
        if 品种[:4] == "SHFE":
            api.insert_order(symbol=品种, direction="SELL", offset="CLOSETODAY", volume=多仓2)
        else:
            api.insert_order(symbol=品种, direction="SELL", offset="CLOSE", volume=多仓2)
    if 空仓1 != 0:
        api.insert_order(symbol=品种, direction="BUY", offset="CLOSE", volume=空仓1)
    if 空仓2 != 0:
        if 品种[:4] == "SHFE":
            api.insert_order(symbol=品种, direction="BUY", offset="CLOSETODAY", volume=空仓2)
        else:
            api.insert_order(symbol=品种, direction="BUY", offset="CLOSE", volume=空仓2)

def close_judge():
    global 当前状态
    if 当前状态 == "已开多仓等待平仓":
        if get_open("BP"):
            close_out(品种)
    if  当前状态 == "已开空仓等待平仓":
        if get_open("SP"):
            close_out(品种)


api = api.TqApi(TqSim())
klines = api.get_kline_serial(品种,period)

#kline_count()
open_judge()
close_judge()
while True:
    api.wait_update()
    print()
