import os
from flask import Flask, render_template, request, send_file, redirect, url_for
from moviepy.editor import VideoFileClip
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(video_path)
        return redirect(url_for('convert', filename=file.filename))

@app.route('/convert/<filename>', methods=['GET', 'POST'])
def convert(filename):
    if request.method == 'POST':
        screenshot_interval = float(request.form['interval'])
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_pdf = os.path.join(app.config['OUTPUT_FOLDER'], f"screenshots_{filename.split('.')[0]}.pdf")

        try:
            video = VideoFileClip(video_path)
            duration = video.duration
        except Exception as e:
            return f"Failed to load video: {str(e)}"

        width, height = letter
        c = canvas.Canvas(output_pdf, pagesize=letter)

        for t in range(0, int(duration), int(screenshot_interval)):
            try:
                frame = video.get_frame(t)
            except Exception as e:
                return f"Failed to extract frame at {t} seconds: {str(e)}"

            temp_image_path = os.path.join(app.config['OUTPUT_FOLDER'], f"screenshot_{t}.png")
            Image.fromarray(frame).save(temp_image_path)

            image = Image.open(temp_image_path)
            image_width, image_height = image.size
            aspect_ratio = image_width / image_height

            if aspect_ratio > 1:
                pdf_image_width = width
                pdf_image_height = width / aspect_ratio
            else:
                pdf_image_height = height
                pdf_image_width = height * aspect_ratio

            x_offset = (width - pdf_image_width) / 2
            y_offset = (height - pdf_image_height) / 2

            c.drawInlineImage(temp_image_path, x_offset, y_offset, pdf_image_width, pdf_image_height)
            c.showPage()

            os.remove(temp_image_path)

        c.save()
        return send_file(output_pdf, as_attachment=True)

    return render_template('convert.html', filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
