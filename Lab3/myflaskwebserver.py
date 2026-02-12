from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return "<p>SYSC3010 rocks!</p>"

@app.route("/hello")
def hello():
    name = "Kezman04"
    return render_template("hello.html", name=name)

if __name__ == "__main__":
    # host=0.0.0.0 allows other devices on your network to access it
    app.run(host="0.0.0.0", port=5000, debug=True)

