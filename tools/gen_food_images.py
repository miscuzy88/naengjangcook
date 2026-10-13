# 요리 사진을 AI(Pollinations)로 한 번 만들어 images/food/에 저장하는 스크립트.
# GitHub Actions에서 실행됨. 이미 있는 사진은 건너뜀 (다시 만들려면 해당 파일을 지우면 됨).
import json, os, time, urllib.parse, urllib.request, io
from PIL import Image

STYLE = ("professional food photography, appetizing, served on a simple ceramic dish, light wooden table, "
         "soft natural window light, 45 degree angle, shallow depth of field, high detail, no text, no watermark, no people")
OUT = "images/food"
os.makedirs(OUT, exist_ok=True)
items = json.load(open("tools/food_prompts.json", encoding="utf-8"))
token = os.environ.get("POLLINATIONS_TOKEN", "")
made, failed = 0, []
START = time.time()
BUDGET = 40 * 60  # 한 번 실행에 최대 40분, 나머지는 다음 실행에서 이어서
for i, it in enumerate(items):
    path = f"{OUT}/{it['slug']}.jpg"
    if os.path.exists(path):
        continue
    if time.time() - START > BUDGET:
        print("time budget reached, continue next run", flush=True)
        break
    prompt = f"{it['prompt']}, {STYLE}"
    q = {"width": 768, "height": 768, "nologo": "true", "seed": 7 + i, "model": "flux"}
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt) + "?" + urllib.parse.urlencode(q)
    ok = False
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "naengjangcook-builder"} | ({"Authorization": f"Bearer {token}"} if token else {}))
            data = urllib.request.urlopen(req, timeout=90).read()
            im = Image.open(io.BytesIO(data)).convert("RGB")
            im = im.resize((480, 480), Image.LANCZOS)
            im.save(path, "JPEG", quality=82, optimize=True, progressive=True)
            ok = True; made += 1
            print("ok", it["slug"], flush=True)
            break
        except Exception as e:
            print("retry", it["slug"], attempt, e, flush=True)
            time.sleep(20)
    if not ok:
        failed.append(it["slug"])
    time.sleep(16)  # 무료 요청 간격
print("made", made, "failed", failed)
