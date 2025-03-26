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
    
    # Try to parse date from the first line
    date = None
    date_regex = r"(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})"  # e.g. 25/03/2025 or 25-03-2025
    if re.match(date_regex, lines[0]):
        day, month, year = map(int, re.match(date_regex, lines[0]).groups())
        date = datetime(year, month, day)
        lines = lines[1:]  # remove the date line

    time_regex = r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*(.+)"
    for line in lines:
        match = re.match(time_regex, line.strip())
        if match:
            schedule.append((match.group(1), match.group(2), match.group(3), date))

    return schedule




@app.route('/generate-ics', methods=['POST', 'OPTIONS'])
def generate_ics():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    print("📩 Flask received a request!")
    note = request.json['note']
    schedule = parse_schedule(note)
    calendar = Calendar()

    for start, end, name, event_date in schedule:
        event = Event()
        start_dt = datetime.strptime(start, "%H:%M")
        end_dt = datetime.strptime(end, "%H:%M")
        
        # Use the provided date or today
        date = event_date or datetime.now()
        begin = date.replace(hour=start_dt.hour, minute=start_dt.minute, second=0, microsecond=0)
        end_time = date.replace(hour=end_dt.hour, minute=end_dt.minute, second=0, microsecond=0)

        event.name = name
        event.begin = begin
        event.end = end_time
        calendar.events.add(event)

    # Only one .ics file with all events
    ics_io = io.StringIO(str(calendar))
    return send_file(
        io.BytesIO(ics_io.getvalue().encode()),
        mimetype="text/calendar",
        as_attachment=True,
        download_name="schedule.ics"
    )


if __name__ == '__main__':
            app.run(host='0.0.0.0', port=10000, debug=True)

