from flask import Flask, render_template, request
import pandas as pd
from emotions import analyze_emotions_bert
from create_excel import create_doc

app = Flask(__name__)

def extract_columns_to_dict(file_path, col1='D04 - VoC', col2='D.EXTRA - Commento cliente', col3='BaseContractCode', separator=" "):
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Extract the data from the specified columns
    extracted_data = df[[col1, col2, col3]]

    result_dict = {}

    # Create a list of strings by concatenating the values from the specified columns, skipping empty rows
    for _, row in extracted_data.iterrows():
        col3_value = f"{row[col3]}"
        if pd.notna(row[col1]) or pd.notna(row[col2]):
          combined_col1_col2 = f"{row[col1]}{separator}{row[col2]}"
        else:
          combined_col1_col2 = ''

        result_dict.update({col3_value : combined_col1_col2})

    return result_dict

# End-point to open the main page
@app.route('/')
def index():
  return render_template('main.html')

@app.route('/get_file', methods=['POST'])
def get_file():
  name = request.json.get('name')
  # Parse the data as a Pandas DataFrame type
  data = pd.read_excel(name)
  # Return HTML snippet that will render the table
  return data.to_html()

@app.route('/check_emotion', methods=['POST'])
def check_emotion():
  files = request.files.getlist('input_file')
  list_json = []
  for file in files:
    data = extract_columns_to_dict(file)
    emotions_dict = {}
    for client_id in data:
      full_text = data[client_id]
      if full_text == '':
        emotions_dict.update({client_id : {"Anger" : 0, "Sadness" : 0, "Happiness" : 0, "Disgust" : 0, "Fear" : 0}})
      else:
        emotions_dict.update({client_id : analyze_emotions_bert(full_text)})

    feeling_json = {"Anger" : 0, "Sadness" : 0, "Happiness" : 0, "Disgust" : 0, "Fear" : 0}
    total = 0
    create_doc(emotions_dict, file.filename + ' - Output.xlsx')
    for row in emotions_dict:
      for emotion in emotions_dict[row]:
        feeling_json[emotion] += emotions_dict[row][emotion]
        total += emotions_dict[row][emotion]
    
    for feeling in feeling_json:
      feeling_json[feeling] = feeling_json[feeling] / total

    list_json.append(feeling_json) 
  return list_json

if __name__ == '__main__':
  app.run(
    host='localhost',
    port=5001,
    debug=True
  )