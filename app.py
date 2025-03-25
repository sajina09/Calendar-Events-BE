from flask import Flask, request, send_file
from flask_cors import CORS

from ics import Calendar, Event
from datetime import datetime, timedelta
import io
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/data', methods=['GET'])
def get_data():
            data = {'message': 'Hello from the Server!'}
            return data



def parse_schedule(note):
    schedule = []
    lines = note.strip().split('\n')
    time_regex = r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*(.+)"
    for line in lines:
        match = re.match(time_regex, line.strip())
        if match:
            schedule.append(match.groups())
    return schedule



@app.route('/generate-ics', methods=['POST', 'OPTIONS'])
def generate_ics():
    if request.method == 'OPTIONS':
        # Respond to preflight request
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        print("response : ", response)
        return response
    
    print("📩 Flask received a request!")
    note = request.json['note']
    schedule = parse_schedule(note)
    calendar = Calendar()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


    for start, end, name in schedule:
        event = Event()
        start_dt = datetime.strptime(start, "%H:%M")
        end_dt = datetime.strptime(end, "%H:%M")
        event.name = name
        event.begin = today.replace(hour=start_dt.hour, minute=start_dt.minute)
        event.end = today.replace(hour=end_dt.hour, minute=end_dt.minute)
        calendar.events.add(event)


    ics_io = io.StringIO(str(calendar))
    return send_file(
        io.BytesIO(ics_io.getvalue().encode()),
        mimetype="text/calendar",
        as_attachment=True,
        download_name="schedule.ics"
    )


if __name__ == '__main__':
            app.run(host='0.0.0.0', port=10000, debug=True)

