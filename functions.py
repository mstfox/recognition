from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy


def startup():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    db = SQLAlchemy(app)
    app.app_context().push()
    app.debug = True
    return (db ,app)


def filter_(DF, sel_options):
    data = DF[DF.Indx.isin(sel_options)]
    data = data[['Indx','StrikePrice', 'OptionSellPrice', 'OptnSellVol', 'UAIndx', 'UABuyPrice','DaystoMatu', 'RtoMatu' , 'ARR']]
    data.columns = ['اختیار','قیمت اعمال', 'قیمت فروش اختیار', 'حجم فروش', 'نماد پایه', 'قیمت لحظه','سررسید', 'YTM' , 'Ayield']
    #Place Here
    datatbl = data[['اختیار', 'سررسید','Ayield']]
    datatbl.columns = ['01 index', '02 Days to Maturity','AYield']

    return data , datatbl