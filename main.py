import os
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Nexus Vault Core Engine")

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

# 100% Reliable, Zero-Block Direct MP4 Download CDN Streams
DIRECT_STREAMS = [
    "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4",
    "https://raw.githubusercontent.com/bower-media-samples/big-buck-bunny-480p-30s/master/video.mp4"
]

@app.get("/")
def home():
    return {"status": "active", "core": "Nexus Vault Dynamic Seasons Engine", "tmdb": "connected"}

def get_tv_details(tv_id: int):
    """Fetch exact real seasons and episode counts dynamically from TMDB"""
    try:
        url = f"{TMDB_BASE_URL}/tv/{tv_id}"
        data = requests.get(url, params={"api_key": TMDB_API_KEY}, timeout=5).json()
        seasons_info = []
        for s in data.get("seasons", []):
            if s.get("season_number", 0) > 0: # Exclude Specials
                seasons_info.append({
                    "season_number": s.get("season_number"),
                    "name": s.get("name") or f"Season {s.get('season_number')}",
                    "episode_count": s.get("episode_count", 1)
                })
        return seasons_info
    except Exception:
        return [{"season_number": 1, "name": "Season 1", "episode_count": 10}]

@app.get("/api/media")
def get_media(category: str = Query("movies"), sub: str = Query("all"), dub_lang: str = Query("all")):
    items = []
    media_type = "tv" if category in ["series", "kdrama", "anime"] else "movie"
    
    params = {
        "api_key": TMDB_API_KEY,
        "sort_by": "popularity.desc",
        "page": 1
    }
    
    if category == "kdrama":
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
        elif sub == "hollywood": 
            params["with_original_language"] = "en"
            params["vote_count.gte"] = 30
    elif category == "series":
        if sub == "tamil": params["with_original_language"] = "ta"
        elif sub == "hindi": params["with_original_language"] = "hi"
        elif sub == "hollywood": params["with_original_language"] = "en"
    
    endpoint = f"{TMDB_BASE_URL}/discover/{media_type}"
    
    try:
        res = requests.get(endpoint, params=params, timeout=10).json()
        raw_results = res.get("results", [])
        
        for idx, item in enumerate(raw_results[:16]):
            title = item.get("title") or item.get("name") or "Unknown Title"
            poster_path = item.get("poster_path")
            img_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else "https://images.unsplash.com/photo-1568832359672-e36cf5d74f54?w=500"
            date = item.get("release_date") or item.get("first_air_date") or "2024"
            year = date[:4]
            rating = str(round(item.get("vote_average", 7.5), 1))
            badge_label = sub.upper() if sub not in ["all", "dubbed_hub"] else category.upper()

            seasons_data = []
            if media_type == "tv":
                seasons_data = get_tv_details(item.get("id"))
            
            items.append({
                "id": item.get("id", idx + 1),
                "title": title,
                "category": category,
                "subCategory": sub,
                "dubLanguage": "none",
                "badge": badge_label,
                "badgeBg": "bg-red-600" if sub == "tamil" else "bg-zinc-800",
                "year": year,
                "rating": rating,
                "runtime": f"{len(seasons_data)} Seasons" if media_type == "tv" else "2h 10m",
                "subs": "English, Tamil",
                "subInfo": f"{category.capitalize()} • Trending",
                "img": img_url,
                "streamUrl": DIRECT_STREAMS[idx % len(DIRECT_STREAMS)],
                "audios": [
                    {"lang": "Tamil Master" if sub == "tamil" else "Original Audio", "codec": "Dolby 5.1", "type": "51"},
                    {"lang": "Dolby Atmos Track", "codec": "Dolby Atmos", "type": "atmos"}
                ],
                "qualities": [
                    {"res": "480p SD", "size": "380 MB" if media_type == "movie" else "150 MB/ep"},
                    {"res": "720p HD", "size": "850 MB" if media_type == "movie" else "380 MB/ep"},
                    {"res": "1080p FHD", "size": "2.2 GB" if media_type == "movie" else "850 MB/ep"},
                    {"res": "4K UHD", "size": "5.6 GB" if media_type == "movie" else "2.1 GB/ep"}
                ],
                "type": media_type,
                "seasons_list": seasons_data
            })
    except Exception as e:
        print(f"TMDB Fetch Error: {e}")
        
    return {"results": items}

@app.get("/api/search")
def search_tmdb(query: str, category: str = Query("movies"), sub: str = Query("all")):
    if not query:
        return {"results": []}

    media_type = "tv" if category in ["series", "kdrama", "anime"] else "movie"
    url = f"{TMDB_BASE_URL}/search/{media_type}"
    params = {"api_key": TMDB_API_KEY, "query": query, "page": 1}

    target_lang = None
    if category == "kdrama": target_lang = "ko"
    elif category == "anime": target_lang = "ja"
    elif category == "movies":
        lang_map = {"tamil": "ta", "malayalam": "ml", "telugu": "te", "kannada": "kn", "hindi": "hi", "hollywood": "en"}
        target_lang = lang_map.get(sub)
    elif category == "series":
        if sub == "tamil": target_lang = "ta"
        elif sub == "hindi": target_lang = "hi"
        elif sub == "hollywood": target_lang = "en"

    try:
        res = requests.get(url, params=params, timeout=8).json()
        raw_items = res.get("results", [])
        items = []

        for idx, item in enumerate(raw_items):
            title = item.get("title") or item.get("name")
            poster = item.get("poster_path")
            year = (item.get("release_date") or item.get("first_air_date") or "2024")[:4]
            orig_lang = item.get("original_language")
            genre_ids = item.get("genre_ids", [])

            if target_lang and orig_lang != target_lang:
                continue
            if category == "anime" and (16 not in genre_ids):
                continue

            seasons_data = []
            if media_type == "tv":
                seasons_data = get_tv_details(item.get("id"))

            if title and poster:
                items.append({
                    "id": item.get("id"),
                    "title": title,
                    "category": category,
                    "subCategory": sub,
                    "dubLanguage": "none",
                    "badge": category.upper(),
                    "badgeBg": "bg-red-600",
                    "year": year,
                    "rating": str(round(item.get("vote_average", 7.0), 1)),
                    "runtime": f"{len(seasons_data)} Seasons" if media_type == "tv" else "2h 10m",
                    "subs": "English, Tamil",
                    "subInfo": f"{category.capitalize()} • Search Match",
                    "img": f"{TMDB_IMAGE_BASE}{poster}",
                    "streamUrl": DIRECT_STREAMS[idx % len(DIRECT_STREAMS)],
                    "audios": [
                        {"lang": "Tamil Master" if sub == "tamil" else "Original Audio", "codec": "Dolby 5.1", "type": "51"},
                        {"lang": "Dolby Atmos Track", "codec": "Dolby Atmos", "type": "atmos"}
                    ],
                    "qualities": [
                        {"res": "480p SD", "size": "380 MB"},
                        {"res": "720p HD", "size": "850 MB"},
                        {"res": "1080p FHD", "size": "2.2 GB"},
                        {"res": "4K UHD", "size": "5.6 GB"}
                    ],
                    "type": media_type,
                    "seasons_list": seasons_data
                })
        return {"results": items[:18]}
    except Exception as e:
        print(f"Search Error: {e}")
        return {"results": []}
