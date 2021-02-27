from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Menampilkan file html index, dan mengirim data title
    return render_template('index.html', title="100% QUALITY CUSTOM CASES")

if __name__ == '__main__':
    app.run()
