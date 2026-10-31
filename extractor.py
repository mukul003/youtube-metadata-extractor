"""
YouTube Metadata Extractor Module
Handles extracting comprehensive video metadata and thumbnails using yt-dlp
with multi-stage mobile client fallback and direct YouTube page parsing.
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests
import yt_dlp

def extract_video_id(url_or_id: str) -> Optional[str]:
    """Extract 11-character YouTube video ID from various URL formats or raw ID."""
    if not url_or_id:
        return None
    url_or_id = url_or_id.strip()
    
    # Raw 11-char ID
    if re.fullmatch(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
        
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/live\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?m\.youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return None

def format_number(val: Optional[int]) -> str:
    if val is None:
        return "N/A"
    try:
        val = int(val)
        return f"{val:,}"
    except (ValueError, TypeError):
        return str(val)

def format_date(date_str: Optional[str]) -> Dict[str, str]:
    """Parse YYYYMMDD or ISO format into human-readable date formats."""
    if not date_str:
        return {"raw": "N/A", "formatted": "N/A", "iso": "N/A"}
    
    date_str = str(date_str).strip()
    
    # Handle YYYYMMDD
    if len(date_str) == 8 and date_str.isdigit():
        try:
            dt = datetime.strptime(date_str, "%Y%m%d")
            return {
                "raw": date_str,
                "formatted": dt.strftime("%B %d, %Y"),
                "iso": dt.strftime("%Y-%m-%d")
            }
        except Exception:
            pass

    # Handle ISO YYYY-MM-DD
    if "-" in date_str:
        try:
            clean_date = date_str[:10]
            dt = datetime.strptime(clean_date, "%Y-%m-%d")
            return {
                "raw": date_str,
                "formatted": dt.strftime("%B %d, %Y"),
                "iso": dt.strftime("%Y-%m-%d")
            }
        except Exception:
            pass

    return {"raw": date_str, "formatted": date_str, "iso": date_str}

def format_duration(seconds: Optional[int]) -> str:
    if seconds is None:
        return "N/A"
    try:
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
    except (ValueError, TypeError):
        return str(seconds)

def get_best_thumbnails(raw_thumbnails: List[Dict[str, Any]], video_id: str) -> Dict[str, Any]:
    """
    Analyze thumbnail list and return categorized resolutions:
    - best_hd: highest quality (1080p, 720p, or maxresdefault)
    - variants: list of all distinct available thumbnails with dimension labels
    """
    valid_thumbs = []
    for t in raw_thumbnails:
        url = t.get('url', '')
        if not url:
            continue
        width = t.get('width') or 0
        height = t.get('height') or 0
        res = t.get('resolution') or (f"{width}x{height}" if width and height else None)
        valid_thumbs.append({
            'url': url,
            'width': width,
            'height': height,
            'resolution': res or 'Auto',
            'id': t.get('id', '')
        })

    # Sort yt-dlp thumbs by width * height descending
    valid_thumbs.sort(key=lambda x: (x['width'] or 0) * (x['height'] or 0), reverse=True)
    
    best_hd_url = None
    if valid_thumbs and (valid_thumbs[0]['width'] >= 1280 or 'maxresdefault' in valid_thumbs[0]['url']):
        best_hd_url = valid_thumbs[0]['url']
    else:
        best_hd_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"

    variants = [
        {
            'label': 'Max HD (1080p / 720p)',
            'width': 1920,
            'height': 1080,
            'url': f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
            'badge': '1080p Full HD'
        },
        {
            'label': 'High Quality (720p)',
            'width': 1280,
            'height': 720,
            'url': f"https://i.ytimg.com/vi/{video_id}/hq720.jpg",
            'badge': '720p HD'
        },
        {
            'label': 'Standard (480p)',
            'width': 640,
            'height': 480,
            'url': f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg",
            'badge': '480p SD'
        },
        {
            'label': 'High (360p)',
            'width': 480,
            'height': 360,
            'url': f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            'badge': '360p'
        },
        {
            'label': 'Medium (180p)',
            'width': 320,
            'height': 180,
            'url': f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg",
            'badge': '180p'
        }
    ]

    return {
        'best_hd': best_hd_url,
        'variants': variants,
        'raw_count': len(raw_thumbnails)
    }

def scrape_youtube_page_fallback(video_id: str) -> Dict[str, Any]:
    """
    Resilient fallback extraction using YouTube watch page parsing + oEmbed API.
    Used if yt-dlp hits any unexpected network or client restriction.
    """
    canonical_url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    # Fetch watch page HTML
    resp = requests.get(canonical_url, headers=headers, timeout=12)
    html = resp.text

    title = "YouTube Video"
    description = ""
    tags = []
    category = "General"
    upload_date = ""
    channel_name = "YouTube Channel"
    channel_url = f"https://www.youtube.com/watch?v={video_id}"
    view_count = None
    duration_secs = None

    # Parse ytInitialPlayerResponse JSON
    match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});(?:var\s|<)', html)
    if not match:
        match = re.search(r'var ytInitialPlayerResponse\s*=\s*({.+?});', html)

    if match:
        try:
            player_data = json.loads(match.group(1))
            details = player_data.get('videoDetails', {})
            microformat = player_data.get('microformat', {}).get('playerMicroformatRenderer', {})

            title = details.get('title') or title
            description = details.get('shortDescription') or description
            tags = details.get('keywords') or []
            category = microformat.get('category') or category
            upload_date = microformat.get('uploadDate') or microformat.get('publishDate') or ""
            channel_name = details.get('author') or channel_name
            channel_id = details.get('channelId')
            if channel_id:
                channel_url = f"https://www.youtube.com/channel/{channel_id}"
            view_count = details.get('viewCount')
            duration_secs = details.get('lengthSeconds')
        except Exception:
            pass

    # If title still empty, check oEmbed
    if not title or title == "YouTube Video":
        try:
            oembed_resp = requests.get(f"https://www.youtube.com/oembed?url={canonical_url}&format=json", timeout=8)
            if oembed_resp.status_code == 200:
                oe = oembed_resp.json()
                title = oe.get('title') or title
                channel_name = oe.get('author_name') or channel_name
                channel_url = oe.get('author_url') or channel_url
        except Exception:
            pass

    return {
        'title': title,
        'description': description,
        'tags': tags,
        'categories': [category],
        'upload_date': upload_date,
        'channel': channel_name,
        'channel_url': channel_url,
        'view_count': int(view_count) if view_count and str(view_count).isdigit() else None,
        'duration': int(duration_secs) if duration_secs and str(duration_secs).isdigit() else None,
        'like_count': None,
        'comment_count': None,
        'thumbnails': []
    }

def extract_metadata(input_url_or_id: str) -> Dict[str, Any]:
    """
    Main extraction function.
    Extracts complete video metadata and HD thumbnails using yt-dlp with automatic fallbacks.
    """
    video_id = extract_video_id(input_url_or_id)
    if not video_id:
        raise ValueError("Invalid YouTube video URL or ID. Please provide a valid YouTube link.")

    canonical_url = f"https://www.youtube.com/watch?v={video_id}"
    info = None

    # Extraction Strategy 1: yt-dlp with mobile client priority + ignore_no_formats_error
    ydl_opts_1 = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'noplaylist': True,
        'extract_flat': False,
        'ignore_no_formats_error': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts_1) as ydl:
            info = ydl.extract_info(canonical_url, download=False)
    except Exception as e1:
        # Extraction Strategy 2: yt-dlp with dedicated android client
        try:
            ydl_opts_2 = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'noplaylist': True,
                'ignore_no_formats_error': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android']
                    }
                }
            }
            with yt_dlp.YoutubeDL(ydl_opts_2) as ydl:
                info = ydl.extract_info(canonical_url, download=False)
        except Exception as e2:
            # Extraction Strategy 3: Direct Web Scraping Fallback
            try:
                info = scrape_youtube_page_fallback(video_id)
            except Exception as e3:
                raise RuntimeError(f"Could not retrieve video information. Please ensure the link is correct. ({str(e1)})")

    if not info:
        raise RuntimeError("No metadata could be extracted for this video.")

    # Extract required fields
    title = info.get('title') or 'Untitled Video'
    description = info.get('description') or ''
    tags = info.get('tags') or []
    if isinstance(tags, str):
        tags = [tags]
    
    # Categories
    raw_cats = info.get('categories') or []
    if isinstance(raw_cats, str):
        categories = [raw_cats]
    else:
        categories = list(raw_cats)
    primary_category = categories[0] if categories else 'General'

    # Date published
    upload_date = info.get('upload_date')
    dates = format_date(upload_date)

    # Channel & Stats
    channel_name = info.get('channel') or info.get('uploader') or 'Unknown Channel'
    channel_url = info.get('channel_url') or info.get('uploader_url') or f"https://www.youtube.com/watch?v={video_id}"
    channel_id = info.get('channel_id') or ''
    channel_follower_count = info.get('channel_follower_count')
    
    view_count = info.get('view_count')
    like_count = info.get('like_count')
    comment_count = info.get('comment_count')
    duration_secs = info.get('duration')
    duration_formatted = format_duration(duration_secs)

    # Thumbnails
    thumb_data = get_best_thumbnails(info.get('thumbnails', []), video_id)

    # Formatted tags versions
    tags_comma = ", ".join(tags) if tags else ""
    tags_hashtag = " ".join([f"#{re.sub(r'[^a-zA-Z0-9_]', '', t)}" for t in tags if t]) if tags else ""
    tags_lines = "\n".join(tags) if tags else ""

    # Formatted full summary (plain text)
    summary_lines = [
        f"Title: {title}",
        f"Video URL: {canonical_url}",
        f"Video ID: {video_id}",
        f"Channel: {channel_name} ({channel_url})",
        f"Category: {primary_category}",
        f"Date Published: {dates['formatted']} ({dates['iso']})",
        f"Duration: {duration_formatted}",
        f"Views: {format_number(view_count)}",
        f"Likes: {format_number(like_count)}",
        f"HD Thumbnail: {thumb_data['best_hd']}",
        "",
        f"Tags ({len(tags)}):",
        tags_comma if tags_comma else "None",
        "",
        "Description:",
        "-" * 40,
        description,
        "-" * 40
    ]
    summary_text = "\n".join(summary_lines)

    # Formatted Markdown
    summary_markdown = f"""# {title}

- **Video URL:** [{canonical_url}]({canonical_url})
- **Channel:** [{channel_name}]({channel_url})
- **Category:** `{primary_category}`
- **Published:** {dates['formatted']} (`{dates['iso']}`)
- **Duration:** {duration_formatted}
- **Views:** {format_number(view_count)} | **Likes:** {format_number(like_count)}
- **HD Thumbnail:** [View / Download]({thumb_data['best_hd']})

---

### Tags ({len(tags)})
{', '.join([f'`{t}`' for t in tags]) if tags else '_No tags_'}

---

### Description
```text
{description}
```
"""

    return {
        'id': video_id,
        'url': canonical_url,
        'title': title,
        'description': description,
        'tags': tags,
        'tags_count': len(tags),
        'tags_comma': tags_comma,
        'tags_hashtag': tags_hashtag,
        'tags_lines': tags_lines,
        'category': primary_category,
        'categories': categories,
        'date_published': dates['formatted'],
        'date_iso': dates['iso'],
        'date_raw': dates['raw'],
        'channel': channel_name,
        'channel_url': channel_url,
        'channel_id': channel_id,
        'channel_subscribers': format_number(channel_follower_count) if channel_follower_count else None,
        'duration_seconds': duration_secs,
        'duration_formatted': duration_formatted,
        'view_count': view_count,
        'view_count_formatted': format_number(view_count),
        'like_count': like_count,
        'like_count_formatted': format_number(like_count),
        'comment_count': comment_count,
        'comment_count_formatted': format_number(comment_count),
        'hd_thumbnail': thumb_data['best_hd'],
        'thumbnail_variants': thumb_data['variants'],
        'summary_text': summary_text,
        'summary_markdown': summary_markdown
    }
