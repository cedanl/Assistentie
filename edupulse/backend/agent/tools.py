from sqlalchemy import or_

from backend.models import StudentDB, StudentSchema
from backend.ml.predict import RisicoPredictor, DREMPEL

TOOL_DEFINITIONS = [
    {
        "name": "get_student_data",
        "description": "Haal het volledige profiel op van een student op basis van studentnummer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "studentnummer": {
                    "type": "string",
                    "description": "Het studentnummer (bijv. '20240001')",
                }
            },
            "required": ["studentnummer"],
        },
    },
    {
        "name": "predict_dropout_risk",
        "description": "Bereken het uitvalrisico voor een student en geef de top-3 beïnvloedende factoren.",
        "input_schema": {
            "type": "object",
            "properties": {"studentnummer": {"type": "string"}},
            "required": ["studentnummer"],
        },
    },
    {
        "name": "get_cohort_comparison",
        "description": "Vergelijk de student met het gemiddelde van zijn/haar cohort en opleiding.",
        "input_schema": {
            "type": "object",
            "properties": {"studentnummer": {"type": "string"}},
            "required": ["studentnummer"],
        },
    },
    {
        "name": "get_mentor_info",
        "description": "Geef naam en e-mail van de mentor van een student.",
        "input_schema": {
            "type": "object",
            "properties": {"studentnummer": {"type": "string"}},
            "required": ["studentnummer"],
        },
    },
    {
        "name": "search_students",
        "description": "Zoek studenten op naam of gedeeltelijk studentnummer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Naam of (deel van) studentnummer"}
            },
            "required": ["query"],
        },
    },
]


class ToolRegistry:
    def __init__(self, db, predictor: RisicoPredictor):
        self.db = db
        self.predictor = predictor

    def _get_student_or_error(self, studentnummer: str) -> tuple[StudentDB | None, dict | None]:
        student = self.db.query(StudentDB).filter_by(studentnummer=studentnummer).first()
        if not student:
            return None, {"error": f"Student {studentnummer!r} niet gevonden."}
        return student, None

    def get_student_data(self, studentnummer: str) -> dict:
        student, err = self._get_student_or_error(studentnummer)
        if err:
            return err
        return StudentSchema.model_validate(student).model_dump(mode="json")

    def predict_dropout_risk(self, studentnummer: str) -> dict:
        student, err = self._get_student_or_error(studentnummer)
        if err:
            return err
        data = StudentSchema.model_validate(student).model_dump()
        result = self.predictor.predict(data)
        return {
            "studentnummer": studentnummer,
            "naam": student.naam,
            "uitval_kans": result["kans"],
            "succes_kans": round(1 - result["kans"], 4),
            "status": "dreiging" if result["kans"] >= DREMPEL else "op_koers",
            "shap_top3": result["shap_top3"],
        }

    def get_cohort_comparison(self, studentnummer: str) -> dict:
        student, err = self._get_student_or_error(studentnummer)
        if err:
            return err
        cohortgenoten = (
            self.db.query(StudentDB)
            .filter(
                StudentDB.opleiding == student.opleiding,
                StudentDB.cohort == student.cohort,
                StudentDB.studentnummer != student.studentnummer,
            )
            .all()
        )
        if not cohortgenoten:
            return {"error": "Geen cohortgenoten gevonden."}
        gem_aanw = round(sum(s.aanwezigheid for s in cohortgenoten) / len(cohortgenoten), 3)
        gem_voortgang = round(sum(s.voortgang for s in cohortgenoten) / len(cohortgenoten), 3)
        gem_bsa = round(sum(s.bsa_studiepunten for s in cohortgenoten) / len(cohortgenoten), 1)
        return {
            "opleiding": student.opleiding,
            "cohort": student.cohort,
            "aantal_cohortgenoten": len(cohortgenoten),
            "student": {
                "aanwezigheid": student.aanwezigheid,
                "voortgang": student.voortgang,
                "bsa_studiepunten": student.bsa_studiepunten,
            },
            "cohortgemiddelde": {
                "aanwezigheid": gem_aanw,
                "voortgang": gem_voortgang,
                "bsa_studiepunten": gem_bsa,
            },
        }

    def get_mentor_info(self, studentnummer: str) -> dict:
        student, err = self._get_student_or_error(studentnummer)
        if err:
            return err
        return {
            "mentor_naam": student.mentor_naam,
            "mentor_email": student.mentor_email,
            "student_naam": student.naam,
            "student_email": student.email,
        }

    def search_students(self, query: str) -> list[dict]:
        treffer = (
            self.db.query(StudentDB)
            .filter(
                or_(
                    StudentDB.naam.ilike(f"%{query}%"),
                    StudentDB.studentnummer.ilike(f"%{query}%"),
                )
            )
            .limit(10)
            .all()
        )
        return [
            {
                "studentnummer": s.studentnummer,
                "naam": s.naam,
                "opleiding": s.opleiding,
                "cohort": s.cohort,
            }
            for s in treffer
        ]

    def get_handlers(self) -> dict:
        return {
            "get_student_data": self.get_student_data,
            "predict_dropout_risk": self.predict_dropout_risk,
            "get_cohort_comparison": self.get_cohort_comparison,
            "get_mentor_info": self.get_mentor_info,
            "search_students": self.search_students,
        }
