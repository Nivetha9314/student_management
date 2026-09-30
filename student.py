from flask import request, jsonify, render_template
from db import get_connection
import re


def student_routes(app):

    # ==========================================
    # STUDENT HTML PAGE
    # ==========================================

    @app.route("/students")
    def student_page():
        return render_template("student.html")


    # ==========================================
    # GET ALL STUDENTS
    # ==========================================

    @app.route("/students/all", methods=["GET"])
    def get_students():

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    phone,
                    date_of_birth,
                    gender,
                    address
                FROM student
            """)

            rows = cursor.fetchall()

            students = []

            for row in rows:

                students.append({
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "date_of_birth": str(row[4]),
                    "gender": row[5],
                    "address": row[6]
                })

            cursor.close()
            conn.close()

            return jsonify(students), 200

        except Exception as e:

            print("GET ALL STUDENTS ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ==========================================
    # GET STUDENT BY ID
    # ==========================================

    @app.route("/students/<int:id>", methods=["GET"])
    def get_student(id):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    phone,
                    date_of_birth,
                    gender,
                    address
                FROM student
                WHERE id = ?
            """, (id,))

            row = cursor.fetchone()

            cursor.close()
            conn.close()

            if not row:

                return jsonify({
                    "error": "Student not found"
                }), 404

            student = {

                "id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "date_of_birth": str(row[4]),
                "gender": row[5],
                "address": row[6]

            }

            return jsonify(student), 200

        except Exception as e:

            print("GET STUDENT ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ==========================================
    # ADD STUDENT
    # ==========================================

    @app.route("/students", methods=["POST"])
    def add_student():

        try:

            data = request.get_json()

            if not data:

                return jsonify({
                    "error": "No data received"
                }), 400


            name = data.get("name", "").strip()
            email = data.get("email", "").strip()
            phone = data.get("phone", "").strip()
            date_of_birth = data.get("date_of_birth")
            gender = data.get("gender")
            address = data.get("address", "").strip()


            # -------------------------
            # NAME VALIDATION
            # -------------------------

            if not name:

                return jsonify({
                    "error": "Name should not be empty"
                }), 400


            # -------------------------
            # EMAIL VALIDATION
            # -------------------------

            if not email:

                return jsonify({
                    "error": "Email should not be empty"
                }), 400


            email_pattern = (
                r"^[A-Za-z0-9._%+-]+"
                r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
            )

            if not re.match(email_pattern, email):

                return jsonify({
                    "error": "Enter a valid email address"
                }), 400


            # -------------------------
            # PHONE VALIDATION
            # -------------------------

            if not phone:

                return jsonify({
                    "error": "Phone should not be empty"
                }), 400


            if not phone.isdigit():

                return jsonify({
                    "error": "Phone should contain only digits"
                }), 400


            if len(phone) != 10:

                return jsonify({
                    "error": "Phone number must contain 10 digits"
                }), 400


            # -------------------------
            # DOB VALIDATION
            # -------------------------

            if not date_of_birth:

                return jsonify({
                    "error": "Date of birth is required"
                }), 400


            # -------------------------
            # GENDER VALIDATION
            # -------------------------

            if not gender:

                return jsonify({
                    "error": "Gender is required"
                }), 400


            # -------------------------
            # DATABASE CONNECTION
            # -------------------------

            conn = get_connection()
            cursor = conn.cursor()


            # -------------------------
            # CHECK DUPLICATE EMAIL
            # -------------------------

            cursor.execute("""
                SELECT id
                FROM student
                WHERE email = ?
            """, (email,))

            existing_student = cursor.fetchone()


            if existing_student:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Email already exists"
                }), 400


            # -------------------------
            # INSERT STUDENT
            # -------------------------

            cursor.execute("""
                INSERT INTO student
                (
                    name,
                    email,
                    phone,
                    date_of_birth,
                    gender,
                    address
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name,
                email,
                phone,
                date_of_birth,
                gender,
                address
            ))


            conn.commit()

            cursor.close()
            conn.close()


            return jsonify({
                "message": "Student added successfully"
            }), 201


        except Exception as e:

            print("ADD STUDENT ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ==========================================
    # UPDATE STUDENT
    # ==========================================

    @app.route("/students/<int:id>", methods=["PUT"])
    def update_student(id):

        try:

            data = request.get_json()

            if not data:

                return jsonify({
                    "error": "No data received"
                }), 400


            name = data.get("name", "").strip()
            email = data.get("email", "").strip()
            phone = data.get("phone", "").strip()
            date_of_birth = data.get("date_of_birth")
            gender = data.get("gender")
            address = data.get("address", "").strip()


            # Name

            if not name:

                return jsonify({
                    "error": "Name should not be empty"
                }), 400


            # Email

            if not email:

                return jsonify({
                    "error": "Email should not be empty"
                }), 400


            email_pattern = (
                r"^[A-Za-z0-9._%+-]+"
                r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
            )

            if not re.match(email_pattern, email):

                return jsonify({
                    "error": "Enter a valid email address"
                }), 400


            # Phone

            if not phone.isdigit():

                return jsonify({
                    "error": "Phone should contain only digits"
                }), 400


            if len(phone) != 10:

                return jsonify({
                    "error": "Phone number must contain 10 digits"
                }), 400


            # DOB

            if not date_of_birth:

                return jsonify({
                    "error": "Date of birth is required"
                }), 400


            # Gender

            if not gender:

                return jsonify({
                    "error": "Gender is required"
                }), 400


            conn = get_connection()
            cursor = conn.cursor()


            # Check student exists

            cursor.execute("""
                SELECT id
                FROM student
                WHERE id = ?
            """, (id,))

            student = cursor.fetchone()


            if not student:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Student not found"
                }), 404


            # Check duplicate email

            cursor.execute("""
                SELECT id
                FROM student
                WHERE email = ?
                AND id != ?
            """, (email, id))

            existing_email = cursor.fetchone()


            if existing_email:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Email already exists"
                }), 400


            # Update

            cursor.execute("""
                UPDATE student
                SET
                    name = ?,
                    email = ?,
                    phone = ?,
                    date_of_birth = ?,
                    gender = ?,
                    address = ?
                WHERE id = ?
            """, (
                name,
                email,
                phone,
                date_of_birth,
                gender,
                address,
                id
            ))


            conn.commit()

            cursor.close()
            conn.close()


            return jsonify({
                "message": "Student updated successfully"
            }), 200


        except Exception as e:

            print("UPDATE STUDENT ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ==========================================
    # DELETE STUDENT
    # ==========================================

    @app.route("/students/<int:id>", methods=["DELETE"])
    def delete_student(id):

        try:

            conn = get_connection()
            cursor = conn.cursor()


            # Check student exists

            cursor.execute("""
                SELECT id
                FROM student
                WHERE id = ?
            """, (id,))

            student = cursor.fetchone()


            if not student:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Student not found"
                }), 404


            # Delete

            cursor.execute("""
                DELETE FROM student
                WHERE id = ?
            """, (id,))


            conn.commit()

            cursor.close()
            conn.close()


            return jsonify({
                "message": "Student deleted successfully"
            }), 200


        except Exception as e:

            print("DELETE STUDENT ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ==========================================
    # SEARCH STUDENT
    # ==========================================

    @app.route("/students/search", methods=["GET"])
    def search_students():

        try:

            name = request.args.get("name", "").strip()


            if not name:

                return jsonify({
                    "error": "Name is required"
                }), 400


            conn = get_connection()
            cursor = conn.cursor()


            cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    phone,
                    date_of_birth,
                    gender,
                    address
                FROM student
                WHERE name LIKE ?
            """, ("%" + name + "%",))


            rows = cursor.fetchall()

            students = []


            for row in rows:

                students.append({

                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "date_of_birth": str(row[4]),
                    "gender": row[5],
                    "address": row[6]

                })


            cursor.close()
            conn.close()


            return jsonify(students), 200


        except Exception as e:

            print("SEARCH STUDENT ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500