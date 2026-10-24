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

# 100% Working, Non-Blocked Direct CDN MP4 Streams
WORKING_STREAMS = [
    "https://cdn.jsdelivr.net/gh/scqless/cdn@master/test.mp4",
    "https://vjs.zencdn.net/v/oceans.mp4",
    "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"
]

@app.get("/")
def home():
    return {"status": "active", "core": "Nexus Vault Stream Resolver Engine", "tmdb": "connected"}

@app.get("/api/media")
def get_media(category: str = Query("movies"), sub: str = Query("all")):
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
        if sub == "tamil":
            params["with_original_language"] = "ta"
        elif sub == "malayalam":
            params["with_original_language"] = "ml"
        elif sub == "telugu":
            params["with_original_language"] = "te"
        elif sub == "kannada":
            params["with_original_language"] = "kn"
        elif sub == "hindi":
            params["with_original_language"] = "hi"
        elif sub == "hollywood":
            params["with_original_language"] = "en"
            params["vote_count.gte"] = 30
    elif category == "series":
        if sub == "tamil":
            params["with_original_language"] = "ta"
        elif sub == "hindi":
            params["with_original_language"] = "hi"
        elif sub == "hollywood":
            params["with_original_language"] = "en"
    
    endpoint = f"{TMDB_BASE_URL}/discover/{media_type}"
    
    try:
        res = requests.get(endpoint, params=params, timeout=10).json()
        raw_results = res.get("results", [])
        
        for idx, item in enumerate(raw_results[:14]):
            title = item.get("title") or item.get("name") or "Unknown Title"
            poster_path = item.get("poster_path")
            img_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else "https://images.unsplash.com/photo-1568832359672-e36cf5d74f54?w=500"
            date = item.get("release_date") or item.get("first_air_date") or "2024"
            year = date[:4]
            rating = str(round(item.get("vote_average", 7.5), 1))
            
            badge_label = sub.upper() if sub not in ["all", "dubbed_hub"] else ("TAMIL DUB" if sub == "dubbed_hub" else category.upper())
            badge_bg = "bg-red-600" if "DUB" in badge_label else ("bg-amber-500 text-black" if sub == "tamil" else "bg-zinc-800")
            
            stream_url = WORKING_STREAMS[idx % len(WORKING_STREAMS)]
            
            qualities = [
                {"res": "480p SD", "size": "450 MB" if media_type == "movie" else "180 MB/ep"},
                {"res": "720p HD", "size": "850 MB" if media_type == "movie" else "380 MB/ep"},
                {"res": "1080p FHD", "size": "2.2 GB" if media_type == "movie" else "850 MB/ep"},
                {"res": "4K UHD", "size": "5.6 GB" if media_type == "movie" else "2.1 GB/ep"}
            ]

            items.append({
                "id": item.get("id", idx + 1),
                "title": title,
                "category": category,
                "subCategory": sub,
                "dubLanguage": "tamil" if sub == "dubbed_hub" else "none",
                "badge": badge_label,
                "badgeBg": badge_bg,
                "year": year,
                "rating": rating,
                "runtime": "Season 1" if media_type == "tv" else "2h 10m",
                "subs": "English, Tamil",
                "subInfo": f"{sub.capitalize() if sub != 'all' else category.capitalize()} • Trending",
                "img": img_url,
                "streamUrl": stream_url,
                "audios": [
                    {"lang": "Tamil Master" if sub in ["tamil", "dubbed_hub"] else "Original Audio", "codec": "Dolby 5.1", "type": "51"},
                    {"lang": "Dolby Atmos Track", "codec": "Dolby Atmos", "type": "atmos"}
                ],
                "qualities": qualities,
                "type": media_type,
                "seasons": 1 if media_type == "tv" else None,
                "episodes": 8 if media_type == "tv" else None
            })
    except Exception as e:
        print(f"TMDB Fetch Error: {e}")
        
    return {"results": items}

@app.get("/api/search")
def search_tmdb(query: str):
    if not query:
        return {"results": []}

    url = f"{TMDB_BASE_URL}/search/multi"
    params = {"api_key": TMDB_API_KEY, "query": query}
    try:
        res = requests.get(url, params=params, timeout=8).json()
        items = []
        for item in res.get("results", [])[:6]:
            title = item.get("title") or item.get("name")
            poster = item.get("poster_path")
            year = (item.get("release_date") or item.get("first_air_date") or "N/A")[:4]
            if title and poster:
                items.append({
                    "id": item.get("id"),
                    "title": title,
                    "year": year,
                    "img": f"{TMDB_IMAGE_BASE}{poster}",
                    "rating": round(item.get("vote_average", 0), 1)
                })
        return {"results": items}
    except Exception:
        return {"results": []}
