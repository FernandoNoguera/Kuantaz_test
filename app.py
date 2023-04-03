import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask import jsonify, request
from datetime import datetime
import urllib.parse
from flask import jsonify

# Environment
load_dotenv()
app = Flask(__name__)


# DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()


# Models
# Define Institution model
class Institution(db.Model):
    __tablename__ = 'institutions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    address = db.Column(db.String(255))
    creation_date = db.Column(db.Date, nullable=False)
    projects = db.relationship('Project', backref='institution', lazy=True)

    def __repr__(self):
        return f'<Institution {self.name}>'


# Define Project model
class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Project {self.name}>'
    

# Define User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    rut = db.Column(db.String(12), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    position = db.Column(db.String(255))
    age = db.Column(db.Integer)
    projects = db.relationship('Project', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name} {self.last_name}>'

def create_default_data():
    institution = Institution(
        name='Sample Institution', 
        description='A sample institution',
        address='123 Main St', 
        creation_date=datetime.now()
    )
    user = User(
        name='John', 
        last_name='Doe', 
        rut='12345678-9', 
        birth_date=datetime.now(), 
        position='Manager', 
        age=35
    )
    project = Project(
        name='Sample Project', 
        description='A sample project', 
        start_date=datetime.now(), 
        end_date=datetime.now(), 
        institution=institution, 
        user=user
    )

    db.session.add(institution)
    db.session.add(user)
    db.session.add(project)

    db.session.commit()

#routes
# API routes for Institution
@app.route('/institutions', methods=['GET'])
def get_institutions():
    institutions = Institution.query.all()
    return jsonify([{
        'id': i.id,
        'name': i.name,
        'description': i.description,
        'address': i.address,
        'location': f'https://www.google.com/maps/search/{urllib.parse.quote(i.address)}',
        'abbreviation': i.name[:3],
        'creation_date': i.creation_date.strftime('%Y-%m-%d')
    } for i in institutions]), 200

@app.route('/institutions', methods=['POST'])
def create_institution():
    data = request.get_json()
    institution = Institution(name=data['name'], description=data['description'], address=data['address'], creation_date=datetime.strptime(data['creation_date'], '%Y-%m-%d').date())
    institution.location = f'https://www.google.com/maps/search/{urllib.parse.quote(institution.address)}'
    institution.abbreviation = institution.name[:3]
    db.session.add(institution)
    db.session.commit()
    return jsonify({
        'name': institution.name,
        'description': institution.description,
        'address': institution.address,
        'location': institution.location,
        'abbreviation': institution.abbreviation,
        'creation_date': institution.creation_date.isoformat()
    }), 201

# routes for Institution with Projects and Users
@app.route('/institutions/<int:id>', methods=['GET'])
def get_institution_with_projects(id):
    institution = Institution.query.get(id)
    if institution is None:
        return jsonify({'error': 'Institution not found'}), 404
    projects = []
    for project in institution.projects:
        user = User.query.get(project.user_id)
        projects.append({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'start_date': project.start_date.strftime('%Y-%m-%d'),
            'end_date': project.end_date.strftime('%Y-%m-%d'),
            'responsible': {
                'id': user.id,
                'name': user.name,
                'last_name': user.last_name,
                'position': user.position
            }
        })
    return jsonify({
        'id': institution.id,
        'name': institution.name,
        'description': institution.description,
        'address': institution.address,
        'creation_date': institution.creation_date.strftime('%Y-%m-%d'),
        'projects': projects
    }), 200


@app.route('/institutions/<int:id>', methods=['PUT'])
def update_institution(id):
    institution = Institution.query.get(id)
    if institution is None:
        return jsonify({'error': 'Institution not found'}), 404
    data = request.get_json()
    institution.name = data['name']
    institution.description = data['description']
    institution.address = data['address']
    institution.creation_date = datetime.strptime(data['creation_date'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify({
        'name': institution.name,
        'description': institution.description,
        'address': institution.address,
        'creation_date': institution.creation_date.isoformat()
    }),200

@app.route('/institutions/<int:id>', methods=['DELETE'])
def delete_institution(id):
    institution = Institution.query.get(id)
    if institution is None:
        return jsonify({'error': 'Institution not found'}), 404
    db.session.delete(institution)
    db.session.commit()
    return '', 204

# API routes for Project
@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    result = []
    for project in projects:
        days_left = (project.end_date - datetime.now().date()).days
        result.append({
            'id': project.id,
            'name': project.name,
            'days_left': days_left,
            'description': project.description,
            'start_date': project.start_date.strftime('%Y-%m-%d'),
            'end_date': project.end_date.strftime('%Y-%m-%d'),
            'institution_id': project.institution_id,
            'user_id': project.user_id
            
        })
    return jsonify(result)

@app.route('/projects/<int:id>', methods=['GET'])
def get_project(id):
    project = Project.query.get(id)
    days_left = (project.end_date - datetime.now().date()).days
    if project is None:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'start_date': project.start_date.strftime('%Y-%m-%d'),
        'end_date': project.end_date.strftime('%Y-%m-%d'),
        'days_left': days_left,
        'institution_id': project.institution_id,
        'user_id': project.user_id
    }), 200

# API routes for User
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'name': u.name,
        'last_name': u.last_name,
        'rut': u.rut,
        'birth_date': u.birth_date.strftime('%Y-%m-%d'),
        'position': u.position,
        'age': u.age
    } for u in users]), 200

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'name': user.name,
        'last_name': user.last_name,
        'rut': user.rut,
        'birth_date': user.birth_date.strftime('%Y-%m-%d'),
        'position': user.position,
        'age': user.age
    }), 200

@app.route('/users/rut/<string:rut>', methods=['GET'])
def get_user_with_projects(rut):
    user = User.query.filter_by(rut=rut).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    projects = []
    for project in user.projects:
        projects.append({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'start_date': project.start_date.strftime('%Y-%m-%d'),
            'end_date': project.end_date.strftime('%Y-%m-%d'),
            'institution': {
                'id': project.institution.id,
                'name': project.institution.name,
                'description': project.institution.description,
                'address': project.institution.address,
                'creation_date': project.institution.creation_date.strftime('%Y-%m-%d')
            }
        })

    return jsonify({
        'rut': user.rut,
        'name': user.name,
        'last_name': user.last_name,
        'position': user.position,
        'projects': projects
    }), 200





if __name__ == '__main__':
    # Initialize DB
    db.init_app(app)

    # Create tables
    with app.app_context():
        db.create_all()
        create_default_data()

    app.run(debug=True, host='0.0.0.0', port=5001)