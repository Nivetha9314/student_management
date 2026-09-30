from flask import request, jsonify, render_template
from db import get_connection
import re


def course_routes(app):

    # ==========================================
    # COURSE HTML PAGE
    # ==========================================

    @app.route("/courses")
    def course_page():
        return render_template("course.html")


    # ==========================================
    # GET ALL COURSES
    # ==========================================

    @app.route("/courses/all", methods=["GET"])
    def get_courses():

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    course_name,
                    course_code,
                    duration,
                    fee,
                    description,
                    created_at
                FROM courses
            """)

            rows = cursor.fetchall()

            courses = []

            for row in rows:

                courses.append({
                    "id": row[0],
                    "course_name": row[1],
                    "course_code": row[2],
                    "duration": row[3],
                    "fee": row[4],
                    "description": row[5],
                    "created_at": str(row[6])
                })

            cursor.close()
            conn.close()

            return jsonify(courses), 200

        except Exception as e:

            print("GET ALL COURSES ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ==========================================
    # GET COURSE BY ID
    # ==========================================

    @app.route("/courses/<int:id>", methods=["GET"])
    def get_course(id):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    course_name,
                    course_code,
                    duration,
                    fee,
                    description,
                    created_at
                FROM courses
                WHERE id = ?
            """, (id,))

            row = cursor.fetchone()

            cursor.close()
            conn.close()

            if not row:

                return jsonify({
                    "error": "Course not found"
                }), 404

            course = {

                "id": row[0],
                "course_name": row[1],
                "course_code": row[2],
                "duration": row[3],
                "fee": row[4],
                "description": row[5],
                "created_at": str(row[6])

            }

            return jsonify(course), 200

        except Exception as e:

            print("GET COURSE ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ==========================================
    # ADD COURSE
    # ==========================================

    @app.route("/courses", methods=["POST"])
    def add_course():

        try:

            data = request.get_json()

            if not data:

                return jsonify({
                    "error": "No data received"
                }), 400


            course_name = data.get(
                "course_name", ""
            ).strip()

            course_code = data.get(
                "course_code", ""
            ).strip()

            duration = data.get(
                "duration", ""
            ).strip()

            fee = data.get("fee")

            description = data.get(
                "description", ""
            ).strip()


            # -------------------------
            # COURSE NAME
            # -------------------------

            if not course_name:

                return jsonify({
                    "error": "Course name should not be empty"
                }), 400


            # -------------------------
            # COURSE CODE
            # -------------------------

            if not course_code:

                return jsonify({
                    "error": "Course code should not be empty"
                }), 400


            # -------------------------
            # DURATION
            # -------------------------

            if not duration:

                return jsonify({
                    "error": "Duration should not be empty"
                }), 400


            # -------------------------
            # FEE
            # -------------------------

            if fee is None or fee == "":

                return jsonify({
                    "error": "Fee is required"
                }), 400

            try:

                fee = float(fee)

            except ValueError:

                return jsonify({
                    "error": "Fee must be a number"
                }), 400


            if fee < 0:

                return jsonify({
                    "error": "Fee cannot be negative"
                }), 400


            # -------------------------
            # DATABASE
            # -------------------------

            conn = get_connection()
            cursor = conn.cursor()


            # Check duplicate course code

            cursor.execute("""
                SELECT id
                FROM courses
                WHERE course_code = ?
            """, (course_code,))

            existing_course = cursor.fetchone()


            if existing_course:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Course code already exists"
                }), 400


            # -------------------------
            # INSERT
            # -------------------------

            cursor.execute("""
                INSERT INTO courses
                (
                    course_name,
                    course_code,
                    duration,
                    fee,
                    description
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                course_name,
                course_code,
                duration,
                fee,
                description
            ))


            conn.commit()

            cursor.close()
            conn.close()


            return jsonify({
                "message": "Course added successfully"
            }), 201


        except Exception as e:

            print("ADD COURSE ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ==========================================
    # UPDATE COURSE
    # ==========================================

    @app.route("/courses/<int:id>", methods=["PUT"])
    def update_course(id):

        try:

            data = request.get_json()

            if not data:

                return jsonify({
                    "error": "No data received"
                }), 400


            course_name = data.get(
                "course_name", ""
            ).strip()

            course_code = data.get(
                "course_code", ""
            ).strip()

            duration = data.get(
                "duration", ""
            ).strip()

            fee = data.get("fee")

            description = data.get(
                "description", ""
            ).strip()


            # Course name

            if not course_name:

                return jsonify({
                    "error": "Course name should not be empty"
                }), 400


            # Course code

            if not course_code:

                return jsonify({
                    "error": "Course code should not be empty"
                }), 400


            # Duration

            if not duration:

                return jsonify({
                    "error": "Duration should not be empty"
                }), 400


            # Fee

            if fee is None or fee == "":

                return jsonify({
                    "error": "Fee is required"
                }), 400


            try:

                fee = float(fee)

            except ValueError:

                return jsonify({
                    "error": "Fee must be a number"
                }), 400


            if fee < 0:

                return jsonify({
                    "error": "Fee cannot be negative"
                }), 400


            conn = get_connection()
            cursor = conn.cursor()


            # Check course exists

            cursor.execute("""
                SELECT id
                FROM courses
                WHERE id = ?
            """, (id,))

            course = cursor.fetchone()


            if not course:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Course not found"
                }), 404


            # Check duplicate course code

            cursor.execute("""
                SELECT id
                FROM courses
                WHERE course_code = ?
                AND id != ?
            """, (course_code, id))

            existing_code = cursor.fetchone()


            if existing_code:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Course code already exists"
                }), 400


            # Update

            cursor.execute("""
                UPDATE courses
                SET
                    course_name = ?,
                    course_code = ?,
                    duration = ?,
                    fee = ?,
                    description = ?
                WHERE id = ?
            """, (
                course_name,
                course_code,
                duration,
                fee,
                description,
                id
            ))


            conn.commit()

            cursor.close()
            conn.close()


            return jsonify({
                "message": "Course updated successfully"
            }), 200


        except Exception as e:

            print("UPDATE COURSE ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ==========================================
    # DELETE COURSE
    # ==========================================

    @app.route("/courses/<int:id>", methods=["DELETE"])
    def delete_course(id):

        try:

            conn = get_connection()
            cursor = conn.cursor()


            # Check course exists

            cursor.execute("""
                SELECT id
                FROM courses
                WHERE id = ?
            """, (id,))

            course = cursor.fetchone()


            if not course:

                cursor.close()
                conn.close()

                return jsonify({
                    "error": "Course not found"
                }), 404


            # Delete

            cursor.execute("""
                DELETE FROM courses
                WHERE id = ?
            """, (id,))


            conn.commit()

            cursor.close()
            conn.close()


            return jsonify({
                "message": "Course deleted successfully"
            }), 200


        except Exception as e:

            print("DELETE COURSE ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500


    # ==========================================
    # SEARCH COURSE
    # ==========================================

    @app.route("/courses/search", methods=["GET"])
    def search_courses():

        try:

            name = request.args.get(
                "name", ""
            ).strip()


            if not name:

                return jsonify({
                    "error": "Course name is required"
                }), 400


            conn = get_connection()
            cursor = conn.cursor()


            cursor.execute("""
                SELECT
                    id,
                    course_name,
                    course_code,
                    duration,
                    fee,
                    description,
                    created_at
                FROM courses
                WHERE course_name LIKE ?
                   OR course_code LIKE ?
            """, (
                "%" + name + "%",
                "%" + name + "%"
            ))


            rows = cursor.fetchall()

            courses = []


            for row in rows:

                courses.append({

                    "id": row[0],
                    "course_name": row[1],
                    "course_code": row[2],
                    "duration": row[3],
                    "fee": row[4],
                    "description": row[5],
                    "created_at": str(row[6])

                })


            cursor.close()
            conn.close()


            return jsonify(courses), 200


        except Exception as e:

            print("SEARCH COURSE ERROR:", e)

            return jsonify({
                "error": str(e)
            }), 500