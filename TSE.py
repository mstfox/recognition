import requests
import pandas as pd
import xmltodict
from datetime import datetime
import json
from pathlib import Path
from datetime import datetime
import jdatetime
import numpy as np

def jalali():
    GDate = str(datetime.now())
    C = str(jdatetime.date.fromgregorian(day= int(GDate.split()[0].split('-')[2]), month= int(GDate.split()[0].split('-')[1]), year= int(GDate.split()[0].split('-')[0])))
    return C + ' ' + GDate.split()[1].split('.')[0]

def JL(D):
    D=str(D)
    Y = int(D[:4])
    M = int(D[4:6])
    D3 = int(D[6:])
    return str(jdatetime.date.fromgregorian(day= D3, month= M, year= Y))

def multi(DF , P1 ,vol1 , P2 , vol2 , pnet , volnet):
    for i in range(len(DF)):

        if DF.iloc[i][P1] <3:
            DF.loc[i,pnet] , DF.loc[i,volnet] = 0 ,0
        elif abs(DF.iloc[i][P1] - DF.iloc[i][P2])>3:
            DF.loc[i,pnet] , DF.loc[i,volnet] = DF.iloc[i][P1] , DF.iloc[i][vol1]
        else:
        
            DF.loc[i,pnet] = ((DF.iloc[i][P1]*DF.iloc[i][vol1] + DF.iloc[i][P2]*DF.iloc[i][vol2])/(DF.iloc[i][vol1]+DF.iloc[i][vol2])).round(1)
            DF.loc[i,volnet] = (DF.iloc[i][vol1]+DF.iloc[i][vol2])
    return DF

def CalcWA(DF):
    DF = multi(DF , 'OptnFrstOrderSellPrice' , 'OptnFrstOrderSellVol' , 'OptnscndOrderSellPrice' , 'OptnscndOrderSellVol' , 'OptionSellPrice' , 'OptnSellVol' )
    DF = multi(DF , 'OptnFrstOrderBuyPrice' , 'OptnFrstOrderBuyVol' , 'OptnscndOrderBuyPrice' , 'OptnscndOrderBuyVol' , 'OptionBuyPrice' , 'OptnBuyVol' )   
    return DF







#############################
#############################
#### Laterals ###############

def Colrename(DF):
    #DF = OptionsDF
    Correspond = pd.read_excel(Path(__file__).parent/'static/KSA.xlsx')
    cols=[]
    dropcols = []
    for i in DF.columns:

        try:
            cols.append(list(Correspond['Second'][Correspond['First'] == i])[0])
        except:
            dropcols.append(i)
    DF = DF.drop(columns = dropcols)
    DF.columns = cols
    return DF.reset_index(drop =True)

def Responsepost(url , SOAPEnvelope , options):
    flag = True
    Counter_  = 0
    while flag and Counter_<10:
        try:
            Response = requests.post(url, data = SOAPEnvelope , headers = options)
            flag  = False
        except:
            print('Trying to get aggregate Options List')
            Counter_ += 1
    if flag:
        print('The connection is impaired. failed tries to get option list!')
    return Response

def Responseget(url):
    flag = True
    Counter_  = 0
    while flag and Counter_<10:
        try:
            Response = requests.get(url, headers = {'User-Agent': 'Some user agent'}, timeout = 2)
            flag  = False
        except:
            print('Trying to get aggregate List')
            Counter_ += 1
    if flag:
        print('The connection is impaired. failed tries to get option list!')
    return Response




def Order_(list_):
    try:
        return list_[0]['pmo'] , list_[0]['qmo'] , list_[0]['pmd'] , list_[0]['qmd'] , list_[1]['pmo'] , list_[1]['qmo'] , list_[1]['pmd'] , list_[1]['qmd']
    except:
        return list_[0]['pmo'] , list_[0]['qmo'] , list_[0]['pmd'] , list_[0]['qmd'] , 0, 0, 0, 0

    
    
def Type(df , colname):
    TypeList = []
    Ref = pd.read_excel(Path(__file__).parent/'static/KSA.xlsx')
    for i in df[colname]:
        for idj , j in enumerate(Ref.First):
            if j in i: 
               TypeList.append(Ref.Second[idj])
               break
    df['Type'] = TypeList
    return df

def DateDif(i):
    return (datetime.strptime(str(i), '%Y%m%d') - datetime.today()).days+1





def Calcs(DF):
    #DF = Merge
    DF['RtoMatu'] , DF['DaystoMatu'] =  (DF.StrikePrice.astype(float) / (DF.UABuyPrice- DF.OptionSellPrice) -1)*100 , DF['EndDate'].map(DateDif)
    DF['ARR'] = ((1+(DF.RtoMatu)/100)**(365/DF.DaystoMatu) -1) *100
    return DF

#############################
#############################

def AllData():
    #url2 ='http://cdn.tsetmc.com/api/ClosingPrice/GetMarketWatch?market=0&industrialGroup=&paperTypes%5B0%5D=6&paperTypes%5B1%5D=1&paperTypes%5B2%5D=2&showTraded=false&withBestLimits=true'
    url2 = 'http://cdn.tsetmc.com/api/ClosingPrice/GetMarketWatch?market=0&industrialGroup=&paperTypes%5B0%5D=1&paperTypes%5B1%5D=2&paperTypes%5B2%5D=6&paperTypes%5B3%5D=8&showTraded=false&withBestLimits=true'
    MM = Colrename(pd.DataFrame.from_dict(Responseget(url2).json()['marketwatch']))
    MM['BuyPr1order'] , MM['BuyVol1order'] , MM['SellPr1order'] , MM['SellVol1order'], MM['BuyPr2order'] , MM['BuyVol2order'] , MM['SellPr2order'] , MM['SellVol2order']= zip(*MM['Orders'].map(Order_))
    return MM
### Get All Options List 


def GetOptionsList():
    
    url = 'http://service.tsetmc.com/WebService/TsePublicV2.asmx'
    SOAPEnvelope = """<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <Option xmlns="http://tsetmc.com/">
          <UserName>shetabNitrogen</UserName>
          <Password>shetabNitrogen</Password>
        </Option>
      </soap:Body>
    </soap:Envelope>
    """
    options = {"Content-Type": "text/xml; charset=utf-8"}
    OptionsDF = Colrename(pd.DataFrame.from_dict(xmltodict.parse(Responsepost(url , SOAPEnvelope , options).content)['soap:Envelope']['soap:Body']['OptionResponse']['OptionResult']['diffgr:diffgram']['Option']['Option']))         
    return OptionsDF

### Get Limit Orders
def GetUpdateoptn():
    MM = AllData()
    OptionsDF = GetOptionsList()
    OptionsDF['InsCode'] = OptionsDF['InsCode'].astype(str)
    Cols = ['InsCode_x', 'InstrumentID','Indx_y', 'IndxPer','TradesVol', 'ContractSize', 'OpenInterest', 'StrikePrice', 'SellPr1order', 'SellVol1order', 'SellPr2order', 'SellVol2order', 'BuyPr1order_y', 'BuyVol1order', 'BuyPr2order', 'BuyVol2order' ,'BeginDate', 'EndDate', 'UAInsCode',  'Indx_x', 'BuyPr1order_x']
    Merge = pd.merge(OptionsDF, MM[['InsCode' , 'Indx' , 'BuyPr1order']], left_on= 'UAInsCode' , right_on='InsCode')
    Merge  = pd.merge(Merge, MM[['InsCode' , 'Indx','IndxPer' ,'TradesVol', 'SellPr1order', 'SellVol1order', 'SellPr2order', 'SellVol2order' , 'BuyPr1order', 'BuyVol1order', 'BuyPr2order', 'BuyVol2order']], left_on= 'InsCode_x' , right_on='InsCode')[Cols]
    Merge = Type(Merge , 'IndxPer')  
    Cols = ['InsCode', 'InstrumentID','Indx', 'IndxPer','TradesVol', 'ContractSize', 'OpenInterest','StrikePrice', 'OptnFrstOrderSellPrice', 'OptnFrstOrderSellVol', 'OptnscndOrderSellPrice', 'OptnscndOrderSellVol', 'OptnFrstOrderBuyPrice', 'OptnFrstOrderBuyVol', 'OptnscndOrderBuyPrice', 'OptnscndOrderBuyVol', 'BeginDate', 'EndDate', 'UAInsCode',  'UAIndx', 'UABuyPrice', 'Type']
    Merge.columns = Cols
    Merge = CalcWA(Merge)
    Merge = Calcs(Merge)
    Merge.RtoMatu = Merge.RtoMatu.round(1)
    Merge.ARR = Merge.ARR.round(1)
    Merge.OptionSellPrice = Merge.OptionSellPrice.round(1)
    Merge['Date'] = Merge.EndDate.apply(JL)
    Merge.to_excel(Path(__file__).parent/'static/Updated.xlsx', index=False)
    file = open(Path(__file__).parent/'static/Date.txt', 'w')
    file.write(jalali())
    file.close()  
    return Merge

def CoveredCAll(Vallimit = 500000000, Ratio = .9, arr = 50):
    Merge = pd.read_excel(Path(__file__).parent/'static/Updated.xlsx')
    Merge = Merge[~Merge.Type.str.contains('فروش')]
    Merge = Merge[(Merge.OptnSellVol*Merge.ContractSize.astype(float)*(Merge.UABuyPrice - Merge.OptionSellPrice)>= Vallimit) & (Merge.StrikePrice.astype(float)/Merge.UABuyPrice<Ratio) & (Merge.ARR>arr)]
    Merge.to_excel(Path(__file__).parent/'static/CoveredCall.xlsx', index=False)
    return Merge

def BullCall():
    Merge = pd.read_excel(Path(__file__).parent/'static/Updated.xlsx')
    Merge = Merge[Merge.Type == 'اختیار خرید']
    Dic={}
    for indx in list(set(Merge.UAIndx)):
        Dic01={}
        Temp = Merge[Merge.UAIndx == indx]
        flag = False
        for matu_date in  list(set(Temp.EndDate)):
            Temp1 = Temp[Temp.EndDate == matu_date]
            
            if len(Temp1) >1:
               Dic01[matu_date] = Temp1.reset_index(drop=True)
               flag= True
        if flag:
            Dic[indx] =  Dic01       

    cols = ['Date', 'DaystoMat' , 'UAIndx' , 'UAsellprice', '1stopt', '1ststrike', '1stoptbuypr', '1stoptbuyvol' ,'2ndopt' , '2ndstrike', '2ndoptsellpr', '2ndoptsellvol' ,'ContractSize', 'state']
    mainDF = pd.DataFrame(columns = cols)
    for i in Dic:
        #i = 'اهرم'
        #j = 20231015
        for j in Dic[i]:
            FG = Dic[i][j].sort_values('StrikePrice')
            for k in range(len(FG)-1):
                for l in range(k+1,len(FG)):
                    if (FG.iloc[k]['OptionBuyPrice'] * FG.iloc[l]['OptionSellPrice']!=0) and (FG.iloc[0]['UABuyPrice'] >= FG.iloc[k]['StrikePrice']) :
                        if FG.iloc[0]['UABuyPrice']>FG.iloc[l]['StrikePrice']:
                            State = 'Zone II'
                        else:
                            State = 'Zone I'
                        
                        List = [0]*len(cols)
                        List = [FG.iloc[0]['Date'],
                                FG.iloc[0]['DaystoMatu'],
                                i,
                                FG.iloc[0]['UABuyPrice'],
                                
                                FG.iloc[k]['Indx'],
                                FG.iloc[k]['StrikePrice'],
                                FG.iloc[k]['OptionBuyPrice'],
                                FG.iloc[k]['OptnBuyVol'],
                                
                                
                                FG.iloc[l]['Indx'],
                                FG.iloc[l]['StrikePrice'],
                                FG.iloc[l]['OptionSellPrice'],
                                FG.iloc[l]['OptnSellVol'],
                                FG.iloc[0]['ContractSize'],
                                State  ]
                        mainDF.loc[len(mainDF)] = List      
    mainDF['Max YTM'] = (((mainDF ['2ndstrike'] - mainDF ['1ststrike'])/(mainDF['1stoptbuypr']-mainDF['2ndoptsellpr'])-1)*100).round(1)
    mainDF['Tradecost'] = mainDF[['1stoptbuyvol','2ndoptsellvol']].min(axis=1)*mainDF['ContractSize']*(mainDF['1stoptbuypr']-mainDF['2ndoptsellpr'])
    mainDF['A Yield'] = (((1+ mainDF['Max YTM']/100)**(365/mainDF['DaystoMat']) -1)*100).round(1)
    mainDF.to_excel(Path(__file__).parent/'static/BullCall.xlsx')
    return mainDF
