"""
Flask Web Application for YouTube Metadata Extractor & HD Thumbnail Downloader.
"""

import os
import io
import re
import sys
import webbrowser
import requests
from flask import Flask, render_template, request, jsonify, send_file, Response
from extractor import extract_metadata

app = Flask(__name__)

def sanitize_filename(name: str, max_length: int = 60) -> str:
    """Create a safe filename from video title."""
    clean = re.sub(r'[\\/*?:"<>|]', '', name)
    clean = re.sub(r'\s+', '_', clean.strip())
    clean = clean.strip('._')
    if not clean:
        clean = "youtube_metadata"
    return clean[:max_length]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/metadata', methods=['POST'])
def get_metadata():
    data = request.get_json(silent=True) or {}
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'success': False, 'error': 'Please enter a valid YouTube video link or Video ID.'}), 400

    try:
        metadata = extract_metadata(url)
        return jsonify({'success': True, 'data': metadata})
    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to extract metadata: {str(e)}'}), 500

@app.route('/api/download-thumbnail', methods=['GET'])
def download_thumbnail():
    thumb_url = request.args.get('url', '').strip()
    title = request.args.get('title', 'youtube_thumbnail').strip()
    resolution = request.args.get('res', 'hd').strip()

    if not thumb_url:
        return jsonify({'error': 'Missing thumbnail URL'}), 400

    safe_name = sanitize_filename(title)
    filename = f"{safe_name}_thumbnail_{resolution}.jpg"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        resp = requests.get(thumb_url, headers=headers, timeout=15)
        if resp.status_code != 200:
            # Fallback if specific resolution (like maxresdefault) isn't available for this video
            if 'maxresdefault' in thumb_url:
                fallback_url = thumb_url.replace('maxresdefault', 'hqdefault')
                resp = requests.get(fallback_url, headers=headers, timeout=15)
            
            if resp.status_code != 200:
                return jsonify({'error': f'Could not download thumbnail (HTTP {resp.status_code})'}), 502

        content_type = resp.headers.get('Content-Type', 'image/jpeg')
        if 'webp' in content_type:
            filename = filename.replace('.jpg', '.webp')

        return send_file(
            io.BytesIO(resp.content),
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/export', methods=['POST'])
def export_file():
    data = request.get_json(silent=True) or {}
    export_format = data.get('format', 'json').lower()
    title = data.get('title', 'youtube_metadata')
    content = data.get('content', '')
    safe_name = sanitize_filename(title)

    if export_format == 'json':
        filename = f"{safe_name}_metadata.json"
        mimetype = "application/json"
    elif export_format == 'markdown' or export_format == 'md':
        filename = f"{safe_name}_metadata.md"
        mimetype = "text/markdown"
    else:
        filename = f"{safe_name}_metadata.txt"
        mimetype = "text/plain"

    return send_file(
        io.BytesIO(content.encode('utf-8')),
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename
    )

def main():
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    # Auto open browser if flag provided or by default in normal run
    if '--no-open' not in sys.argv:
        try:
            webbrowser.open(f'http://{host}:{port}')
        except Exception:
            pass
            
    print(f" * YouTube Metadata Extractor running on http://{host}:{port}")
    print(" * Press Ctrl+C to stop.")
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    main()
