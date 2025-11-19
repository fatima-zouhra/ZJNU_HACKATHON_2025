from extensions import db
from datetime import datetime
import json

class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    building = db.Column(db.String(100))
    floor = db.Column(db.String(50))
    room_number = db.Column(db.String(50))
    description = db.Column(db.Text)
    image_urls = db.Column(db.JSON)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    amap_link = db.Column(db.String(500))
    baidu_map_link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Location {self.name}>'

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Teacher {self.name}>'

class SportClass(db.Model):
    __tablename__ = 'sport_classes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    teacher = db.relationship('Teacher', backref='sport_classes')
    location = db.relationship('Location', backref='sport_classes')
    
    def __repr__(self):
        return f'<SportClass {self.name}>'

class ClassSchedule(db.Model):
    __tablename__ = 'class_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('sport_classes.id'), nullable=False)
    semester = db.Column(db.String(50), nullable=False)
    day_of_week = db.Column(db.String(20))
    start_time = db.Column(db.String(50))
    end_time = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    sport_class = db.relationship('SportClass', backref='schedules')
    
    def __repr__(self):
        return f'<ClassSchedule {self.semester} {self.day_of_week}>'


stion}>'
