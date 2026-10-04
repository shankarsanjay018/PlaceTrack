from flask import Flask, render_template, request, redirect, session
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "placetrack-secret-key"


# =========================================================
# GLOBAL NOTIFICATION COUNT
# =========================================================

@app.context_processor
def inject_notification_count():

    unread_notifications_count = 0

    if "user_id" in session:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM notifications
            WHERE user_id = %s
            AND is_read = FALSE
            """,
            (session["user_id"],)
        )

        result = cursor.fetchone()

        if result:
            unread_notifications_count = result[0]

        cursor.close()
        connection.close()

    return {
        "unread_notifications_count": unread_notifications_count
    }


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        college = request.form["college"]

        print(
            "REGISTER EMAIL:",
            email
        )

        hashed_password = generate_password_hash(
            password
        )

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO users
            (
                name,
                email,
                password,
                college
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
        """

        cursor.execute(
            query,
            (
                name,
                email,
                hashed_password,
                college
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/login")

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect("/dashboard")

        return "Invalid email or password"

    return render_template(
        "login.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    # =====================================================
    # CURRENT USER
    # =====================================================

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id = %s
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()


    # =====================================================
    # USER APPLICATIONS
    # =====================================================

    cursor.execute(
        """
        SELECT *
        FROM applications
        WHERE user_id = %s
        ORDER BY id DESC
        """,
        (session["user_id"],)
    )

    applications = cursor.fetchall()


    # =====================================================
    # STATISTICS
    # =====================================================

    total_applications = len(
        applications
    )


    applied = sum(
        1
        for application in applications
        if application["status"]
        and application["status"].lower()
        == "applied"
    )


    interviews = sum(
        1
        for application in applications
        if application["status"]
        and application["status"].lower()
        == "interview"
    )


    selected = sum(
        1
        for application in applications
        if application["status"]
        and application["status"].lower()
        == "selected"
    )


    # =====================================================
    # DASHBOARD NOTIFICATIONS
    #
    # Get the five most recent notifications
    # for the logged-in student.
    # =====================================================

    cursor.execute(
        """
        SELECT
            id,
            user_id,
            application_id,
            title,
            message,
            is_read,
            created_at
        FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 5
        """,
        (session["user_id"],)
    )

    dashboard_notifications = (
        cursor.fetchall()
    )


    # =====================================================
    # TOTAL UNREAD NOTIFICATIONS
    #
    # This counts ALL unread notifications, not just the
    # five displayed in the popup.
    # =====================================================

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM notifications
        WHERE user_id = %s
        AND is_read = FALSE
        """,
        (session["user_id"],)
    )

    unread_result = cursor.fetchone()

    if unread_result:
        unread_notifications_count = (
            unread_result["total"]
        )
    else:
        unread_notifications_count = 0


    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    cursor.close()
    connection.close()


    # =====================================================
    # RENDER DASHBOARD
    # =====================================================

    return render_template(
        "dashboard.html",

        user=user,

        applications=applications,

        total_applications=
            total_applications,

        applied=
            applied,

        interviews=
            interviews,

        selected=
            selected,

        dashboard_notifications=
            dashboard_notifications,

        unread_notifications_count=
            unread_notifications_count
    )


# =========================================================
# APPLICATIONS
# =========================================================

@app.route("/applications")
def applications():

    if "user_id" not in session:
        return redirect("/login")


    search = request.args.get(
        "search",
        ""
    ).strip()


    status = request.args.get(
        "status",
        ""
    ).strip()


    application_id = request.args.get(
        "application_id",
        ""
    ).strip()


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    query = """
        SELECT *
        FROM applications
        WHERE user_id = %s
    """


    params = [
        session["user_id"]
    ]


    # =====================================================
    # SEARCH
    # =====================================================

    if search:

        query += """
            AND (
                company_name LIKE %s
                OR job_role LIKE %s
            )
        """

        search_value = f"%{search}%"

        params.extend(
            [
                search_value,
                search_value
            ]
        )


    # =====================================================
    # STATUS FILTER
    # =====================================================

    if status:

        query += """
            AND status = %s
        """

        params.append(
            status
        )


    # =====================================================
    # OPEN SPECIFIC APPLICATION
    # =====================================================

    if application_id:

        query += """
            AND id = %s
        """

        params.append(
            application_id
        )


    query += """
        ORDER BY application_date DESC
    """


    cursor.execute(
        query,
        tuple(params)
    )


    applications = cursor.fetchall()


    cursor.close()
    connection.close()


    return render_template(
        "applications.html",

        applications=
            applications,

        search=
            search,

        selected_status=
            status,

        selected_application_id=
            application_id
    )


# =========================================================
# ADD APPLICATION
# =========================================================

@app.route(
    "/add-application",
    methods=["GET", "POST"]
)
def add_application():

    if "user_id" not in session:
        return redirect("/login")


    if request.method == "POST":

        company_name = request.form[
            "company_name"
        ]

        job_role = request.form[
            "job_role"
        ]

        application_date = request.form[
            "application_date"
        ]

        status = request.form[
            "status"
        ]

        package = request.form[
            "package"
        ]

        notes = request.form[
            "notes"
        ]


        connection = get_db_connection()
        cursor = connection.cursor()


        query = """
            INSERT INTO applications
            (
                user_id,
                company_name,
                job_role,
                application_date,
                status,
                source,
                package,
                notes
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """


        cursor.execute(
            query,
            (
                session["user_id"],
                company_name,
                job_role,
                application_date,
                status,
                "manual",
                package,
                notes
            )
        )


        connection.commit()

        cursor.close()
        connection.close()


        return redirect(
            "/dashboard"
        )


    return render_template(
        "add_application.html"
    )


# =========================================================
# EDIT APPLICATION
# =========================================================

@app.route(
    "/edit-application/<int:id>",
    methods=["GET", "POST"]
)
def edit_application(id):

    if "user_id" not in session:
        return redirect("/login")


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    cursor.execute(
        """
        SELECT *
        FROM applications
        WHERE id = %s
        AND user_id = %s
        """,
        (
            id,
            session["user_id"]
        )
    )


    application = cursor.fetchone()


    if not application:

        cursor.close()
        connection.close()

        return (
            "Application not found",
            404
        )


    if request.method == "POST":

        company_name = request.form[
            "company_name"
        ]

        job_role = request.form[
            "job_role"
        ]

        application_date = request.form[
            "application_date"
        ]

        package = request.form[
            "package"
        ]

        notes = request.form[
            "notes"
        ]


        # =====================================================
        # MANUAL APPLICATION
        # Student can update the status.
        # =====================================================

        if application["source"] == "manual":

            status = request.form[
                "status"
            ]

            cursor.execute(
                """
                UPDATE applications
                SET
                    company_name = %s,
                    job_role = %s,
                    application_date = %s,
                    status = %s,
                    package = %s,
                    notes = %s
                WHERE id = %s
                AND user_id = %s
                """,
                (
                    company_name,
                    job_role,
                    application_date,
                    status,
                    package,
                    notes,
                    id,
                    session["user_id"]
                )
            )


        # =====================================================
        # PLACE TRACK APPLICATION
        # Student can edit details, but NOT the status.
        # Admin controls the status.
        # =====================================================

        else:

            cursor.execute(
                """
                UPDATE applications
                SET
                    company_name = %s,
                    job_role = %s,
                    application_date = %s,
                    package = %s,
                    notes = %s
                WHERE id = %s
                AND user_id = %s
                """,
                (
                    company_name,
                    job_role,
                    application_date,
                    package,
                    notes,
                    id,
                    session["user_id"]
                )
            )


        connection.commit()


        cursor.close()
        connection.close()


        return redirect(
            "/dashboard"
        )


    cursor.close()
    connection.close()


    return render_template(
        "edit_application.html",
        application=application
    )


# =========================================================
# DELETE APPLICATION
# =========================================================

@app.route(
    "/delete-application/<int:id>",
    methods=["POST"]
)
def delete_application(id):

    if "user_id" not in session:
        return redirect("/login")


    connection = get_db_connection()
    cursor = connection.cursor()


    cursor.execute(
        """
        DELETE FROM applications
        WHERE id = %s
        AND user_id = %s
        """,
        (
            id,
            session["user_id"]
        )
    )


    connection.commit()


    cursor.close()
    connection.close()


    return redirect(
        "/dashboard"
    )


# =========================================================
# OPPORTUNITIES
# =========================================================

@app.route("/opportunities")
def opportunities():

    if "user_id" not in session:
        return redirect("/login")


    search = request.args.get(
        "search",
        ""
    ).strip()


    target_group = request.args.get(
        "target_group",
        ""
    ).strip()


    work_mode = request.args.get(
        "work_mode",
        ""
    ).strip()


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    query = """
    SELECT *
    FROM opportunities
    WHERE is_active = TRUE
"""


    params = []


    # =====================================================
    # SEARCH
    # =====================================================

    if search:

        query += """
            AND (
                company_name LIKE %s
                OR internship_title LIKE %s
                OR skills LIKE %s
                OR description LIKE %s
            )
        """


        search_value = f"%{search}%"


        params.extend(
            [
                search_value,
                search_value,
                search_value,
                search_value
            ]
        )


    # =====================================================
    # STUDENT FILTER
    # =====================================================

    if target_group == "Students":

        query += """
            AND target_group LIKE %s
        """

        params.append(
            "%Students%"
        )


    # =====================================================
    # GRADUATE FILTER
    # =====================================================

    elif target_group == "Graduates":

        query += """
            AND target_group LIKE %s
        """

        params.append(
            "%Graduates%"
        )


    # =====================================================
    # WORK MODE
    # =====================================================

    if work_mode:

        query += """
            AND work_mode = %s
        """

        params.append(
            work_mode
        )


    # =====================================================
    # DEADLINE ORDER
    # =====================================================

    query += """
        ORDER BY
            CASE
                WHEN deadline IS NULL THEN 1
                ELSE 0
            END,
            deadline ASC
    """


    cursor.execute(
        query,
        tuple(params)
    )


    opportunities_list = (
        cursor.fetchall()
    )


    cursor.close()
    connection.close()


    return render_template(
        "opportunities.html",

        opportunities=
            opportunities_list,

        search=
            search,

        target_group=
            target_group,

        work_mode=
            work_mode
    )


# =========================================================
# OPPORTUNITY DETAILS
# =========================================================

@app.route(
    "/opportunity/<int:id>"
)
def opportunity_details(id):

    if "user_id" not in session:
        return redirect("/login")


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    cursor.execute(
        """
        SELECT *
        FROM opportunities
        WHERE id = %s
        """,
        (id,)
    )


    opportunity = cursor.fetchone()


    cursor.close()
    connection.close()


    if not opportunity:

        return (
            "Opportunity not found",
            404
        )


    return render_template(
        "opportunity_details.html",
        opportunity=opportunity
    )


# =========================================================
# APPLY FOR OPPORTUNITY
# =========================================================

@app.route(
    "/apply-opportunity/<int:id>",
    methods=["POST"]
)
def apply_opportunity(id):

    if "user_id" not in session:
        return redirect("/login")


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    # =====================================================
    # GET OPPORTUNITY
    # =====================================================

    cursor.execute(
        """
        SELECT *
        FROM opportunities
        WHERE id = %s
        """,
        (id,)
    )


    opportunity = cursor.fetchone()


    if not opportunity:

        cursor.close()
        connection.close()

        return (
            "Opportunity not found",
            404
        )


    # =====================================================
    # CHECK DUPLICATE APPLICATION
    # =====================================================

    cursor.execute(
        """
        SELECT id
        FROM applications
        WHERE user_id = %s
        AND company_name = %s
        AND job_role = %s
        """,
        (
            session["user_id"],
            opportunity["company_name"],
            opportunity["internship_title"]
        )
    )


    existing_application = (
        cursor.fetchone()
    )


    if existing_application:

        cursor.close()
        connection.close()

        return redirect(
            "/applications"
        )


    # =====================================================
    # CREATE APPLICATION
    # =====================================================

    cursor.execute(
        """
        INSERT INTO applications
        (
            user_id,
            company_name,
            job_role,
            application_date,
            status,
            source,
            package,
            notes
        )
        VALUES
        (
            %s,
            %s,
            %s,
            CURDATE(),
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            session["user_id"],
            opportunity["company_name"],
            opportunity["internship_title"],
            "Applied",
            "site",
            opportunity["stipend"],
            "Applied through PlaceTrack Opportunities"
        )
    )


    connection.commit()


    cursor.close()
    connection.close()


    return redirect(
        "/applications"
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            college
        FROM users
        WHERE id = %s
        """,
        (session["user_id"],)
    )


    user = cursor.fetchone()


    cursor.close()
    connection.close()


    if not user:

        return (
            "User not found",
            404
        )


    return render_template(
        "profile.html",
        user=user
    )


# =========================================================
# EDIT PROFILE
# =========================================================

@app.route(
    "/edit-profile",
    methods=["GET", "POST"]
)
def edit_profile():

    if "user_id" not in session:
        return redirect("/login")


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    # =====================================================
    # CURRENT USER
    # =====================================================

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            college
        FROM users
        WHERE id = %s
        """,
        (session["user_id"],)
    )


    user = cursor.fetchone()


    if not user:

        cursor.close()
        connection.close()

        return (
            "User not found",
            404
        )


    if request.method == "POST":

        name = request.form[
            "name"
        ]

        email = request.form[
            "email"
        ]

        college = request.form[
            "college"
        ]


        cursor.execute(
            """
            UPDATE users
            SET
                name = %s,
                email = %s,
                college = %s
            WHERE id = %s
            """,
            (
                name,
                email,
                college,
                session["user_id"]
            )
        )


        connection.commit()


        session["user_name"] = name


        cursor.close()
        connection.close()


        return redirect(
            "/profile"
        )


    cursor.close()
    connection.close()


    return render_template(
        "edit_profile.html",
        user=user
    )


# =========================================================
# ANALYTICS
# =========================================================

@app.route("/analytics")
def analytics():

    if "user_id" not in session:
        return redirect("/login")


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    cursor.execute(
        """
        SELECT *
        FROM applications
        WHERE user_id = %s
        ORDER BY application_date DESC
        """,
        (session["user_id"],)
    )


    applications = cursor.fetchall()


    total = len(
        applications
    )


    applied = sum(
        1
        for application in applications
        if application["status"]
        and application["status"].lower()
        == "applied"
    )


    interviews = sum(
        1
        for application in applications
        if application["status"]
        and application["status"].lower()
        == "interview"
    )


    selected = sum(
        1
        for application in applications
        if application["status"]
        and application["status"].lower()
        == "selected"
    )


    rejected = sum(
        1
        for application in applications
        if application["status"]
        and application["status"].lower()
        == "rejected"
    )


    # =====================================================
    # SELECTION RATE
    # =====================================================

    if total > 0:

        selection_rate = round(
            (selected / total) * 100,
            1
        )

    else:

        selection_rate = 0


    # =====================================================
    # INTERVIEW RATE
    # =====================================================

    if total > 0:

        interview_rate = round(
            (interviews / total) * 100,
            1
        )

    else:

        interview_rate = 0


    cursor.close()
    connection.close()


    return render_template(
        "analytics.html",

        total=
            total,

        applied=
            applied,

        interviews=
            interviews,

        selected=
            selected,

        rejected=
            rejected,

        selection_rate=
            selection_rate,

        interview_rate=
            interview_rate
    )


# =========================================================
# STUDENT - NOTIFICATIONS
# =========================================================

@app.route("/notifications")
def notifications():

    if "user_id" not in session:
        return redirect("/login")


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    cursor.execute(
        """
        SELECT
            id,
            user_id,
            application_id,
            title,
            message,
            is_read,
            created_at
        FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    )


    notifications_list = (
        cursor.fetchall()
    )


    cursor.close()
    connection.close()


    return render_template(
        "notifications.html",
        notifications=
            notifications_list
    )


# =========================================================
# STUDENT - OPEN NOTIFICATION
# =========================================================

@app.route(
    "/notification/<int:id>"
)
def open_notification(id):

    if "user_id" not in session:
        return redirect("/login")


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    # =====================================================
    # GET CURRENT USER'S NOTIFICATION
    # =====================================================

    cursor.execute(
        """
        SELECT
            id,
            application_id
        FROM notifications
        WHERE id = %s
        AND user_id = %s
        """,
        (
            id,
            session["user_id"]
        )
    )


    notification = cursor.fetchone()


    if not notification:

        cursor.close()
        connection.close()

        return (
            "Notification not found",
            404
        )


    # =====================================================
    # MARK NOTIFICATION AS READ
    # =====================================================

    cursor.execute(
        """
        UPDATE notifications
        SET is_read = TRUE
        WHERE id = %s
        AND user_id = %s
        """,
        (
            id,
            session["user_id"]
        )
    )


    connection.commit()


    cursor.close()
    connection.close()


    # =====================================================
    # OPEN RELATED APPLICATION
    # =====================================================

    if notification["application_id"]:

        return redirect(
            f"/applications?application_id="
            f"{notification['application_id']}"
        )


    return redirect(
        "/applications"
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        email = request.form[
            "email"
        ]

        password = request.form[
            "password"
        ]


        connection = get_db_connection()
        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT *
            FROM admins
            WHERE email = %s
            """,
            (email,)
        )


        admin = cursor.fetchone()


        cursor.close()
        connection.close()


        # Current admin password is plain text
        if (
            admin
            and admin["password"] == password
        ):

            session["admin_id"] = (
                admin["id"]
            )

            session["admin_name"] = (
                admin["name"]
            )


            return redirect(
                "/admin"
            )


        return render_template(
            "admin_login.html",
            error=
                "Invalid admin email or password."
        )


    return render_template(
        "admin_login.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin_dashboard():

    if "admin_id" not in session:
        return redirect("/admin/login")


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    # =====================================================
    # ALL OPPORTUNITIES
    # =====================================================

    cursor.execute(
        """
        SELECT *
        FROM opportunities
        ORDER BY created_at DESC
        """
    )


    opportunities_list = (
        cursor.fetchall()
    )


    # =====================================================
    # TOTAL OPPORTUNITIES
    # =====================================================

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM opportunities
        """
    )


    total_opportunities = (
        cursor.fetchone()["total"]
    )


    # =====================================================
    # ACTIVE OPPORTUNITIES
    # =====================================================

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM opportunities
        WHERE deadline IS NULL
        OR deadline >= CURDATE()
        """
    )


    active_opportunities = (
        cursor.fetchone()["total"]
    )


    # =====================================================
    # TOTAL STUDENTS
    # =====================================================

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM users
        """
    )


    total_students = (
        cursor.fetchone()["total"]
    )


    # =====================================================
    # TOTAL APPLICATIONS
    # =====================================================

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM applications
        """
    )


    total_applications = (
        cursor.fetchone()["total"]
    )


    cursor.close()
    connection.close()


    return render_template(
        "admin_dashboard.html",

        opportunities=
            opportunities_list,

        total_opportunities=
            total_opportunities,

        active_opportunities=
            active_opportunities,

        total_students=
            total_students,

        total_applications=
            total_applications
    )


# =========================================================
# ADMIN - ADD OPPORTUNITY
# =========================================================

@app.route(
    "/admin/add-opportunity",
    methods=["GET", "POST"]
)
def admin_add_opportunity():

    if "admin_id" not in session:
        return redirect("/admin/login")


    if request.method == "POST":

        company_name = request.form[
            "company_name"
        ]

        internship_title = request.form[
            "internship_title"
        ]

        description = request.form[
            "description"
        ]

        location = request.form[
            "location"
        ]

        work_mode = request.form[
            "work_mode"
        ]

        internship_type = request.form[
            "internship_type"
        ]

        stipend = request.form[
            "stipend"
        ]

        eligibility = request.form[
            "eligibility"
        ]

        target_group = request.form[
            "target_group"
        ]

        skills = request.form[
            "skills"
        ]

        deadline = (
            request.form["deadline"]
            or None
        )

        apply_url = request.form[
            "apply_url"
        ]


        connection = get_db_connection()
        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO opportunities
            (
                company_name,
                internship_title,
                description,
                location,
                work_mode,
                internship_type,
                stipend,
                eligibility,
                target_group,
                skills,
                deadline,
                apply_url
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                company_name,
                internship_title,
                description,
                location,
                work_mode,
                internship_type,
                stipend,
                eligibility,
                target_group,
                skills,
                deadline,
                apply_url
            )
        )


        connection.commit()


        cursor.close()
        connection.close()


        return redirect(
            "/admin"
        )


    return render_template(
        "admin_add_opportunity.html"
    )


# =========================================================
# ADMIN - EDIT OPPORTUNITY
# =========================================================

@app.route(
    "/admin/edit-opportunity/<int:id>",
    methods=["GET", "POST"]
)
def admin_edit_opportunity(id):

    if "admin_id" not in session:
        return redirect("/admin/login")


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    # =====================================================
    # GET OPPORTUNITY
    # =====================================================

    cursor.execute(
        """
        SELECT *
        FROM opportunities
        WHERE id = %s
        """,
        (id,)
    )


    opportunity = cursor.fetchone()


    if not opportunity:

        cursor.close()
        connection.close()

        return (
            "Opportunity not found",
            404
        )


    if request.method == "POST":

        company_name = request.form[
            "company_name"
        ]

        internship_title = request.form[
            "internship_title"
        ]

        description = request.form[
            "description"
        ]

        location = request.form[
            "location"
        ]

        work_mode = request.form[
            "work_mode"
        ]

        internship_type = request.form[
            "internship_type"
        ]

        stipend = request.form[
            "stipend"
        ]

        eligibility = request.form[
            "eligibility"
        ]

        target_group = request.form[
            "target_group"
        ]

        skills = request.form[
            "skills"
        ]

        deadline = (
            request.form["deadline"]
            or None
        )

        apply_url = request.form[
            "apply_url"
        ]


        cursor.execute(
            """
            UPDATE opportunities
            SET
                company_name = %s,
                internship_title = %s,
                description = %s,
                location = %s,
                work_mode = %s,
                internship_type = %s,
                stipend = %s,
                eligibility = %s,
                target_group = %s,
                skills = %s,
                deadline = %s,
                apply_url = %s
            WHERE id = %s
            """,
            (
                company_name,
                internship_title,
                description,
                location,
                work_mode,
                internship_type,
                stipend,
                eligibility,
                target_group,
                skills,
                deadline,
                apply_url,
                id
            )
        )


        connection.commit()


        cursor.close()
        connection.close()


        return redirect(
            "/admin"
        )


    cursor.close()
    connection.close()


    return render_template(
        "admin_edit_opportunity.html",
        opportunity=opportunity
    )


# =========================================================
# ADMIN - DELETE OPPORTUNITY
# =========================================================

@app.route(
    "/admin/delete-opportunity/<int:id>",
    methods=["POST"]
)
def admin_delete_opportunity(id):

    if "admin_id" not in session:
        return redirect("/admin/login")


    connection = get_db_connection()
    cursor = connection.cursor()


    cursor.execute(
        """
        DELETE FROM opportunities
        WHERE id = %s
        """,
        (id,)
    )


    connection.commit()


    cursor.close()
    connection.close()


    return redirect(
        "/admin"
    )


# =========================================================
# ADMIN - APPLICATIONS
# =========================================================

@app.route(
    "/admin/applications"
)
def admin_applications():

    if "admin_id" not in session:
        return redirect("/admin/login")


    search = request.args.get(
        "search",
        ""
    ).strip()


    status = request.args.get(
        "status",
        ""
    ).strip()


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    query = """
        SELECT
            applications.id,
            applications.company_name,
            applications.job_role,
            applications.application_date,
            applications.status,
            applications.package,
            applications.notes,
            users.name AS student_name,
            users.email AS student_email,
            users.college AS student_college
        FROM applications
        INNER JOIN users
            ON applications.user_id = users.id
        WHERE 1 = 1
    """


    params = []


    # =====================================================
    # SEARCH
    # =====================================================

    if search:

        query += """
            AND (
                users.name LIKE %s
                OR users.email LIKE %s
                OR applications.company_name LIKE %s
                OR applications.job_role LIKE %s
            )
        """


        search_value = f"%{search}%"


        params.extend(
            [
                search_value,
                search_value,
                search_value,
                search_value
            ]
        )


    # =====================================================
    # STATUS FILTER
    # =====================================================

    if status:

        query += """
            AND applications.status = %s
        """

        params.append(
            status
        )


    # =====================================================
    # ORDER
    # =====================================================

    query += """
        ORDER BY applications.application_date DESC
    """


    cursor.execute(
        query,
        tuple(params)
    )


    applications_list = (
        cursor.fetchall()
    )


    cursor.close()
    connection.close()


    return render_template(
        "admin_applications.html",

        applications=
            applications_list,

        search=
            search,

        status=
            status
    )


# =========================================================
# ADMIN - APPLICATION DETAILS
# =========================================================

@app.route(
    "/admin/application/<int:id>"
)
def admin_application_details(id):

    if "admin_id" not in session:
        return redirect("/admin/login")


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    cursor.execute(
        """
        SELECT
            applications.id,
            applications.company_name,
            applications.job_role,
            applications.application_date,
            applications.status,
            applications.package,
            applications.notes,
            users.name AS student_name,
            users.email AS student_email,
            users.college AS student_college
        FROM applications
        INNER JOIN users
            ON applications.user_id = users.id
        WHERE applications.id = %s
        """,
        (id,)
    )


    application = cursor.fetchone()


    cursor.close()
    connection.close()


    if not application:

        return (
            "Application not found",
            404
        )


    return render_template(
        "admin_application_details.html",
        application=application
    )


# =========================================================
# ADMIN - UPDATE APPLICATION STATUS
# =========================================================

@app.route(
    "/admin/application/<int:id>/status",
    methods=["POST"]
)
def admin_update_application_status(id):

    if "admin_id" not in session:
        return redirect("/admin/login")


    new_status = request.form[
        "status"
    ]


    allowed_statuses = [
        "Applied",
        "Assessment",
        "Interview",
        "Selected",
        "Rejected"
    ]


    if new_status not in allowed_statuses:

        return (
            "Invalid status",
            400
        )


    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )


    # =====================================================
    # GET CURRENT APPLICATION
    # =====================================================

    cursor.execute(
        """
        SELECT
            applications.id,
            applications.user_id,
            applications.company_name,
            applications.job_role,
            applications.status,
            users.name AS student_name
        FROM applications
        INNER JOIN users
            ON applications.user_id = users.id
        WHERE applications.id = %s
        """,
        (id,)
    )


    application = cursor.fetchone()


    if not application:

        cursor.close()
        connection.close()

        return (
            "Application not found",
            404
        )


    old_status = application[
        "status"
    ]


    # =====================================================
    # UPDATE ONLY WHEN STATUS CHANGED
    # =====================================================

    if old_status != new_status:

        cursor.execute(
            """
            UPDATE applications
            SET status = %s
            WHERE id = %s
            """,
            (
                new_status,
                id
            )
        )


        # =================================================
        # CREATE NOTIFICATION
        # =================================================

        title = (
            "Application Status Updated"
        )


        message = (
            f"Your application for "
            f"{application['job_role']} at "
            f"{application['company_name']} "
            f"has been moved from "
            f"{old_status} to "
            f"{new_status}."
        )


        cursor.execute(
            """
            INSERT INTO notifications
            (
                user_id,
                application_id,
                title,
                message
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                application["user_id"],
                application["id"],
                title,
                message
            )
        )


    connection.commit()


    cursor.close()
    connection.close()


    return redirect(
        f"/admin/application/{id}"
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route(
    "/admin/logout"
)
def admin_logout():

    session.pop(
        "admin_id",
        None
    )

    session.pop(
        "admin_name",
        None
    )


    return redirect(
        "/admin/login"
    )


# =========================================================
# USER LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        "/login"
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )