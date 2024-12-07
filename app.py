import logging
from flask import Flask, request, jsonify, render_template
import voicemeeter
import time

app = Flask(__name__)

kind = 'banana'
voicemeeter.launch(kind)

logging.basicConfig(level=logging.DEBUG)

current_gain = 0
current_aux_gain = 0
current_input3_gain = 0
last_updated = 0
pending_gain = None
pending_aux_gain = None
pending_input3_gain = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_gain', methods=['POST'])
def set_gain():
    global current_gain, current_aux_gain, current_input3_gain
    global last_updated, pending_gain, pending_aux_gain, pending_input3_gain
    try:
        data = request.json
        gain_value = float(data.get('gain', 0))
        aux_gain_value = float(data.get('auxGain', 0))
        input3_gain_value = float(data.get('input3Gain', 0))

        pending_gain = gain_value
        pending_aux_gain = aux_gain_value
        pending_input3_gain = input3_gain_value
        logging.info(f"Received: Gain={gain_value}, AuxGain={aux_gain_value}, Input3Gain={input3_gain_value}")

        current_time = time.time()
        if current_time - last_updated >= 0.1:
            if pending_gain is not None:
                current_gain = pending_gain
                pending_gain = None
            if pending_aux_gain is not None:
                current_aux_gain = pending_aux_gain
                pending_aux_gain = None
            if pending_input3_gain is not None:
                current_input3_gain = pending_input3_gain
                pending_input3_gain = None

            last_updated = current_time
            with voicemeeter.remote(kind) as vmr:
                vmr.outputs[0].gain = current_gain
                vmr.inputs[4].gain = current_aux_gain
                vmr.inputs[3].gain = current_input3_gain  
            logging.info(f"Applied: Gain={current_gain}, AuxGain={current_aux_gain}, Input3Gain={current_input3_gain}")
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "wait", "message": "Please wait before adjusting again."})
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(debug=False, host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(f"Error running Flask app: {e}")
