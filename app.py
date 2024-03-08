from flask import Flask, jsonify, render_template, request, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://steedelivery:GuessThis1!@dd-api-db.cmrbrfkecsbo.us-east-1.rds.amazonaws.com:5432/cases'
db = SQLAlchemy(app)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dtc = db.Column(db.String(255))
    stop_reason = db.Column(db.String(255))
    date = db.Column(db.String(255))
    description = db.Column(db.String(255))
    full_description = db.Column(db.String(255))
    unit_details = db.Column(db.String(255))
    firmware_version = db.Column(db.String(255))
    client_name = db.Column(db.String(255))
    severity = db.Column(db.String(255))
    applicability = db.Column(db.String(255))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/newCase')
def new_case():
    return render_template('newCase.html')

@app.route('/changeOCPP')
def change_ocpp():
    return render_template('changeOCPP.html')

@app.route('/explanation')
def explanation():
    return render_template('explanation.html')

@app.route('/lookupError')
def lookup_error():
    return render_template('lookupError.html')

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
