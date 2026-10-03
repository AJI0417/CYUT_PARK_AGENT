from datetime import datetime

from flask import Blueprint, abort, redirect, render_template, request, url_for

import config
from db.announcement_db import (
    create_announcement,
    delete_announcement_by_id,
    get_all_announcements,
)


announcement_bp = Blueprint("announcement", __name__)


def get_current_time():
    now = datetime.now(config.TAIPEI_TIMEZONE)
    return now.strftime("%Y-%m-%d %H:%M:%S")


@announcement_bp.get("/announcements")
def announcement_list():
    return render_template(
        "announcements.html",
        announcements=get_all_announcements(),
    )


@announcement_bp.route("/admin/announcements", methods=["GET", "POST"])
def announcement_admin():
    form_title = ""
    form_content = ""
    error_message = None

    if request.method == "POST":
        form_title = request.form.get("title", "").strip()
        form_content = request.form.get("content", "").strip()

        if not form_title or not form_content:
            error_message = "公告標題和公告內容都必須填寫。"
        else:
            create_announcement(
                get_current_time(),
                config.ANNOUNCEMENT_PUBLISHER,
                form_title,
                form_content,
            )

            return redirect(
                url_for("announcement.announcement_admin", result="created")
            )

    success_message = None
    if request.args.get("result") == "created":
        success_message = "公告已成功發布。"
    elif request.args.get("result") == "deleted":
        success_message = "公告已成功刪除。"

    status_code = 400 if error_message else 200
    now = datetime.now(config.TAIPEI_TIMEZONE)

    return render_template(
        "announcement_admin.html",
        announcements=get_all_announcements(),
        current_date=now.strftime("%Y-%m-%d"),
        current_clock=now.strftime("%H:%M"),
        publisher=config.ANNOUNCEMENT_PUBLISHER,
        form_title=form_title,
        form_content=form_content,
        error_message=error_message,
        success_message=success_message,
    ), status_code


@announcement_bp.post("/admin/announcements/<int:announcement_id>/delete")
def delete_announcement(announcement_id):
    deleted = delete_announcement_by_id(announcement_id)

    if not deleted:
        abort(404, description="找不到指定的公告。")

    return redirect(
        url_for("announcement.announcement_admin", result="deleted")
    )
