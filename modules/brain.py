import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ContentBrain:
    
    def __init__(self):
        self.history_file = "topics_history.json"
        self.history = self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"used_topics": []}

    def save_history(self, topic):
        if topic and topic not in self.history["used_topics"]:
            self.history["used_topics"].append(topic)
            if len(self.history["used_topics"]) > 200:
                self.history["used_topics"] = self.history["used_topics"][-150:]
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)

    def generate_script(self):
        print("🎬 Generating Global Did You Know Short...")

        prompt = f"""
You are an expert Ayurvedic and Health YouTube Shorts creator.

Your job is to create VIRAL, TRUSTABLE, and USEFUL health tips videos.

IMPORTANT:
- Do NOT repeat topics already used: {self.history["used_topics"]}

Create ONE short (40-55 seconds).

CONTENT RULES:
- Topic must be about ONE specific food item (fruit, vegetable, herb,
 spice or common kitchen ingredient or jungle specific plant who gives benifits to halth ) and its health benefits.
  Examples:
  - onion benefits
  - banana benefits
  - turmeric milk
  - garlic empty stomach
  - neem leaves

- Tips must be REALISTIC, SAFE and commonly known (avoid extreme medical claims)
- Include 4-6 clear benefits
- Add 1 simple usage tip (how to consume)

STYLE:
- Language: 100% English only
- Use simple, clear spoken English (like a YouTube creator)
- No Hindi or Hinglish words at all
- Tone: engaging, slightly energetic, human-like

STRUCTURE:
Hook → Benefits → Usage → Ending

VISUALS:
Return 5 visuals for better video quality

RETURN ONLY JSON:

[
  {{
    "id": 1,
    "title": "SEO friendly english title (food + benefit based)",
    "text": "Full 40-55 sec english script",
    "visual_1": "food close up cinematic",
    "visual_2": "cutting / preparation scene",
    "visual_3": "healthy lifestyle visuals",
    "visual_4": "benefit related visuals (energy, digestion etc)",
    "visual_5": "final aesthetic food shot"
  }}
]
"""

        models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3.1-flash"]

        for model_name in models:
            for attempt in range(3):
                try:
                    print(f"🔄 Trying {model_name} (Attempt {attempt+1}/3)")
                    
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config={"response_mime_type": "application/json"}
                    )

                    clean = response.text.strip().replace("```json", "").replace("```", "").strip()
                    result = json.loads(clean)

                    # Save topic for avoiding repetition
                    title = result[0].get("title", "") if isinstance(result, list) else ""
                    if title:
                        self.save_history(title)

                    print(f"✅ SUCCESS with {model_name}")
                    return result   # ← List return kar rahe hain

                except Exception as e:
                    err = str(e)
                    print(f"❌ Failed {model_name}: {err[:150]}")
                    if "503" in err or "high demand" in err:
                        time.sleep(10)
                        continue
                    else:
                        break

        print("❌ All models failed.")
        return None


if __name__ == "__main__":
    brain = ContentBrain()
    output = brain.generate_script()
    if output:
        with open("latest_script.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print("✅ latest_script.json saved")
