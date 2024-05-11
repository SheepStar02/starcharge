from flask import Flask, jsonify, render_template, request, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://steedelivery:GuessThis1!@dd-api-db.cmrbrfkecsbo.us-east-1.rds.amazonaws.com:5432/cases'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dtc = db.Column(db.String(255))
    stop_reason = db.Column(db.String(255))
    date = db.Column(db.String(255))
    status = db.Column(db.String(255), default="Not Reviewed")
    description = db.Column(db.String(255))
    full_description = db.Column(db.String(255))
    unit_details = db.Column(db.String(255))
    firmware_version = db.Column(db.String(255))
    client_name = db.Column(db.String(255))
    severity = db.Column(db.String(255))
    applicability = db.Column(db.String(255))
    
    def to_json(self):
        return {
            'id': self.id,
            'dtc': self.dtc,
            'stop_reason': self.stop_reason,
            'date': self.date,
            'status': self.status,
            'description': self.description,
            'full_description': self.full_description,
            'unit_details': self.unit_details,
            'firmware_version': self.firmware_version,
            'client_name': self.client_name,
            'severity': self.severity,
            'applicability': self.applicability
        }

@app.route('/')
def home():
    cases = Case.query.filter(Case.status != "Close - Resolved").all()
    converted = [case.to_json() for case in cases]
    print(converted)
    cases_json = json.dumps([case.to_json() for case in cases])
    print(cases_json)
    return render_template('index.html', cases=cases, cases_json=jsonify(cases_json).get_json())

@app.route('/newCase')
def new_case():
    with open('OUTPUT_DTC.json', 'r') as file:
        data = json.load(file)
        codes = [item['code'] for item in data]
        return render_template('newCase.html', codes=codes)

@app.route('/changeOCPP')
def change_ocpp():
    return render_template('changeOCPP.html')

@app.route('/explanation')
def explanation():
    return render_template('explanation.html')

@app.route('/lookupError')
def lookup_error():
    return render_template('lookupError.html')

@app.route('/update_status/<int:case_id>', methods=['PUT'])
def update_case_status(case_id):
    # Parse request data
    data = request.json
    new_status = data.get('status')

    # Fetch the case from the database
    case = Case.query.get(case_id)
    if not case:
        return jsonify({'message': 'Case not found'}), 404

    # Update the status
    case.status = new_status
    db.session.commit()

    return jsonify({'message': 'Status updated successfully'}), 200


@app.route('/addCase', methods=['POST'])
def add_case():
    body = request.json
    try:
        new_case = Case(
            dtc=body['dtc'],
            stop_reason=body['stopReason'],
            date=body['date'],
            description=body['description'],
            full_description=body['fullDescription'],
            unit_details=body['unitDetails'],
            firmware_version=body['firmwareVersion'],
            client_name=body['clientName'],
            severity=body['severity'],
            applicability=body['applicability']
        )
        db.session.add(new_case)
        db.session.commit()
        return jsonify({'message': 'Case added successfully'})
    except Exception as e:
        print(f"Error executing database query: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/getCases', methods=['POST'])
def get_cases():
    body = request.json
    print(body)
    def get_string():
        conditions = [f"{key}='{value}'" for key, value in body.items() if value and key in Case.__table__.columns]
        print(conditions)
        if conditions:
            return text(' AND '.join(conditions))
        else:
            return text('1=1')
    try:
        cases = Case.query.filter(get_string()).all()

        cases_dict = [case.__dict__ for case in cases]
        for case in cases_dict:
            case.pop('_sa_instance_state', None) 

        return json.jsonify(cases_dict)
    except Exception as e:
        print(f"Error executing database query: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/deleteEntry', methods=['DELETE'])
def delete_entry():
    id = request.args.get('id')

    try:
        case_to_delete = Case.query.get(id)
        db.session.delete(case_to_delete)
        db.session.commit()
        return jsonify({'message': 'Case deleted successfully'})
    except Exception as e:
        print(f"Error deleting case: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/output_dtc')
def output_utc():
    with open('OUTPUT_DTC.json', 'r') as file:
        json_data = json.load(file)
    return jsonify(json_data)

@app.route('/output_stopreason')
def output_stopreason():
    with open('OUTPUT_STOPREASON.json', 'r') as file:
        json_data = json.load(file)
    return jsonify(json_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
