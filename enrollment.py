
from flask import request, jsonify, render_template
from db import get_connection


def enrollment_routes(app):

    # ---------------------------------
    # GET - Enrollment Page
    # ---------------------------------

    @app.route("/enrollments", methods=["GET"])
    def enrollment_page():
        return render_template("enrollment.html")


    # ---------------------------------
    # POST - Add Enrollment
    # ---------------------------------

    @app.route("/enrollments", methods=["POST"])
    def add_enrollment():

        try:

            data = request.get_json()

            if not data:
                return jsonify({
                    "error": "No data received"
                }), 400

            student_id = data.get("student_id")
            course_id = data.get("course_id")

            if not student_id:
                return jsonify({
                    "error": "Student ID is required"
                }), 400

            if not course_id:
                return jsonify({
                    "error": "Course ID is required"
                }), 400

            conn = get_connection()
            cursor = conn.cursor()


            # ---------------------------------
            # Check Student Exists
            # ---------------------------------

            cursor.execute("""
                SELECT id
                FROM student
                WHERE id = ?
            """, (student_id,))

            student = cursor.fetchone()

            if not student:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Student not found"
                }), 404


            # ---------------------------------
            # Check Course Exists
            # ---------------------------------

            cursor.execute("""
                SELECT id
                FROM courses
                WHERE id = ?
            """, (course_id,))

            course = cursor.fetchone()

            if not course:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Course not found"
                }), 404


            # ---------------------------------
            # Check Duplicate Enrollment
            # ---------------------------------

            cursor.execute("""
                SELECT id
                FROM enrollments
                WHERE student_id = ?
                AND course_id = ?
            """, (student_id, course_id))

            existing_enrollment = cursor.fetchone()

            if existing_enrollment:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Student is already enrolled in this course"
                }), 400


            # ---------------------------------
            # Insert Enrollment
            # ---------------------------------

            cursor.execute("""
                INSERT INTO enrollments
                (
                    student_id,
                    course_id,
                    status
                )
                VALUES (?, ?, ?)
            """, (
                student_id,
                course_id,
                "Active"
            ))

            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({
                "message": "Enrollment added successfully"
            }), 201


        except Exception as e:

            print("ADD ENROLLMENT ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500

    @app.route("/enrollments/<int:id>", methods=["PUT"])
    def update_enrollment_status(id):

        try:

            data = request.get_json()

            if not data:
                return jsonify({
                    "error": "No data received"
                }), 400

            status = data.get("status")

            if status not in ["Active", "Completed"]:
                return jsonify({
                    "error": "Status must be Active or Completed"
                }), 400

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id
                FROM enrollments
                WHERE id = ?
            """, (id,))

            enrollment = cursor.fetchone()

            if not enrollment:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Enrollment not found"
                }), 404

            cursor.execute("""
                UPDATE enrollments
                SET status = ?
                WHERE id = ?
            """, (status, id))

            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({
                "message": "Enrollment status updated successfully"
            }), 200

        except Exception as e:

            print("UPDATE ENROLLMENT STATUS ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500

    # ---------------------------------
    # GET Student's Courses
    # ---------------------------------

    @app.route(
        "/students/<int:student_id>/courses",
        methods=["GET"]
    )
    def get_student_courses(student_id):

        try:

            conn = get_connection()
            cursor = conn.cursor()


            # ---------------------------------
            # Check Student Exists
            # ---------------------------------

            cursor.execute("""
                SELECT id
                FROM student
                WHERE id = ?
            """, (student_id,))

            student = cursor.fetchone()

            if not student:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Student not found"
                }), 404


            # ---------------------------------
            # Get Student's Courses
            # ---------------------------------

            cursor.execute("""
                SELECT
                    c.id,
                    c.course_name,
                    c.course_code,
                    c.duration,
                    c.fee,
                    e.enrollment_date,
                    e.status
                FROM enrollments e
                INNER JOIN courses c
                    ON e.course_id = c.id
                WHERE e.student_id = ?
            """, (student_id,))

            rows = cursor.fetchall()

            courses = []

            for row in rows:

                courses.append({

                    "course_id": row[0],

                    "course_name": row[1],

                    "course_code": row[2],

                    "duration": row[3],

                    "fee": row[4],

                    "enrollment_date": str(row[5]),

                    "status": row[6]

                })


            cursor.close()
            conn.close()

            return jsonify(courses), 200


        except Exception as e:

            print("GET STUDENT COURSES ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ---------------------------------
    # GET Course's Students
    # ---------------------------------

    @app.route(
        "/courses/<int:course_id>/students",
        methods=["GET"]
    )
    def get_course_students(course_id):

        try:

            conn = get_connection()
            cursor = conn.cursor()


            # ---------------------------------
            # Check Course Exists
            # ---------------------------------

            cursor.execute("""
                SELECT id
                FROM courses
                WHERE id = ?
            """, (course_id,))

            course = cursor.fetchone()

            if not course:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Course not found"
                }), 404


            # ---------------------------------
            # Get Course's Students
            # ---------------------------------

            cursor.execute("""
                SELECT
                    s.id,
                    s.name,
                    s.email,
                    s.phone,
                    e.enrollment_date,
                    e.status
                FROM enrollments e
                INNER JOIN student s
                    ON e.student_id = s.id
                WHERE e.course_id = ?
            """, (course_id,))

            rows = cursor.fetchall()

            students = []

            for row in rows:

                students.append({

                    "student_id": row[0],

                    "name": row[1],

                    "email": row[2],

                    "phone": row[3],

                    "enrollment_date": str(row[4]),

                    "status": row[5]

                })


            cursor.close()
            conn.close()

            return jsonify(students), 200


        except Exception as e:

            print("GET COURSE STUDENTS ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500

