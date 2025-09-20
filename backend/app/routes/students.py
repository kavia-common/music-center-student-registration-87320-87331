from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields, validate

from ..models import db, Student

blp = Blueprint(
    "Students",
    "students",
    url_prefix="/api/students",
    description="Endpoints for student registration and listing.",
)


class StudentCreateSchema(Schema):
    full_name = fields.String(required=True, validate=validate.Length(min=1), metadata={"description": "Student full name"})
    email = fields.Email(required=True, metadata={"description": "Contact email (must be unique)."})
    phone = fields.String(required=False, allow_none=True, metadata={"description": "Phone number"})
    instrument = fields.String(required=False, allow_none=True, metadata={"description": "Instrument of interest"})
    experience_level = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf(["Beginner", "Intermediate", "Advanced"], error="experience_level must be one of: Beginner, Intermediate, Advanced"),
        metadata={"description": "Experience level"},
    )


class StudentResponseSchema(Schema):
    id = fields.Integer(required=True)
    full_name = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(allow_none=True)
    instrument = fields.String(allow_none=True)
    experience_level = fields.String(allow_none=True)


@blp.route("/")
class StudentsCollection(MethodView):
    # PUBLIC_INTERFACE
    def get(self):
        """List all registered students."""
        students = Student.query.order_by(Student.id.desc()).all()
        return {"items": [s.to_dict() for s in students]}

    # PUBLIC_INTERFACE
    @blp.arguments(StudentCreateSchema)
    @blp.response(201, StudentResponseSchema)
    def post(self, new_student):
        """
        Create a new student registration.

        Request JSON:
          - full_name (str, required)
          - email (str, required, unique)
          - phone (str, optional)
          - instrument (str, optional)
          - experience_level (str, optional; OneOf: Beginner, Intermediate, Advanced)
        """
        # Enforce uniqueness on email
        existing = Student.query.filter_by(email=new_student["email"]).first()
        if existing:
            abort(409, message="A student with this email already exists.")

        student = Student(
            full_name=new_student["full_name"],
            email=new_student["email"],
            phone=new_student.get("phone"),
            instrument=new_student.get("instrument"),
            experience_level=new_student.get("experience_level"),
        )
        db.session.add(student)
        db.session.commit()
        return student.to_dict()
