
from flask import render_template, request, jsonify
from db import get_connection


def marks_routes(app):
    @app.route("/marks", methods=["GET"])
    def marks_page():
       return render_template("marks.html")

    # ---------------------------------
    # POST - Add Marks
    # ---------------------------------

    @app.route("/marks", methods=["POST"])
    def add_marks():

        try:

            data = request.get_json()

            if not data:
                return jsonify({
                    "error": "No data received"
                }), 400

            student_id = data.get("student_id")
            course_id = data.get("course_id")
            subject = data.get("subject")
            marks = data.get("marks")
            max_marks = data.get("max_marks")

            # Check required fields
            if not student_id:
                return jsonify({
                    "error": "Student ID is required"
                }), 400

            if not course_id:
                return jsonify({
                    "error": "Course ID is required"
                }), 400

            if not subject or not subject.strip():
                return jsonify({
                    "error": "Subject is required"
                }), 400

            if marks is None:
                return jsonify({
                    "error": "Marks is required"
                }), 400

            if max_marks is None:
                return jsonify({
                    "error": "Maximum marks is required"
                }), 400

            # Convert marks to number
            try:
                marks = int(marks)
                max_marks = int(max_marks)

            except (ValueError, TypeError):

                return jsonify({
                    "error": "Marks and maximum marks must be numbers"
                }), 400


            # Validate marks
            if marks < 0:

                return jsonify({
                    "error": "Marks cannot be negative"
                }), 400


            if max_marks <= 0:

                return jsonify({
                    "error": "Maximum marks must be greater than 0"
                }), 400


            if marks > max_marks:

                return jsonify({
                    "error": "Marks cannot be greater than maximum marks"
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
            # Check Student Enrolled
            # ---------------------------------

            cursor.execute("""
                SELECT id
                FROM enrollments
                WHERE student_id = ?
                AND course_id = ?
            """, (student_id, course_id))

            enrollment = cursor.fetchone()

            if not enrollment:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Student is not enrolled in this course"
                }), 400


            # ---------------------------------
            # Insert Marks
            # ---------------------------------

            cursor.execute("""
                INSERT INTO marks
                (
                    student_id,
                    course_id,
                    subject,
                    marks,
                    max_marks
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                student_id,
                course_id,
                subject.strip(),
                marks,
                max_marks
            ))

            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({
                "message": "Marks added successfully"
            }), 201


        except Exception as e:

            print("ADD MARKS ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ---------------------------------
    # PUT - Update Marks
    # ---------------------------------

    @app.route("/marks/<int:id>", methods=["PUT"])
    def update_marks(id):

        try:

            data = request.get_json()

            if not data:
                return jsonify({
                    "error": "No data received"
                }), 400

            marks = data.get("marks")
            max_marks = data.get("max_marks")

            if marks is None:
                return jsonify({
                    "error": "Marks is required"
                }), 400

            if max_marks is None:
                return jsonify({
                    "error": "Maximum marks is required"
                }), 400

            try:

                marks = int(marks)
                max_marks = int(max_marks)

            except (ValueError, TypeError):

                return jsonify({
                    "error": "Marks and maximum marks must be numbers"
                }), 400


            if marks < 0:

                return jsonify({
                    "error": "Marks cannot be negative"
                }), 400


            if max_marks <= 0:

                return jsonify({
                    "error": "Maximum marks must be greater than 0"
                }), 400


            if marks > max_marks:

                return jsonify({
                    "error": "Marks cannot be greater than maximum marks"
                }), 400


            conn = get_connection()
            cursor = conn.cursor()


            # ---------------------------------
            # Check Marks Record Exists
            # ---------------------------------

            cursor.execute("""
                SELECT id
                FROM marks
                WHERE id = ?
            """, (id,))

            existing_marks = cursor.fetchone()

            if not existing_marks:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Marks record not found"
                }), 404


            # ---------------------------------
            # Update Marks
            # ---------------------------------

            cursor.execute("""
                UPDATE marks
                SET
                    marks = ?,
                    max_marks = ?
                WHERE id = ?
            """, (
                marks,
                max_marks,
                id
            ))

            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({
                "message": "Marks updated successfully"
            }), 200


        except Exception as e:

            print("UPDATE MARKS ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ---------------------------------
    # GET - Student Marks
    # ---------------------------------

    @app.route(
        "/students/<int:student_id>/marks",
        methods=["GET"]
    )
    def get_student_marks(student_id):

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
            # Get Student Marks
            # ---------------------------------

            cursor.execute("""
                SELECT
                    m.id,
                    m.course_id,
                    c.course_name,
                    c.course_code,
                    m.subject,
                    m.marks,
                    m.max_marks
                FROM marks m
                INNER JOIN courses c
                    ON m.course_id = c.id
                WHERE m.student_id = ?
                ORDER BY m.id
            """, (student_id,))

            rows = cursor.fetchall()

            marks_list = []

            for row in rows:

                marks_list.append({

                    "id": row[0],

                    "course_id": row[1],

                    "course_name": row[2],

                    "course_code": row[3],

                    "subject": row[4],

                    "marks": row[5],

                    "max_marks": row[6]

                })


            cursor.close()
            conn.close()

            return jsonify(marks_list), 200


        except Exception as e:

            print("GET STUDENT MARKS ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ---------------------------------
    # GET - Student Result
    # ---------------------------------

    @app.route(
        "/students/<int:student_id>/result",
        methods=["GET"]
    )
    def get_student_result(student_id):

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
            # Get Total and Maximum Marks
            # ---------------------------------

            cursor.execute("""
                SELECT
                    ISNULL(SUM(marks), 0),
                    ISNULL(SUM(max_marks), 0)
                FROM marks
                WHERE student_id = ?
            """, (student_id,))

            row = cursor.fetchone()

            total_marks = row[0]
            maximum_marks = row[1]


            # ---------------------------------
            # Calculate Percentage
            # ---------------------------------

            if maximum_marks > 0:

                percentage = (
                    total_marks / maximum_marks
                ) * 100

            else:

                percentage = 0


            # ---------------------------------
            # Calculate Grade
            # ---------------------------------

            if percentage >= 90:

                grade = "A+"

            elif percentage >= 80:

                grade = "A"

            elif percentage >= 70:

                grade = "B"

            elif percentage >= 60:

                grade = "C"

            elif percentage >= 50:

                grade = "D"

            else:

                grade = "F"


            cursor.close()
            conn.close()


            return jsonify({

                "student_id": student_id,

                "total_marks": total_marks,

                "maximum_marks": maximum_marks,

                "percentage": round(percentage, 2),

                "grade": grade

            }), 200


        except Exception as e:

            print("GET STUDENT RESULT ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500

