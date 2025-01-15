import os
import json
import random
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Imagga API credentials
IMAGGA_API_KEY = os.getenv("IMAGGA_API_KEY")
IMAGGA_API_SECRET = os.getenv("IMAGGA_API_SECRET")
BASE_URL = "https://api.imagga.com/v2"

# Input and Output Paths
input_folder = r"C:\Users\User\OneDrive\Desktop\Wallpaper&Carpets Sdn Bhd\Datasets\Rezised Wallpapers"  # Absolute path to your dataset folder
output_file = "./results/imagga_output.json"

# Headers for Basic Authentication
auth = (IMAGGA_API_KEY, IMAGGA_API_SECRET)

# Global API Call Counter
api_call_count = 0

print("Initializing Imagga API client...")

if IMAGGA_API_KEY and IMAGGA_API_SECRET:
    print("Imagga API client initialized successfully.")
else:
    print("Error: Missing API credentials. Please check your .env file.")
    exit(1)

# Function to Select Random 100 Images
def select_images(folder_path, count=100):
    all_images = [f for f in os.listdir(folder_path) if f.endswith((".jpg", ".png"))]
    selected_images = random.sample(all_images, min(len(all_images), count))
    print(f"Selected {len(selected_images)} images for processing.")
    return selected_images

# Function to Process Images Using Imagga API
def process_images(folder_path, selected_images, output_file):
    global api_call_count
    results = []
    for idx, file_name in enumerate(selected_images, start=1):
        image_path = os.path.join(folder_path, file_name)
        print(f"Processing image {idx}/{len(selected_images)}: {file_name}")

        # Upload the image to Imagga
        try:
            with open(image_path, "rb") as image_file:
                response = requests.post(
                    f"{BASE_URL}/uploads",
                    auth=auth,
                    files={"image": image_file}
                )
                response.raise_for_status()
                upload_id = response.json()["result"]["upload_id"]
                api_call_count += 1
                print(f"Uploaded image successfully. API calls: {api_call_count}")
        except Exception as e:
            print(f"Error uploading {file_name}: {e}")
            results.append({"file_name": file_name, "error": str(e)})
            continue

        # Extract labels
        try:
            tag_response = requests.get(
                f"{BASE_URL}/tags",
                auth=auth,
                params={"image_upload_id": upload_id}
            )
            tag_response.raise_for_status()
            api_call_count += 1
            print(f"Extracted labels. API calls: {api_call_count}")
            tags = [
                {"description": tag["tag"]["en"], "confidence": tag["confidence"]}
                for tag in tag_response.json()["result"]["tags"]
            ]
        except Exception as e:
            print(f"Error tagging {file_name}: {e}")
            results.append({"file_name": file_name, "error": str(e)})
            continue

        # Extract colors
        try:
            color_response = requests.get(
                f"{BASE_URL}/colors",
                auth=auth,
                params={"image_upload_id": upload_id}
            )
            color_response.raise_for_status()
            api_call_count += 1
            print(f"Extracted colors. API calls: {api_call_count}")
            colors = color_response.json()["result"]["colors"]["image_colors"]
        except Exception as e:
            print(f"Error extracting colors for {file_name}: {e}")
            colors = []

        # Append results
        results.append({
            "file_name": file_name,
            "tags": tags,
            "colors": colors
        })

    # Save results to JSON
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    print(f"Processing complete. Results saved to {output_file}")
    print(f"Total API calls made: {api_call_count}")

# Select Random 100 Images
selected_images = select_images(input_folder, count=30)

# Process Images and Extract Metadata
process_images(input_folder, selected_images, output_file)
