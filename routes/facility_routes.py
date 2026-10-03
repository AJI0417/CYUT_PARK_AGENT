import sqlite3

from flask import Blueprint, redirect, render_template, request, url_for

from db.facility_db import (
    ALLOWED_STATUSES,
    get_all_facilities,
    get_facility_ids,
    update_facility_statuses,
)


facility_bp = Blueprint("facility", __name__)


@facility_bp.get("/worker")
def worker():
    facilities = get_all_facilities()

    return render_template(
        "worker.html",
        facilities=facilities,
    )


@facility_bp.post("/update")
def update():
    updates = []

    for facility_id in get_facility_ids():
        field_name = f"status_{facility_id}"
        new_status = request.form.get(field_name)

        if new_status not in ALLOWED_STATUSES:
            return f"設施 {facility_id} 的狀態不正確", 400

        updates.append((new_status, facility_id))

    try:
        update_facility_statuses(updates)
    except sqlite3.Error as error:
        print("更新資料庫失敗：", error)
        return "更新資料庫失敗", 500

    return redirect(url_for("facility.success"))


@facility_bp.get("/success")
def success():
    return render_template("success.html")
