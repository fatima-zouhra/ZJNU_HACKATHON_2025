from flask import Blueprint, request, jsonify
from models import ClassInfo, Location, Teacher
from extensions import db

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/add_class", methods=["POST"])
def add_class():
    data = request.get_json()

    teacher = Teacher(name=data["teacher_name"], contact=data["teacher_contact"])
    location = Location(
        building=data["building"],
        floor=data["floor"],
        map_url=data["map_url"],
        photo_url=data["photo_url"]
    )

    db.session.add_all([teacher, location])
    db.session.commit()

    new_class = ClassInfo(
        sport=data["sport"],
        time=data["time"],
        teacher_id=teacher.id,
        location_id=location.id
    )

    db.session.add(new_class)
    db.session.commit()

    return jsonify({"message": "Class added successfully"})
