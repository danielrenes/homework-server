from datetime import datetime, timedelta

from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer
from werkzeug.security import generate_password_hash, check_password_hash

from . import db

students_homeworks_table = db.Table('students_homeworks',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id'), primary_key=True),
    db.Column('homework_id', db.Integer, db.ForeignKey('homeworks.id'), primary_key=True)
)

students_courses_table = db.Table('students_courses',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    token = db.Column(db.String(64), unique=True)
    token_expiration = db.Column(db.DateTime)

    __mapper_args__ = {
        'polymorphic_identity': 'users',
        'polymorphic_on': type
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        serializer = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        self.token = serializer.dumps({'username': self.username}).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
        db.session.add(self)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name
        }

    def from_dict(self, data):
        for field in ['name', 'username']:
            if field in data:
                setattr(self, field, data[field])
        if 'password' in data:
            self.set_password(data['password'])

class Administrator(User):
    __tablename__ = 'administrators'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'administrators',
    }

class Teacher(User):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'teachers',
    }

    courses = db.relationship('Course', backref='teacher', lazy=True)

class Student(User):
    __tablename__ = 'students'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    homeworks = db.relationship('Homework',
                                secondary=students_homeworks_table,
                                backref='students_homeworks'
                               )

    courses = db.relationship('Course',
                              secondary=students_courses_table,
                              backref='students_courses'
                             )

    __mapper_args__ = {
        'polymorphic_identity': 'students',
    }

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256), nullable=False)

    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    homeworks = db.relationship('Homework', backref='course', lazy=True, cascade='all, delete-orphan')
    students = db.relationship('Student',
                               secondary=students_courses_table,
                               backref='students_courses'
                              )

    def to_dict(self):
        teacher = Teacher.query.filter_by(id=self.teacher_id).first()
        teacher_name = teacher.name if teacher is not None else None

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'teacher': teacher_name
        }

    def from_dict(self, data):
        for field in ['name', 'description']:
            if field in data:
                setattr(self, field, data[field])

class Homework(db.Model):
    __tablename__ = 'homeworks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    headcount = db.Column(db.Integer, nullable=False)
    self_assignable = db.Column(db.Boolean, nullable=False, default=False)

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    solutions = db.relationship('Solution', backref='student', lazy=True, cascade='all, delete-orphan')
    students = db.relationship('Student',
                               secondary=students_homeworks_table,
                               backref='students_homeworks'
                              )

    def to_dict(self):
        course = Course.query.filter_by(id=self.course_id).first()
        course_name = course.name if course is not None else None

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'headcount': self.headcount,
            'self_assignable': self.self_assignable,
            'course': course_name
        }

    def from_dict(self, data):
        for field in ['name', 'description']:
            if field in data:
                setattr(self, field, data[field])
        if 'deadline' in data:
            if isinstance(data['deadline'], datetime):
                self.deadline = data['deadline']
            else:
                try:
                    self.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    pass
        if 'headcount' in data:
            try:
                self.headcount = int(data['headcount'])
            except ValueError:
                pass
        if 'self_assignable' in data:
            if type(data['self_assignable']) == bool:
                self.self_assignable = data['self_assignable']
            elif type(data['self_assignable']) == str and data['self_assignable'].lower() in ['true', 'false']:
                self.self_assignable = (data['self_assignable'].lower() == 'true')
        if 'students' in data:
            for id in data['students']:
                student = Student.query.filter_by(id=id).first()
                self.students.append(student)

class Solution(db.Model):
    __tablename__ = 'solutions'

    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(256), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(512), default='')

    homework_id = db.Column(db.Integer, db.ForeignKey('homeworks.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status
        }

    def from_dict(self, data):
        if 'status' in data:
            self.status = data['status']