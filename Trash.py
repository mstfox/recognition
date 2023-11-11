if request.method == 'POST':
        if 'form1' in request.form:
          vallimit = request.form['vallimit']
          ratio = request.form['ratio']
          ARR = request.form['ARR']
          DF = CoveredCAll(float(vallimit.replace(',','')), float(ratio)/100, float(ARR.replace(',','')))
    
        else: 
            sel_ULA     = request.form.getlist('ULA')
            sel_types   = request.form.getlist('mdates')
            sel_options = request.form.getlist('options')
            options = list(set(DF[DF.UAIndx.isin(sel_ULA)]['Indx']))
            mdates   = set(DF[DF.UAIndx.isin(sel_ULA)]['Date'].tolist())


#Filter_
VTB = ''
    for i in range(len(data.columns)):
        VTB += '<th onclick="sortTable({})">{}</th>'.format(str(i) , data.columns[i])





if request.method == 'POST':
        sel_ULA     = request.form.getlist('ULA')
        sel_mdates = request.form.getlist('mdates')
        sel_Zones = request.form.getlist('Zones')

    LL=[]
    for i in sel_Zones:
        if i == 'Zone I':
            LL.append(0)
        elif i == 'Zone II':
            LL.append(1)

    data = DF[DF.UAIndx.isin(sel_ULA)][DF.state.isin(LL)][DF.Date.isin(sel_mdates)]
    data = data[['UAIndx' , 'UAsellprice', '1stopt', '1ststrike' ,'1stoptbuypr', '2ndopt', '2ndstrike' ,'2ndoptsellpr' ,'DaystoMat' , 'Date' , 'Max YTM' , 'A Yield']]   
    #Place Here
    
    #data , datatbl = filter_(DF, sel_options)