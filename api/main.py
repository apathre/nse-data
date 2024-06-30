import random, string, json

from flask import Flask, jsonify 
from jugaad_data.nse import NSELive, stock_csv, stock_df
from datetime import date, datetime

app = Flask(__name__) 


@app.route('/') 
def home():
  return  jsonify("message:Hello World")

@app.route('/live/<scripId>')
def live(scripId):
  n = NSELive()
  
  f= open('scripList.json')
  chkdt=json.load(f)
  for item in chkdt:
    if(item['SYMBOL']==scripId):
        #print("item found:",item['SYMBOL'])
        q = n.stock_quote(scripId)
        #print(q['priceInfo'])
        perChange = round(q['priceInfo']['pChange'],2)
        res_data = {
          "Last Price":q['priceInfo']['lastPrice'],
          "Open":q['priceInfo']['open'],
          "High":q['priceInfo']['intraDayHighLow']['max'],
          "Low":q['priceInfo']['intraDayHighLow']['min'],
          "Percentage Change":perChange,
          "Change":round(q['priceInfo']['change'],2),
          "Previous Day Close":q['priceInfo']['previousClose']
        }
        break
    else:
       res_data = "ScripId not found"
      
  
  
  return jsonify(res_data)
  

@app.route('/history/<scripId>/<fromDate>/<toDate>')
def history(scripId,fromDate,toDate):
  # Download as pandas dataframe
  
  date_format = '%Y%m%d'
  dt_frm = datetime.strptime(fromDate, date_format)
  dt_to = datetime.strptime(toDate, date_format)
    
  from_date=date(dt_frm.year,dt_frm.month,dt_frm.day)
  to_date = date(dt_to.year,dt_to.month,dt_to.day)
  
  f= open('scripList.json')
  chkdt=json.load(f)
  for item in chkdt:
    if(item['SYMBOL']==scripId):
        df = stock_df(symbol=scripId,
                  from_date=from_date,
                  to_date=to_date,
                  series="EQ")
  
        # storing the data in JSON format
        df.to_json('file.json', orient = 'split', compression = 'infer', index = 'true')

        df_column = df.columns.values.tolist()
        df_list = df.values.tolist()
    
        data = jsonify({'columns': df_column, 'values': df_list})
        break
    else:
       data = "Scrip not found"
  
  return (data) 
    
#jsonify(data[data])

#Add to Database. Execute this route only when our historical database is empty. Else check for last data available

#print("df head is:",df.head())

# Download data and save to a csv file
#stock_csv(symbol="SBIN", from_date=date(2023,10,1),
#            to_date=date(2023,10,30), series="EQ", output="./file.csv")




if __name__ == "__main__":
  app.run()
    