from flask import Blueprint, jsonify, g
from app.models import Report, User
from app.services.analysis_service import AnalysisService
from app.api.dependencies import login_required
from app.core.database import db
import asyncio

analysis_bp = Blueprint('analysis', __name__)
analysis_service = AnalysisService()

@analysis_bp.route("/<int:report_id>/analyze", methods=["POST"])
@login_required
def analyze_report(report_id: int):
    """Analyze a specific report"""
    report = db.session.query(Report).filter(
        Report.id == report_id,
        Report.user_id == g.current_user.id
    ).first()

    if not report:
        return jsonify({"detail": "Report not found"}), 404

    if report.status != "completed":
        return jsonify({"detail": "Report must be completed before analysis"}), 400

    try:
        parsed_data = report.parsed_data
        if not parsed_data:
            return jsonify({"detail": "No parsed data available for analysis"}), 400

        patient_info = {
            "age": report.patient_age,
            "sex": report.patient_sex,
            "medications": [],
            "conditions": []
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis_result = loop.run_until_complete(analysis_service.analyze_report(parsed_data, patient_info))
        loop.close()

        report.analysis_result = analysis_result.dict()
        db.session.commit()

        return jsonify({
            "report_id": report_id,
            "analysis": analysis_result.dict(),
            "status": "completed"
        })

    except Exception as e:
        return jsonify({"detail": f"Analysis failed: {str(e)}"}), 500

@analysis_bp.route("/<int:report_id>/insights", methods=["GET"])
@login_required
def get_report_insights(report_id: int):
    """Get insights for a specific report"""
    report = db.session.query(Report).filter(
        Report.id == report_id,
        Report.user_id == g.current_user.id
    ).first()

    if not report:
        return jsonify({"detail": "Report not found"}), 404

    if not report.analysis_result:
        return jsonify({"detail": "Report analysis not available. Please run analysis first."}), 400

    analysis = report.analysis_result
    insights = {
        "flagged_tests_count": len(analysis.get("flagged_tests", [])),
        "summary": analysis.get("summary", ""),
        "recommendations": analysis.get("recommendations", []),
        "disclaimer": analysis.get("disclaimer", ""),
        "confidence": analysis.get("confidence_overall", 0.0),
        "flagged_tests": analysis.get("flagged_tests", [])
    }
    return jsonify(insights)