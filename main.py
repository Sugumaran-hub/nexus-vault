import os
import requests
from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Nexus Vault Master Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "efeb831b3735905153e997765ea5b2de")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# 100% Active, Open-Source MP4 Direct Files (Zero Google Storage / Zero AccessDenied)
DIRECT_OPEN_MP4 = [
    "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
    "https://vjs.zencdn.net/v/oceans.mp4"
]

@app.get("/")
def home():
    return {"status": "active", "core": "Nexus Vault High Speed Core"}

@app.get("/api/download")
def download_stream(id: int = Query(...), filename: str = Query("video.mp4")):
    """Direct clean download redirect avoiding browser XML cache"""
    stream_url = DIRECT_OPEN_MP4[id % len(DIRECT_OPEN_MP4)]
    return RedirectResponse(url=stream_url)

@app.get("/api/tv_details")
def tv_details(tv_id: int):
    try:
        url = f"{TMDB_BASE_URL}/tv/{tv_id}"
        data = requests.get(url, params={"api_key": TMDB_API_KEY}, timeout=4).json()
        seasons = []
        for s in data.get("seasons", []):
            if s.get("season_number", 0) > 0:
                seasons.append({
                    "season_number": s.get("season_number"),
                    "name": s.get("name") or f"Season {s.get('season_number')}",
                    "episode_count": s.get("episode_count", 1)
                })
        return {"seasons": seasons}
    except Exception:
        return {"seasons": [{"season_number": 1, "name": "Season 1", "episode_count": 10}]}

@app.get("/api/media")
def get_media(category: str = Query("movies"), sub: str = Query("all"), dub_lang: str = Query("all")):
    items = []
    media_type = "tv" if category in ["series", "kdrama", "anime"] else "movie"
    
    params = {
        "api_key": TMDB_API_KEY,
        "sort_by": "popularity.desc",
        "page": 1
    }
    
    if sub == "dubbed_hub":
        if category == "kdrama":
            params["with_original_language"] = "ko"
        elif category == "anime":
            params["with_original_language"] = "ja"
            params["with_genres"] = "16"
        elif category in ["movies", "series"]:
            params["with_original_language"] = "en"
    elif category == "kdrama":
        params["with_original_language"] = "ko"
    elif category == "anime":
        params["with_original_language"] = "ja"
        params["with_genres"] = "16"
    elif category == "movies":
        if sub == "tamil": params["with_original_language"] = "ta"
        elif sub == "malayalam": params["with_original_language"] = "ml"
        elif sub == "telugu": params["with_original_language"] = "te"
        elif sub == "kannada": params["with_original_language"] = "kn"
        elif sub == "hindi": params["with_original_language"] = "hi"
        elif sub == "hollywood": params["with_original_language"] = "en"
    elif category == "series":
        if sub == "tamil": params["with_original_language"] = "ta"
        elif sub == "hindi": params["with_original_language"] = "hi"
        elif sub == "hollywood": params["with_original_language"] = "en"
    
    endpoint = f"{TMDB_BASE_URL}/discover/{media_type}"
    
    try:
        res = requests.get(endpoint, params=params, timeout=6).json()
        raw_results = res.get("results", [])
        
        for idx, item in enumerate(raw_results[:16]):
            title = item.get("title") or item.get("name") or "Unknown Title"
            item_id = item.get("id", idx + 1)
            poster_path = item.get("poster_path")
            img_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else "https://images.unsplash.com/photo-1568832359672-e36cf5d74f54?w=500"
            date = item.get("release_date") or item.get("first_air_date") or "2024"
            year = date[:4]
            rating = str(round(item.get("vote_average", 7.5), 1))
            
            badge_label = f"{dub_lang.upper()} DUB" if sub == "dubbed_hub" and dub_lang != "all" else (sub.upper() if sub not in ["all", "dubbed_hub"] else category.upper())
            badge_bg = "bg-red-600" if "DUB" in badge_label else ("bg-amber-500 text-black" if sub == "tamil" else "bg-zinc-800")
            
            stream_url = DIRECT_OPEN_MP4[idx % len(DIRECT_OPEN_MP4)]
            
            primary_aud = f"{dub_lang.capitalize()} Dubbed" if sub == "dubbed_hub" and dub_lang != "all" else ("Tamil Master" if sub in ["tamil", "dubbed_hub"] else "Original Audio")

            audios = [
                {"lang": primary_aud, "codec": "Dolby 5.1", "type": "51"},
                {"lang": "Original Audio", "codec": "Dolby Atmos", "type": "atmos"}
            ]

            items.append({
                "id": item_id,
                "title": title,
                "category": category,
                "subCategory": sub,
                "dubLanguage": dub_lang if sub == "dubbed_hub" else "none",
                "badge": badge_label,
                "badgeBg": badge_bg,
                "year": year,
                "rating": rating,
                "runtime": "Series Master" if media_type == "tv" else "2h 10m",
                "subs": "English, Tamil",
                "subInfo": f"{sub.capitalize() if sub != 'all' else category.capitalize()} • Trending",
                "img": img_url,
                "streamUrl": stream_url,
                "audios": audios,
                "qualities": [
                    {"res": "480p SD", "size": "350 MB" if media_type == "movie" else "150 MB/ep"},
                    {"res": "720p HD", "size": "850 MB" if media_type == "movie" else "380 MB/ep"},
                    {"res": "1080p FHD", "size": "2.2 GB" if media_type == "movie" else "850 MB/ep"},
                    {"res": "4K UHD", "size": "5.6 GB" if media_type == "movie" else "2.1 GB/ep"}
                ],
                "type": media_type
            })
    except Exception as e:
        print(f"Error: {e}")
        
    return {"results": items}

@app.get("/api/search")
def search_tmdb(query: str, category: str = Query("movies"), sub: str = Query("all")):
    if not query:
        return {"results": []}

    media_type = "tv" if category in ["series", "kdrama", "anime"] else "movie"
    url = f"{TMDB_BASE_URL}/search/{media_type}"
    params = {"api_key": TMDB_API_KEY, "query": query, "page": 1}

    target_lang = None
    if sub == "dubbed_hub":
        target_lang = None
    elif category == "kdrama": target_lang = "ko"
    elif category == "anime": target_lang = "ja"
    elif category == "movies":
        lang_map = {"tamil": "ta", "malayalam": "ml", "telugu": "te", "kannada": "kn", "hindi": "hi", "hollywood": "en"}
        target_lang = lang_map.get(sub)
    elif category == "series":
        if sub == "tamil": target_lang = "ta"
        elif sub == "hindi": target_lang = "hi"
        elif sub == "hollywood": target_lang = "en"

    try:
        res = requests.get(url, params=params, timeout=6).json()
        raw_items = res.get("results", [])
        items = []

        for idx, item in enumerate(raw_items):
            title = item.get("title") or item.get("name")
            item_id = item.get("id")
            poster = item.get("poster_path")
            year = (item.get("release_date") or item.get("first_air_date") or "2024")[:4]
            orig_lang = item.get("original_language")
            genre_ids = item.get("genre_ids", [])

            if target_lang and orig_lang != target_lang:
                continue
            if category == "anime" and (16 not in genre_ids):
                continue

            badge_name = sub.upper() if sub != "all" else category.upper()
            stream_url = DIRECT_OPEN_MP4[idx % len(DIRECT_OPEN_MP4)]

            if title and poster:
                items.append({
                    "id": item_id,
                    "title": title,
                    "category": category,
                    "subCategory": sub,
                    "dubLanguage": "none",
                    "badge": badge_name,
                    "badgeBg": "bg-red-600",
                    "year": year,
                    "rating": str(round(item.get("vote_average", 7.0), 1)),
                    "runtime": "Series Master" if media_type == "tv" else "2h 10m",
                    "subs": "English, Tamil",
                    "subInfo": f"{category.capitalize()} • Match",
                    "img": f"{TMDB_IMAGE_BASE}{poster}",
                    "streamUrl": stream_url,
                    "audios": [
                        {"lang": f"{sub.capitalize()} Master" if sub != "all" else "Tamil Master", "codec": "Dolby 5.1", "type": "51"},
                        {"lang": "Original Audio", "codec": "Dolby Atmos", "type": "atmos"}
                    ],
                    "qualities": [
                        {"res": "480p SD", "size": "350 MB"},
                        {"res": "720p HD", "size": "850 MB"},
                        {"res": "1080p FHD", "size": "2.2 GB"},
                        {"res": "4K UHD", "size": "5.6 GB"}
                    ],
                    "type": media_type
                })
        return {"results": items[:18]}
    except Exception as e:
        print(f"Search Error: {e}")
        return {"results": []}
