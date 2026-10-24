import os
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Nexus Vault Core Engine")

# CORS enable panrom (Mini app frontend-la irundhu direct API call panna)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "YOUR_TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

@app.get("/")
def home():
    return {"status": "active", "core": "Nexus Vault Stream Resolver Engine"}

@app.get("/api/media")
def get_media(category: str = Query("movies"), sub: str = Query("all")):
    """
    Frontend request panra tab & category-ku thagundha data-va return pannum.
    """
    # Demo seed list (Idhula namma scraper functions map pannuvom)
    sample_vault = [
        {
            "id": 1,
            "title": "Deadpool & Wolverine",
            "category": "movies",
            "subCategory": "dubbed_hub",
            "dubLanguage": "tamil",
            "badge": "TAMIL DUB",
            "badgeBg": "bg-red-600",
            "year": "2024",
            "rating": "8.1",
            "runtime": "2h 08m",
            "subs": "English, Tamil",
            "subInfo": "Hollywood • Action",
            "img": "https://images.unsplash.com/photo-1568832359672-e36cf5d74f54?w=500",
            "streamUrl": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "audios": [
                {"lang": "Tamil", "codec": "Dolby 5.1", "type": "51"},
                {"lang": "English", "codec": "Dolby Atmos", "type": "atmos"}
            ],
            "qualities": [
                {"res": "720p HD", "size": "850 MB"},
                {"res": "1080p FHD", "size": "2.1 GB"},
                {"res": "4K UHD", "size": "6.8 GB"}
            ],
            "type": "movie"
        },
        {
            "id": 2,
            "title": "Baashha",
            "category": "movies",
            "subCategory": "tamil",
            "dubLanguage": "none",
            "badge": "TAMIL",
            "badgeBg": "bg-amber-500 text-black",
            "year": "1995",
            "rating": "8.6",
            "runtime": "2h 25m",
            "subs": "English",
            "subInfo": "Tamil Classic Remaster",
            "img": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=500",
            "streamUrl": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "audios": [
                {"lang": "Tamil Master", "codec": "DTS 5.1", "type": "51"},
                {"lang": "Original Track", "codec": "Stereo 2.0", "type": "stereo"}
            ],
            "qualities": [
                {"res": "720p HD", "size": "950 MB"},
                {"res": "1080p Remaster", "size": "2.4 GB"}
            ],
            "type": "movie"
        },
        {
            "id": 3,
            "title": "Squid Game S2",
            "category": "kdrama",
            "subCategory": "dubbed_hub",
            "dubLanguage": "tamil",
            "badge": "K-DRAMA",
            "badgeBg": "bg-purple-600",
            "year": "2024",
            "rating": "8.0",
            "runtime": "Season 2",
            "subs": "English, Tamil",
            "subInfo": "K-Drama • Thriller",
            "img": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500",
            "streamUrl": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "audios": [
                {"lang": "Tamil Dubbed", "codec": "Stereo 2.0", "type": "stereo"},
                {"lang": "Korean Org", "codec": "Dolby 5.1", "type": "51"}
            ],
            "qualities": [
                {"res": "720p HD", "size": "420 MB/ep"},
                {"res": "1080p FHD", "size": "1.1 GB/ep"}
            ],
            "type": "series",
            "seasons": 2,
            "episodes": 8
        },
        {
            "id": 4,
            "title": "Demon Slayer",
            "category": "anime",
            "subCategory": "dubbed_hub",
            "dubLanguage": "tamil",
            "badge": "ANIME",
            "badgeBg": "bg-emerald-600",
            "year": "2024",
            "rating": "8.8",
            "runtime": "Season 4",
            "subs": "English, Tamil",
            "subInfo": "Anime • Hashira Arc",
            "img": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500",
            "streamUrl": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "audios": [
                {"lang": "Tamil Dubbed", "codec": "Stereo 2.0", "type": "stereo"},
                {"lang": "Japanese Master", "codec": "FLAC Lossless", "type": "atmos"}
            ],
            "qualities": [
                {"res": "720p HD", "size": "260 MB/ep"},
                {"res": "1080p FHD", "size": "650 MB/ep"}
            ],
            "type": "series",
            "seasons": 4,
            "episodes": 8
        }
    ]
    return {"results": sample_vault}

@app.get("/api/search")
def search_tmdb(query: str):
    """
    Search bar suggestions-kaga TMDB live database fetcher.
    """
    if not query or TMDB_API_KEY == "YOUR_TMDB_API_KEY":
        return {"results": []}

    url = f"{TMDB_BASE_URL}/search/multi?api_key={TMDB_API_KEY}&query={query}"
    res = requests.get(url).json()
    items = []
    
    for item in res.get("results", [])[:6]:
        title = item.get("title") or item.get("name")
        poster = item.get("poster_path")
        year = (item.get("release_date") or item.get("first_air_date") or "N/A")[:4]
        if title and poster:
            items.append({
                "title": title,
                "year": year,
                "img": f"{TMDB_IMAGE_BASE}{poster}",
                "rating": round(item.get("vote_average", 0), 1)
            })
    return {"results": items}
