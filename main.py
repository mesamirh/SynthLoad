from flask import Flask, request, render_template, send_file
import os
import yt_dlp as youtube_dl
from yt_dlp.utils import DownloadError

app = Flask(__name__)

DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "WebAppDownloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formats', methods=['POST'])
def formats():
    url = request.form['url']
    formats, title, thumbnail = get_formats(url)
    if formats:
        return render_template('formats.html', url=url, formats=formats, title=title, thumbnail=thumbnail)
    else:
        return "No formats available or unsupported URL", 400

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_id = request.form['format']
    file_path = download_video(url, format_id)
    if file_path:
        return send_file(file_path, as_attachment=True)
    else:
        return "Error downloading video", 500

@app.route('/download_high_res', methods=['POST'])
def download_high_res():
    url = request.form['url']
    file_path = download_video(url, 'bestvideo+bestaudio')
    if file_path:
        return send_file(file_path, as_attachment=True)
    else:
        return "Error downloading high-resolution video", 500

@app.route('/download_mp3', methods=['POST'])
def download_mp3():
    url = request.form['url']
    file_path = download_video(url, 'bestaudio')
    if file_path:
        return send_file(file_path, as_attachment=True)
    else:
        return "Error downloading audio", 500

def get_formats(url):
    ydl_opts = {'listformats': True}
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            title = info.get('title', 'Unknown Title')
            thumbnail = info.get('thumbnail', '')
            return formats, title, thumbnail
    except DownloadError as e:
        print(f"Error extracting formats: {e}")
        return None, None, None

def download_video(url, format_id):
    ydl_opts = {
        'format': format_id,
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            file_path = ydl.prepare_filename(info)
        return file_path
    except DownloadError as e:
        print(f"Error downloading video: {e}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
