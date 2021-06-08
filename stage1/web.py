import os
from flask import Flask, request,render_template
# set the project root directory as the static folder, you can set others.
app = Flask(__name__, template_folder=os.getcwd())
with open("out.txt", "r") as f:
    content = f.read()
@app.route('/')
def main():
    return render_template("template.html", content=content)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
