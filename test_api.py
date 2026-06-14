"""
test_api.py — Verify Groq key and backend health before running the app.
Usage: python test_api.py
"""
import sys, os
sys.path.insert(0, ".")

print("=" * 55)
print("   AI Career Co-Pilot — API Key Tester")
print("=" * 55)

# Step 1: Config
print("\n[1/3] Reading config.py...")
try:
    from config import GROQ_API_KEY, GROQ_MODEL, DATASET_PATH
    if "YOUR_GROQ" in GROQ_API_KEY:
        print("     ❌ GROQ_API_KEY is still a placeholder!")
        print("     → Open config.py and paste your key from https://console.groq.com")
        sys.exit(1)
    print(f"     ✅ Key found — starts with: {GROQ_API_KEY[:8]}...")
    print(f"     Model: {GROQ_MODEL}")
except Exception as e:
    print(f"     ❌ {e}")
    sys.exit(1)

# Step 2: Live Groq test
print("\n[2/3] Testing Groq API key with a live call...")
try:
    from groq import Groq
    client   = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model    = GROQ_MODEL,
        messages = [{"role":"user","content":"Reply only with: Groq is working"}],
        max_tokens = 20,
    )
    reply = response.choices[0].message.content.strip()
    print(f"     ✅ Groq replied: {reply}")
except Exception as e:
    err = str(e)
    print(f"     ❌ Error: {err}")
    if "401" in err or "invalid" in err.lower():
        print("     → API key is invalid. Create a new one at https://console.groq.com")
    elif "429" in err:
        print("     → Rate limited. Wait 60 seconds and try again.")
    elif "model" in err.lower():
        print("     → Model not found. Change GROQ_MODEL in config.py to 'llama3-8b-8192'")
    sys.exit(1)

# Step 3: Dataset
print(f"\n[3/3] Checking dataset...")
try:
    import pandas as pd
    df = pd.read_csv(DATASET_PATH)
    print(f"     ✅ {len(df)} rows loaded from {DATASET_PATH}")
except FileNotFoundError:
    print(f"     ⚠️  Dataset not found at '{DATASET_PATH}'")
    print(f"     Place your CSV in the data/ folder")

print("\n" + "=" * 55)
print("   ✅ All good! Now run:")
print("   Terminal 1: uvicorn backend.api:app --reload --port 8000")
print("   Terminal 2: streamlit run frontend/app.py")
print("=" * 55 + "\n")
