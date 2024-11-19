from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from instagrapi import Client
import time

# FastAPI app instance
app = FastAPI()

# Instagrapi Client instance
cl = Client()

# Pydantic model for the request body (username)
class UsernameRequest(BaseModel):
    username: str

# Pydantic model for the response data (profile details)
class ProfileResponse(BaseModel):
    full_name: str
    username: str
    followers_count: int
    following_count: int
    biography: str
    email: str
    posts: list
    profile_pic_url: HttpUrl  # Use HttpUrl for URL validation
    is_verified: bool     # Added verification status
    category: str         # Added category if needed (e.g., Digital creator)

# Log in to Instagram once when the app starts
def login_once():
    try:
        cl.login("dailydoseof_art6", "imrankhan@") # gmail
        print("Logged in successfully")
    except Exception as e:
        print(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Instagram login failed")

# Call the login function at startup
login_once()

# Function to get Instagram profile data and recent posts
def get_instagram_profile_data(username: str):
    try:
        # Get user profile details
        user_info = cl.user_info_by_username(username)
        
        # Extract relevant data
        profile_data = {
            "full_name": user_info.full_name,
            "username": user_info.username,
            "followers_count": user_info.follower_count,
            "following_count": user_info.following_count,
            "biography": user_info.biography,
            "email": user_info.public_email if user_info.public_email else "Not available",
            "posts": [],
            "profile_pic_url": str(user_info.profile_pic_url),
            "is_verified": user_info.is_verified,
            "category": user_info.category if user_info.category else "Not available"
        }

        # Fetch recent posts, with delay for rate limiting
        media = cl.user_medias(user_info.pk, 2)
        for m in media:
            post_data = {
                "type": "reel" if m.media_type == 2 else "post",
                "caption": m.caption if hasattr(m, 'caption') else "No caption",
                "image_url": m.thumbnail_url if m.media_type != 2 else m.video_url,
            }
            profile_data["posts"].append(post_data)
            time.sleep(10)  # Delay to prevent rate limiting

        return profile_data

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching profile data: {e}")

# Health check route to verify if the app is running
@app.get("/")
async def read_root():
    return {"message": "FastAPI is up and running!"}

# Define a POST route to fetch Instagram profile details
@app.post("/get_instagram_profile", response_model=ProfileResponse)
async def get_instagram_profile(data: UsernameRequest):
    # Get profile data from Instagram using Instagrapi
    profile_data = get_instagram_profile_data(data.username)
    
    # Return the profile data as a response
    return profile_data

# Run the FastAPI app (use uvicorn for this)
# Run it in terminal with: uvicorn main:app --reload
