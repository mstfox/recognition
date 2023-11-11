import pandas as pd
from pandas import read_excel
import os
import requests
import pandas as pd
import xmltodict
from datetime import datetime
import json
from pathlib import Path
from datetime import datetime
import jdatetime
import numpy as np


path_= Path(__file__).parent/'uploads'

def rplc(st):
    dic = { 
        'واریز از طریق': '',
        ' بابت پیام ': '',
        ' بانک ملي ': '',
        'بانک قرض الحسنه رسالت': '',
        ' شماره پیگیری ': '',
        ' بانک ملت ': '',
        ' بانک سپه ': '',
        ' واریز  پایا ': '',
        'واریز پایا ': '',
        ' بانک پارسيان ': '',
  'بانک گردشگري':'',
  'قرض الحسنه':'',
  'بانک':'',
  '':'',
  '':'',

  
        
        
        
 'ئ':'ی',
 'ك': 'ک' ,
 'آ': 'ا',        
        'ي':'ی',
           '_':' ',
           '-':' ',
           '*':' ',
           ',' :'',
         
           'سید':'',
           'سیده': '',
           'سادات':'',
           'السادات':'',
         
           
           
           '  ': '',
           ' ': '',
           'ِ': '',
           'ُ': '',
           'َ': '',
          
           
          }
    if type(st) == str:
        for i in dic:
            st = str(st).replace(i, dic[i])
            try:
                st = int(st)
            except:
                continue
    return st

def name(DF , G):
    List =[]
    for i in DF[DF.columns[G]]:
        try:
            
            List.append(i.replace(' ' , '/'))
        except:
            List.append('')
    DF[DF.columns[G]] = List
    return DF

def chckif(str_ , D1):
    # str_ =i
    fl = [] 
    for idx in range(len(D1)):
        #idx = 76
        flag = 0
        Name    = D1.iloc[idx]['name']
        Surname = D1.iloc[idx]['surname']
        for k in range(len(Surname.split('/'))):
            Lan = Surname.split('/')[k]
            if (Lan in str_):
                if (Lan != ''):
                    flag += 1
            else: break
        
        #for k in range(len(Name.split('/'))):
        if (Name.split('/')[0] in str_):
                    flag += .1
        fl.append(flag)
        Max = max(fl)
        LI = []
        if Max >=1:
            for o in range(len(fl)):
                if fl[o] == Max :
                    LI.append(o)
    
    return LI


def IDCode(str_ , D1):
    # str_ = 'واریز پایانتقال وجه از سپرده 290.8000.11718626.1توسطزهره صالحی سامانه موبایل بانک' 
    fl = [] 
    for idx in range(len(D1)):
        IDCode    = str(D1.iloc[idx]['ID'])
        
        if (IDCode in str_):
                fl.append(idx)
    
    return fl

def Ind(L,C):
    indices =[]
    for i in range(len(L)):
        if L[i] == C:
            indices.append(i)
    return indices
def recognition():
    for subdir, dirs, files in os.walk(path_):
        for file in files:
            if '$' not in file:
                #print(file)
                #print(os.path.join(path_ , file))
                if list(read_excel(os.path.join(path_ , file)).iloc[1])[1] =='همه':
                    D1N = os.path.join(path_ , file)
                else: D2N = os.path.join(path_ , file)


    D1   = read_excel(D1N , skiprows = 7).iloc[:-1]
    Cols = D1.columns
    D1   = D1[[Cols[4], Cols[5], Cols[6], Cols[8], Cols[11], Cols[13], Cols[14]]]
    D1 = D1.applymap(rplc)
    D1 = name(D1 , 0)
    D1 = name(D1 , 1)


    D1.columns = ['name' , 'surname' , 'ID' , 'bnkcode' , 'IN', 'date', 'time']
    D1 = D1.reset_index()
    D1.date = D1.date.str.replace('/','').astype(int)

    D2   = read_excel(D2N , skiprows = 2).iloc[:-1]
    Cols = D2.columns
    D2  = D2[[Cols[3], Cols[4], Cols[8], Cols[10]]]
    D2.columns = ['Date' , 'Time' , 'note' , 'OUT']
    CG = D2.note
    D2 = D2.applymap(rplc)
    D2['Note'] = CG
    D2 = D2[D2.OUT != 0]
    D2 = D2.sort_values('OUT').reset_index(drop = True)
    D2.Date = D2.Date.str.replace('/','').astype(int)


    #################
    #################

    Listprfctmtch = []
    Nonmatchside1 = []
    Nonmatchside2 = []
    Multimatch    = []
    colsprfctmtch = list(D1.columns) + list(D2.columns)
    D1droplist    = []
    MainList      = []

    for idx , i in enumerate(D2.note):
        # idx = 189
        # i   = D2.note[idx]
        print(idx)
        D1temp = D1 [(D1[D1.columns[0]].isin(list(set(chckif(i , D1)+IDCode(i , D1))))) & (D1.IN == D2.iloc[idx]['OUT']) ]  #& (abs(D1.date - D2.iloc[idx]['Date']) <= 1)  
        MainList.append(list(D1temp[D1temp.columns[0]]))

    for idx in range(len(MainList)):
        #idx = 22
        Tg = len(MainList[idx])
        if   Tg == 0:
            Nonmatchside2.append(list(D2.iloc[idx]))
        elif Tg !=0 :
            indiceslist = Ind(MainList ,MainList[idx])
            if MainList.count(MainList[idx]) == Tg:
                for h in range(Tg):
                    
                    Listprfctmtch.append(list(D1.iloc[MainList[idx][h]]) + list(D2.iloc[indiceslist[h]]))
                    
            else:
                for h in range(Tg):
                    Multimatch.append(list(D1.iloc[MainList[idx][h]])    + list(D2.iloc[idx]))
            D1droplist += MainList[idx]    
        
            
    Match = pd.DataFrame(Listprfctmtch , columns= colsprfctmtch).drop_duplicates()
    Match = Match.drop(columns=['note'])
    MultiMatch = pd.DataFrame(Multimatch , columns= colsprfctmtch).drop_duplicates()
    MultiMatch = MultiMatch.drop(columns=['note'])
    NonmatchSide2  = pd.DataFrame(Nonmatchside2 , columns= D2.columns).drop_duplicates()
    NonmatchSide2  = NonmatchSide2.drop(columns=['note'])
    droplist = list(set(D1droplist))

    #list(Match[Match.columns[0]]) + list(MultiMatch[MultiMatch.columns[0]])
    NonmatchSide1 = D1.drop(index= droplist)



    ##### NonMatch second Process
    OUT = [d for d in list(NonmatchSide2.OUT) if list(NonmatchSide2.OUT).count(d) == 1]
    IN = [d for d in list(NonmatchSide1.IN) if list(NonmatchSide1.IN).count(d) == 1]
    Common = list(set(OUT).intersection(IN))
    Match.loc[len(Match)] = ['*']*12
    Match.loc[len(Match)] = ['*']*12
    Match.loc[len(Match)] = ['*']*12
    MM= [ ]
    for i in Common:

        MM.append(list(NonmatchSide1[NonmatchSide1.IN == i].iloc[0]) + list(NonmatchSide2[NonmatchSide2.OUT == i].iloc[0]))

    Match = Match.append(pd.DataFrame(MM, columns=Match.columns))
    NonmatchSide2 = NonmatchSide2[~NonmatchSide2.OUT.isin(Common)]
    NonmatchSide1 = NonmatchSide1[~NonmatchSide1.IN.isin(Common)]



    ##### NonMatch Thrid Process
    OUT2 = list(set([d for d in list(NonmatchSide2.OUT) if list(NonmatchSide2.OUT).count(d) != 1]))
    IN2 = list(set([d for d in list(NonmatchSide1.IN) if list(NonmatchSide1.IN).count(d) != 1]))
    Common2 = list(set(OUT2).intersection(IN2))

    seperator = [['*']*12, ['*']*12, ['*']*12]

    MM= [['*']*12, ['*']*12, ['*']*12]
    for i in Common2:
        Max = max(len(NonmatchSide1[NonmatchSide1.IN == i]) , len(NonmatchSide2[NonmatchSide2.OUT == i]))
        Min = min(len(NonmatchSide1[NonmatchSide1.IN == i]) , len(NonmatchSide2[NonmatchSide2.OUT == i]))
        if len(NonmatchSide1[NonmatchSide1.IN == i]) == Min:
            for K in range(Max):
                if K< Min:
                    MM.append(list(NonmatchSide1[NonmatchSide1.IN == i].iloc[K])+list(NonmatchSide2[NonmatchSide2.OUT == i].iloc[K]))
                else:
                    MM.append(['*']*8 +list(NonmatchSide2[NonmatchSide2.OUT == i].iloc[K]))
        else:
            for K in range(Max):
                if K< Min:
                    MM.append(list(NonmatchSide1[NonmatchSide1.IN == i].iloc[K])+ list(NonmatchSide2[NonmatchSide2.OUT == i].iloc[K]))
                else:
                    MM.append(list(NonmatchSide1[NonmatchSide1.IN == i].iloc[K])+ ['*']*4)
        MM += (seperator)
    MultiMatch = MultiMatch.append(pd.DataFrame(MM, columns=MultiMatch.columns))
    NonmatchSide2 = NonmatchSide2[~NonmatchSide2.OUT.isin(Common2)]
    NonmatchSide1 = NonmatchSide1[~NonmatchSide1.IN.isin(Common2)]




    import datetime
    writer = pd.ExcelWriter(Path(__file__).parent/'outputs/Recognition.xlsx', engine='xlsxwriter')
    L1=[Match, MultiMatch, NonmatchSide1, NonmatchSide2]
    L2 = ['یک به یک متناظر'  ,
        'متناظر مکرر',
        'غیر متناظر طرف اول' ,
        'غیرمتناظر طرف دوم'
        ]
    for i in range(len(L1)):
        L1[i].to_excel(writer, sheet_name=L2[i], index = False)
        workbook  = writer.book
        worksheet = writer.sheets[L2[i]]
        worksheet.right_to_left()
    writer.save()
    return  L1