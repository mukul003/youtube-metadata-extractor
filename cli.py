"""
Command-Line Interface (CLI) for YouTube Metadata Extractor & HD Thumbnail Downloader.
Usage:
    python cli.py <youtube_url> [--download-thumb] [--json] [--save-all]
"""

import sys
import os
import json
import argparse
import urllib.request

# Ensure UTF-8 output handling on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from extractor import extract_metadata, extract_video_id

def sanitize_filename(name: str) -> str:
    import re
    return re.sub(r'[\\/*?:"<>|]', '', name).strip().replace(' ', '_')[:50]

def main():
    parser = argparse.ArgumentParser(description="Extract YouTube metadata and download HD thumbnails.")
    parser.add_argument("url", help="YouTube video URL or Video ID")
    parser.add_argument("--json", action="store_true", help="Print raw JSON output")
    parser.add_argument("--download-thumb", action="store_true", help="Download HD thumbnail to current folder")
    parser.add_argument("--save-all", action="store_true", help="Save metadata JSON, text summary, and HD thumbnail")
    parser.add_argument("--output-dir", default=".", help="Directory to save downloaded files (default: .)")

    args = parser.parse_args()

    print(f"\n[*] Fetching metadata for: {args.url} ...")
    try:
        data = extract_metadata(args.url)
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)

    safe_title = sanitize_filename(data['title'])
    os.makedirs(args.output_dir, exist_ok=True)

    if args.json:
        print(json.dumps(data, indent=2))
        return

    # Formatted terminal display (cross-platform safe)
    print("\n" + "="*60)
    print(f"TITLE:          {data['title']}")
    print(f"CHANNEL:        {data['channel']} ({data['channel_url']})")
    print(f"CATEGORY:       {data['category']}")
    print(f"PUBLISHED:      {data['date_published']} ({data['date_iso']})")
    print(f"MADE FOR KIDS:  {data['made_for_kids_label']}")
    print(f"LIST NAME:      {data['list_name']}")
    print(f"LISTING STATUS: {data['listing_status']}")
    print(f"DURATION:       {data['duration_formatted']}")
    print(f"VIEWS:          {data['view_count_formatted']}")
    print(f"LIKES:          {data['like_count_formatted']}")
    print(f"HD THUMBNAIL:   {data['hd_thumbnail']}")
    print(f"TAGS ({data['tags_count']}):      {data['tags_comma']}")
    print("="*60)
    print(f"DESCRIPTION:\n{data['description'][:300]}...")
    print("="*60 + "\n")

    # Download HD Thumbnail
    if args.download_thumb or args.save_all:
        thumb_file = os.path.join(args.output_dir, f"{safe_title}_hd.jpg")
        print(f"[*] Downloading HD thumbnail to {thumb_file} ...")
        try:
            req = urllib.request.Request(
                data['hd_thumbnail'],
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as resp, open(thumb_file, 'wb') as out_file:
                out_file.write(resp.read())
            print(f"[OK] Thumbnail saved: {thumb_file}")
        except Exception as e:
            print(f"[!] Failed to download thumbnail: {e}")

    # Save JSON & Summary
    if args.save_all:
        json_file = os.path.join(args.output_dir, f"{safe_title}_metadata.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"[OK] JSON metadata saved: {json_file}")

        txt_file = os.path.join(args.output_dir, f"{safe_title}_summary.txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(data['summary_text'])
        print(f"[OK] Summary text saved: {txt_file}")

if __name__ == '__main__':
    main()
