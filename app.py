from flask import Flask, render_template
from course import course_routes
from marks import marks_routes
from student import student_routes
from enrollment import enrollment_routes

app = Flask(__name__)

student_routes(app)
course_routes(app)
enrollment_routes(app)
marks_routes(app)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)