import os, requests, json, time
from openai import OpenAI
import anthropic

# --- TUMHARI KEYS GITHUB SE AAYENGI ---
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_KEY = os.getenv("ANTHROPIC_API_KEY")
RECRAFT_KEY = os.getenv("RECRAFT_API_KEY")
PRINTIFY_KEY = os.getenv("PRINTIFY_API_KEY")
SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")
TRENDING = os.getenv("TRENDING_KEYWORD", "funny cat halloween")

# --- TUMHARA PROFIT LOGIC ---
STARTING_PRICE = 2499 # $24.99 = 2499 cents - pehle mahine $5+ profit
RUNNING_PRICE = 2999 # $29.99 = 2999 cents - baad me $10+ profit
# 30 din baad isko 2999 kar dena

CURRENT_PRICE = STARTING_PRICE # Abhi ke liye 2499

print(f"--- BUSINESS START: {TRENDING} ---")

# 1. IDEA GENERATION (OpenAI)
client_openai = OpenAI(api_key=OPENAI_KEY)
idea_res = client_openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role":"user","content": f"Give one viral Etsy t-shirt design prompt for '{TRENDING}', cute kawaii vector style, white background, no text"}]
)
design_prompt = idea_res.choices[0].message.content
print(f"Design Prompt: {design_prompt}")

# 2. TITLE / DESCRIPTION (Claude)
claude_client = anthropic.Anthropic(api_key=CLAUDE_KEY)
seo_res = claude_client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=400,
    messages=[{"role":"user","content": f"For t-shirt prompt '{design_prompt}' give ONLY JSON like: {{\"title\":\"...\",\"description\":\"...\",\"tags\":[\"13 tags\"]}}"}]
)
seo_data = json.loads(seo_res.content[0].text.replace("```json","").replace("```","").strip())
print(f"SEO: {seo_data}")

# 3. IMAGE GENERATION (Recraft)
headers_rec = {"Authorization": f"Bearer {RECRAFT_KEY}"}
img_res = requests.post("https://external.api.recraft.ai/v1/images/generations",
    headers=headers_rec,
    json={"prompt": design_prompt, "style": "vector_illustration"}
)
image_url = img_res.json()['data'][0]['url']
print(f"Image URL: {image_url}")

# 4. UPLOAD TO PRINTIFY + CREATE PRODUCT
headers_print = {"Authorization": f"Bearer {PRINTIFY_KEY}", "Content-Type": "application/json"}

# Image upload
upload = requests.post(f"https://api.printify.com/v1/uploads/images",
    headers=headers_print, json={"file_name": "design.png", "url": image_url}
).json()
image_id = upload['id']
time.sleep(10) # image ready hone ka wait

# Create Product
product_data = {
    "title": seo_data['title'][:80],
    "description": seo_data['description'],
    "blueprint_id": 5, # T-shirt
    "print_provider_id": 99, # Monster Digital - sasta
    "variants": [{"id": 40102, "price": CURRENT_PRICE, "is_enabled": True}], # L size
    "print_areas": [{"variant_ids": [40102], "placeholders": [{"position": "front", "images": [{"id": image_id, "x": 0.5, "y": 0.5, "scale": 0.8, "angle": 0}]}]}]
}
create = requests.post(f"https://api.printify.com/v1/shops/{SHOP_ID}/products",
    headers=headers_print, json=product_data
)
print(f"Printify Response: {create.text}")
print(f"--- DONE! Profit will be $5-$10 per sale ---")
