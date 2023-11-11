from flask import url_for, render_template, request, redirect, session, jsonify , send_file
from functions import startup, filter_
from TSE import GetUpdateoptn, CoveredCAll ,  BullCall
from pyt import recognition
import pandas as pd
import os
from pathlib import Path

(db, app) = startup()
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/', methods=['GET' , 'POST'])
def index():
    if session.get('logged_in'):
        if request.method == 'POST':
            GetUpdateoptn()
            message = 'Just Updated'
        else:
            message = ''
        time_ = open(Path(__file__).parent/'static/Date.txt').readline()
         

        return render_template('home.html' , time_ = time_ , msg = message)
    else:
        return render_template('index.html', message="Welcome to My Platform!")



@app.route('/test', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file1' not in request.files or 'file2' not in request.files:
            return redirect(request.url)

        file1 = request.files['file1']
        file2 = request.files['file2']

        if file1 and file2:
            filename1 = os.path.join(app.config['UPLOAD_FOLDER'], '1.xlsx')
            filename2 = os.path.join(app.config['UPLOAD_FOLDER'], '2.xlsx')#file2.filename)
            file1.save(filename1)
            file2.save(filename2)
            recognition()
            

            return render_template('recognition.html', success=True)

    return render_template('recognition.html', success=False)

download_link = Path(__file__).parent/'outputs/Recognition.xlsx'
@app.route('/download')
def download_file():
    file_path = download_link 
    return send_file(file_path, as_attachment=True)




@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db.session.add(User(username=request.form['username'], password=request.form['password']))
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return render_template('index.html', message="User Already Exists")
    else:
        return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        u = request.form['username']
        p = request.form['password']
        data = User.query.filter_by(username=u, password=p).first()
        if data is not None:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('index.html', message="Incorrect Details")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))



@app.route('/CoveredCall.html', methods=['GET', 'POST'])
def CoveredCall():
    DF=pd.read_excel(Path(__file__).parent/'static/Updated.xlsx')
    ULA     = [] #list(set(DF.UAIndx))
    mdates   = [] #list(set(DF.Type))
    options = [] #list(set(DF.Indx))

    sel_ULA = ULA
    sel_mdates = mdates
    sel_options = options

    #Place Here
    
    data , datatbl = filter_(DF, sel_options)

    return render_template('CoveredCall.html' , **locals() )


@app.route('/BullCall.html', methods=['GET', 'POST'])
def BullCallSpread():
    DF = pd.read_excel(Path(__file__).parent/'static/BullCall.xlsx')
    ULA     = [] #list(set(DF.UAIndx))
    mdates = [] #list(set(DF.Date))
    Zones   = [] # ['Zone I' , 'Zone II'] #list(set(DF.Type))

    sel_ULA = ULA
    sel_mdates = mdates
    sel_Zones = Zones

    return render_template('BullCall.html' , **locals() )

@app.route('/firstformbullcall/<code>', methods=['POST', 'GET'])
def firstformbullcall(code):
    # Get the input values from the first form
    vallimit = float(code.split('&')[0].replace(',',''))
    print(vallimit)
    ARR = float(code.split('&')[1].replace(',',''))
    print(ARR)
    DF = pd.read_excel(Path(__file__).parent/'static/BullCall.xlsx')

    DF = DF[(DF['A Yield']>ARR) & (DF['Tradecost']>vallimit) & (DF['DaystoMat']> 6)]

    DF.to_excel(Path(__file__).parent/'static/BullCalltrimed.xlsx')

    return jsonify({'ULA_': list(set(DF.UAIndx)) , 'mdates_': list(set(DF.Date)) ,'Zones_': list(set(DF.state))})


@app.route('/BC/<ULAsststr>')
def BC_(ULAsststr):
    DF=pd.read_excel( Path(__file__).parent/'static/BullCall.xlsx')
    ULAsstlist = ULAsststr.split(',')
    mdate_ , Zones_ =[] , []

    for dx in ULAsstlist:
        Zones_    += list(set(DF[DF.UAIndx == dx]['state']))
        mdate_      += list(set(DF[DF.UAIndx == dx]['Date']))

    return jsonify({'Zones' : list(set(Zones_)) , 'mdates': list(set(mdate_))})

@app.route('/BC/<ULAsststr>/<mdate_>')
def BC1_(ULAsststr , mdate_):
    DF=pd.read_excel( Path(__file__).parent/'static/BullCall.xlsx')
    ULAsstlist = ULAsststr.split(',')
    mdatelist = mdate_.split(',')
   
    Zones_ =[]

    for dx in ULAsstlist:
        for dy in mdatelist:
            Zones_    += list(set(DF[(DF.UAIndx == dx) & (DF.Date == dy)]['state']))
    
    return jsonify({'Zones' : list(set(Zones_))})

@app.route('/datatotableBC/<code>', methods=['POST', 'GET'])
def datatotableBC(code):
    ULAlist= code.split('&')[0]
    mdateslist= code.split('&')[1]
    zoneslist= code.split('&')[2]
    List = ULAlist.split(',')
    List2 = mdateslist.split(',')
    List3 = zoneslist.split(',')
    print(List)
    DF=pd.read_excel( Path(__file__).parent/'static/BullCalltrimed.xlsx')
    data = DF[(DF.UAIndx.isin(List)) & (DF.Date.isin(List2)) & (DF.state.isin(List3))]
    data = data[['UAIndx' , 'UAsellprice', '1stopt', '1ststrike' ,'1stoptbuypr', '2ndopt', '2ndstrike' ,'2ndoptsellpr' ,'DaystoMat' , 'Max YTM' , 'A Yield']]
    Output_ = data.to_dict(orient='records')
    Colus = data.columns
    return jsonify({'body': Output_ , 'columns': list(Colus)})

@app.route('/coveredcall/<ULAsststr>')
def coveredcall_(ULAsststr):
    DF=pd.read_excel( Path(__file__).parent/'static/CoveredCall.xlsx')
    ULAsstlist = ULAsststr.split(',')
    mdate_ , Options_ =[] , []

    for dx in ULAsstlist:
        Options_    += list(set(DF[DF.UAIndx == dx]['Indx']))
        mdate_      += list(set(DF[DF.UAIndx == dx]['Date']))

    return jsonify({'options' : Options_ , 'mdates': list(set(mdate_))})


@app.route('/coveredcall/<ULAsststr>/<mdate_>')
def Option1(ULAsststr , mdate_):
    DF=pd.read_excel( Path(__file__).parent/'static/CoveredCall.xlsx')
    ULAsstlist = ULAsststr.split(',')
    mdatelist = mdate_.split(',')
   
    Options_ =[]

    for dx in ULAsstlist:
        for dy in mdatelist:
            Options_    += list(set(DF[DF.UAIndx == dx][DF.Date == dy]['Indx']))
    return jsonify({'options' : Options_})


@app.route('/coveredcall_process_form1/<code>', methods=['POST', 'GET'])
def process_form1(code):
    # Get the input values from the first form
    vallimit = float(code.split('&')[0].replace(',',''))
    ratio = float(code.split('&')[1].replace(',',''))/100
    ARR = float(code.split('&')[2].replace(',',''))
    DF = CoveredCAll(vallimit, ratio, ARR)

    return jsonify({'ULA_': list(set(DF.UAIndx)) , 'optns': list(set(DF.Indx)) ,'Mat_': list(set(DF.Date))})

@app.route('/datatotable/<code>', methods=['POST', 'GET'])
def datatotable(code):
    List = code.split(',')
    print(List)
    DF=pd.read_excel( Path(__file__).parent/'static/CoveredCall.xlsx')
    data , datatbl = filter_(DF, List)
    return jsonify({'body': data.to_dict(orient='records') , 'help': datatbl.to_dict(orient='records')})

@app.route('/update_core', methods=['POST', 'GET'])
def update_core():
    GetUpdateoptn()
    return jsonify(result ='Just Updated!')


@app.route('/update_bullcall', methods=['POST', 'GET'])
def update_bullcall():
    BullCall()
    return jsonify(result ='Just Updated!')

if(__name__ == '__main__'):
    app.secret_key = "ThisIsNotASecret:p"
    db.create_all()
    app.run()
