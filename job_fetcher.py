import requests
import re
from database import get_db_connection
from datetime import datetime


# =========================================================
# CONFIGURATION
# =========================================================

LEVER_COMPANIES = {
    "Dun & Bradstreet": "dnb",
    "ValGenesis": "valgenesis",
    "Neuron7": "neuron7",
    "Sonatype": "sonatype",
    "Turvo": "turvo",
    "TSMG": "tsmg",
    "3Pillar Global": "3pillarglobal",
    "Everbridge": "everbridge",
    "Hevo Data": "hevodata"
}


# =========================================================
# INDIA FILTER
# =========================================================

INDIA_KEYWORDS = [
    "India",
    "Mumbai",
    "Hyderabad",
    "Chennai",
    "Bengaluru",
    "Bangalore",
    "Delhi",
    "Gurgaon",
    "Gurugram",
    "Pune",
    "Noida",
    "Kolkata"
]


# =========================================================
# RELEVANT ROLE KEYWORDS
# =========================================================

ROLE_KEYWORDS = [
    "analyst",
    "data analyst",
    "data scientist",
    "business analyst",
    "software engineer",
    "software developer",
    "developer",
    "engineer",
    "java",
    "python",
    "frontend",
    "front end",
    "backend",
    "back end",
    "full stack",
    "machine learning",
    "ai",
    "ml",
    "quality assurance",
    "qa",
    "web developer",
    "intern",
    "internship",
    "trainee",
    "apprentice",
    "graduate"
]


# =========================================================
# EXCLUDE EXPERIENCED ROLES
# =========================================================

EXCLUDED_TITLE_KEYWORDS = [
    "senior",
    "sr.",
    "sr ",
    "staff",
    "lead",
    "manager",
    "director",
    "principal",
    "vice president",
    "vp ",
    "head of",
    "chief",
    "architect"
]


# =========================================================
# FETCH LEVER JOBS
# =========================================================

def fetch_lever_jobs(company_name, company_slug):

    url = (
        f"https://api.lever.co/v0/postings/"
        f"{company_slug}?mode=json"
    )

    print()
    print("=" * 70)
    print(f"FETCHING: {company_name}")
    print("=" * 70)

    print(
        f"Company slug : {company_slug}"
    )

    print(
        f"URL          : {url}"
    )

    try:

        response = requests.get(
            url,
            timeout=30
        )

        print(
            "HTTP Status  :",
            response.status_code
        )

        response.raise_for_status()

        jobs = response.json()

        print(
            "Jobs received:",
            len(jobs)
        )

        return jobs

    except requests.exceptions.RequestException as error:

        print()
        print(
            f"ERROR while fetching {company_name}:"
        )

        print(error)

        return []


# =========================================================
# LOCATION CHECK
# =========================================================

def is_india_job(location):

    if not location:
        return False

    location_lower = location.lower()

    return any(
        keyword.lower() in location_lower
        for keyword in INDIA_KEYWORDS
    )


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# =========================================================
# ROLE CHECK
# =========================================================

def is_relevant_role(title, description=""):

    title_normalized = normalize_text(
        title
    )

    description_normalized = normalize_text(
        description
    )

    # -----------------------------------------------------
    # EXCLUDE EXPERIENCED POSITIONS
    # -----------------------------------------------------

    for keyword in EXCLUDED_TITLE_KEYWORDS:

        keyword_normalized = normalize_text(
            keyword
        )

        pattern = (
            rf"\b{re.escape(keyword_normalized)}\b"
        )

        if re.search(
            pattern,
            title_normalized
        ):
            return False

    # -----------------------------------------------------
    # CHECK RELEVANT ROLE
    # -----------------------------------------------------

    combined_text = (
        f"{title_normalized} "
        f"{description_normalized}"
    )

    for keyword in ROLE_KEYWORDS:

        keyword_normalized = normalize_text(
            keyword
        )

        pattern = (
            rf"\b{re.escape(keyword_normalized)}\b"
        )

        if re.search(
            pattern,
            combined_text
        ):
            return True

    return False


# =========================================================
# DETERMINE WORK MODE
# =========================================================

def get_work_mode(job):

    workplace_type = (
        job.get("workplaceType")
        or ""
    ).lower()

    location = (
        job.get("categories", {})
        .get("location", "")
        or ""
    ).lower()

    combined = (
        workplace_type
        + " "
        + location
    )

    if "remote" in combined:
        return "Remote"

    if "hybrid" in combined:
        return "Hybrid"

    return "On-site"


# =========================================================
# DETERMINE JOB TYPE
# =========================================================

def get_job_type(job):

    commitment = (
        job.get("categories", {})
        .get("commitment", "")
        or ""
    ).lower()

    title = (
        job.get("text", "")
        or ""
    ).lower()

    combined = (
        commitment
        + " "
        + title
    )

    if "intern" in combined:
        return "Internship"

    if "apprentice" in combined:
        return "Apprenticeship"

    if "trainee" in combined:
        return "Trainee"

    return "Full Time"


# =========================================================
# CLEAN DESCRIPTION
# =========================================================

def get_description(job):

    description = (
        job.get("descriptionPlain")
        or job.get("description")
        or ""
    )

    return description.strip()


# =========================================================
# NORMALIZE ONE JOB
# =========================================================

def normalize_job(job, company_name):

    categories = (
        job.get("categories")
        or {}
    )

    title = (
        job.get("text")
        or "Untitled Opportunity"
    ).strip()

    location = (
        categories.get("location")
        or "Location not specified"
    ).strip()

    description = get_description(
        job
    )

    apply_url = (
        job.get("applyUrl")
        or job.get("hostedUrl")
        or ""
    )

    source_url = (
        job.get("hostedUrl")
        or apply_url
        or ""
    )

    source_job_id = (
        job.get("id")
        or apply_url
    )

    work_mode = get_work_mode(
        job
    )

    internship_type = get_job_type(
        job
    )

    # Lever may not provide salary in this response.
    stipend = None

    # Do not invent eligibility.
    eligibility = (
        "See company job description"
    )

    target_group = (
        "Students, Graduates"
    )

    return {
        "company_name": company_name,
        "internship_title": title,
        "description": description,
        "location": location,
        "work_mode": work_mode,
        "internship_type": internship_type,
        "stipend": stipend,
        "eligibility": eligibility,
        "target_group": target_group,
        "skills": "",
        "deadline": None,
        "apply_url": apply_url,
        "source": f"Lever - {company_name}",
        "source_job_id": source_job_id,
        "source_url": source_url,
        "is_active": True
    }


# =========================================================
# SAVE / UPDATE JOB
# =========================================================

def save_job(connection, job):

    cursor = connection.cursor()

    # -----------------------------------------------------
    # CHECK EXISTING JOB
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM opportunities
        WHERE source = %s
        AND source_job_id = %s
        """,
        (
            job["source"],
            job["source_job_id"]
        )
    )

    existing = cursor.fetchone()

    # -----------------------------------------------------
    # UPDATE EXISTING JOB
    # -----------------------------------------------------

    if existing:

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
                apply_url = %s,
                source_url = %s,
                last_synced = %s,
                is_active = %s
            WHERE id = %s
            """,
            (
                job["company_name"],
                job["internship_title"],
                job["description"],
                job["location"],
                job["work_mode"],
                job["internship_type"],
                job["stipend"],
                job["eligibility"],
                job["target_group"],
                job["skills"],
                job["deadline"],
                job["apply_url"],
                job["source_url"],
                datetime.now(),
                job["is_active"],
                existing[0]
            )
        )

        print(
            f"UPDATED: "
            f"{job['company_name']} - "
            f"{job['internship_title']}"
        )

        cursor.close()

        return "updated"

    # -----------------------------------------------------
    # INSERT NEW JOB
    # -----------------------------------------------------

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
            apply_url,
            source,
            source_job_id,
            source_url,
            last_synced,
            is_active
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
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            job["company_name"],
            job["internship_title"],
            job["description"],
            job["location"],
            job["work_mode"],
            job["internship_type"],
            job["stipend"],
            job["eligibility"],
            job["target_group"],
            job["skills"],
            job["deadline"],
            job["apply_url"],
            job["source"],
            job["source_job_id"],
            job["source_url"],
            datetime.now(),
            job["is_active"]
        )
    )

    print(
        f"IMPORTED: "
        f"{job['company_name']} - "
        f"{job['internship_title']}"
    )

    cursor.close()

    return "inserted"


# =========================================================
# UPDATE SOURCE SYNC TIME
# =========================================================

def update_source_sync_time(
    connection,
    company_name,
    company_slug
):

    cursor = connection.cursor()

    source_name = (
        f"Lever - {company_name}"
    )

    # -----------------------------------------------------
    # CREATE SOURCE RECORD IF IT DOESN'T EXIST
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM job_sources
        WHERE source_name = %s
        """,
        (source_name,)
    )

    existing = cursor.fetchone()

    if existing:

        cursor.execute(
            """
            UPDATE job_sources
            SET
                source_type = %s,
                base_url = %s,
                is_active = TRUE,
                last_synced = %s
            WHERE id = %s
            """,
            (
                "API",
                f"https://api.lever.co/v0/postings/{company_slug}",
                datetime.now(),
                existing[0]
            )
        )

    else:

        cursor.execute(
            """
            INSERT INTO job_sources
            (
                source_name,
                source_type,
                base_url,
                is_active,
                last_synced
            )
            VALUES
            (
                %s,
                %s,
                %s,
                TRUE,
                %s
            )
            """,
            (
                source_name,
                "API",
                f"https://api.lever.co/v0/postings/{company_slug}",
                datetime.now()
            )
        )

    cursor.close()


# =========================================================
# SYNC ALL COMPANIES
# =========================================================

def sync_jobs():

    total_received = 0
    total_imported = 0
    total_updated = 0
    total_skipped = 0
    total_failed = 0

    connection = get_db_connection()

    print()
    print("=" * 70)
    print("PLACETRACK MULTI-COMPANY JOB SYNC")
    print("=" * 70)

    print(
        f"Companies configured: "
        f"{len(LEVER_COMPANIES)}"
    )

    print()

    # -----------------------------------------------------
    # LOOP THROUGH ALL COMPANIES
    # -----------------------------------------------------

    for company_name, company_slug in (
        LEVER_COMPANIES.items()
    ):

        jobs = fetch_lever_jobs(
            company_name,
            company_slug
        )

        # -------------------------------------------------
        # SOURCE FAILED
        # -------------------------------------------------

        if not jobs:

            total_failed += 1

            print(
                f"Skipping {company_name} "
                f"because no jobs were received."
            )

            continue

        total_received += len(jobs)

        imported_count = 0
        updated_count = 0
        skipped_count = 0

        print()
        print(
            f"PROCESSING: {company_name}"
        )

        print("-" * 70)

        # -------------------------------------------------
        # PROCESS JOBS
        # -------------------------------------------------

        for job in jobs:

            title = (
                job.get("text")
                or ""
            ).strip()

            location = (
                job.get("categories", {})
                .get("location", "")
                or ""
            ).strip()

            description = get_description(
                job
            )

            # ---------------------------------------------
            # INDIA FILTER
            # ---------------------------------------------

            if not is_india_job(
                location
            ):

                skipped_count += 1
                total_skipped += 1

                continue

            # ---------------------------------------------
            # ROLE FILTER
            # ---------------------------------------------

            if not is_relevant_role(
                title,
                description
            ):

                skipped_count += 1
                total_skipped += 1

                continue

            # ---------------------------------------------
            # NORMALIZE
            # ---------------------------------------------

            normalized_job = normalize_job(
                job,
                company_name
            )

            # ---------------------------------------------
            # SAVE
            # ---------------------------------------------

            result = save_job(
                connection,
                normalized_job
            )

            if result == "inserted":

                imported_count += 1
                total_imported += 1

            elif result == "updated":

                updated_count += 1
                total_updated += 1

        # -------------------------------------------------
        # UPDATE SOURCE SYNC TIME
        # -------------------------------------------------

        update_source_sync_time(
            connection,
            company_name,
            company_slug
        )

        connection.commit()

        print()
        print(
            f"Finished: {company_name}"
        )

        print(
            f"Imported: {imported_count}"
        )

        print(
            f"Updated : {updated_count}"
        )

        print(
            f"Skipped : {skipped_count}"
        )

    # -----------------------------------------------------
    # CLOSE DATABASE
    # -----------------------------------------------------

    connection.commit()
    connection.close()

    # -----------------------------------------------------
    # FINAL SUMMARY
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("MULTI-COMPANY SYNC COMPLETED")
    print("=" * 70)

    print(
        f"Companies checked : "
        f"{len(LEVER_COMPANIES)}"
    )

    print(
        f"Sources failed    : "
        f"{total_failed}"
    )

    print(
        f"Jobs received     : "
        f"{total_received}"
    )

    print(
        f"Imported          : "
        f"{total_imported}"
    )

    print(
        f"Updated           : "
        f"{total_updated}"
    )

    print(
        f"Skipped           : "
        f"{total_skipped}"
    )

    print("=" * 70)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    sync_jobs()