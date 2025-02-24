from flask import Flask, render_template, jsonify,redirect, url_for, request
import json 
from distraction import detect_mobile_phone
from helmet import detect_plates
from traffic_signal import detect_signal_violation
from flask import Flask, render_template, request, Response
import utils
import os
import time

app = Flask(__name__)

ROOT_DIR = "./"

with open("details.json", "r") as jf:
    data = json.load(jf)

@app.route('/')
@app.route('/helmet_compliance', methods=['POST', 'GET'])
def helmet_video():
    if request.method == 'POST':
        uploaded_file = request.files['video_file']

        if uploaded_file:
            # Get the selected file name
            file_name = uploaded_file.filename
            file_path = os.path.join(ROOT_DIR, file_name)

            uploaded_file.save(file_path)
            print("Uploaded File Name:", file_name)
            # Get the selected location from the form
            selected_location = request.form.get('location')
            print("Selected Location:", selected_location)

            ret = detect_plates(file_path)
            if ret:
                result_set = utils.perform_ocr()
                if result_set:
                    utils.make_doc(result_set)
                    
            print(ret)
            return jsonify(ret)
            
    locations = ['Miyapur', 'Kukatpally', 'L B Nagar', 'Ameerpet', 'Chanda Nagar']
    return render_template('Helmet.html', location=locations)


@app.route('/signal', methods=['POST', 'GET'])
def signal_video():
    if request.method == 'POST':
        uploaded_file = request.files['video_file']

        if uploaded_file:
            # Get the selected file name
            file_name = uploaded_file.filename
            file_path = os.path.join(ROOT_DIR, file_name)
            uploaded_file.save(file_path)

            print("Uploaded File Name:", file_name)

            # Get the selected location from the form
            selected_location = request.form.get('locations')
            print("Selected Location:", selected_location)

            ret = detect_signal_violation(file_path, data)
            print(ret)
            return jsonify(ret)

    locations = ['Miyapur', 'Kukatpally', 'L B Nagar', 'Ameerpet', 'Chanda Nagar']
    return render_template('Signal.html', location = locations)


# @app.route('/alert', methods=['POST', 'GET'])
# def alert():    
#     return render_template('Alert.html')


# @app.route('/email' , methods=['POST','GET'])
# def email():
#    return render_template('Analytics.html')


if __name__ == '__main__':
    app.run(debug=True)