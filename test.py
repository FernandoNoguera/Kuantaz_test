import os
import unittest
from datetime import datetime
from dotenv import load_dotenv

from app import app, db, Institution, Project, User

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class ModelsTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        db.create_all()
        self.institution = Institution(
            name='Test Institution',
            description='A test institution',
            address='123 Test St',
            creation_date=datetime.now()
        )
        self.user = User(
            name='Jane',
            last_name='Doe',
            rut='12345678-9',
            birth_date=datetime.now(),
            position='Manager',
            age=30
        )
        self.project = Project(
            name='Test Project',
            description='A test project',
            start_date=datetime.now(),
            end_date=datetime.now(),
            institution=self.institution,
            user=self.user
        )
        db.session.add_all([self.institution, self.user, self.project])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_institution_model(self):
        institution = Institution.query.filter_by(name='Test Institution').first()
        self.assertIsNotNone(institution)
        self.assertEqual(institution.description, 'A test institution')
        self.assertEqual(institution.address, '123 Test St')

    def test_project_model(self):
        project = Project.query.filter_by(name='Test Project').first()
        self.assertIsNotNone(project)
        self.assertEqual(project.description, 'A test project')
        self.assertEqual(project.institution.name, 'Test Institution')
        self.assertEqual(project.user.name, 'Jane')

    def test_user_model(self):
        user = User.query.filter_by(name='Jane').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.position, 'Manager')

if __name__ == '__main__':
    unittest.main()
