import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('irrigation_dealers_map_2.html', 'r', encoding='utf-8') as f:
    html = f.read()

def extract_array(html, key):
    m = re.search(key + r'\s*:\s*\[', html)
    if not m: return []
    start = m.end() - 1
    depth, in_str, esc = 0, False, False
    for i in range(start, len(html)):
        c = html[i]
        if esc: esc = False; continue
        if c == '\\' and in_str: esc = True; continue
        if c == '"': in_str = not in_str; continue
        if in_str: continue
        if c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return json.loads(html[start:i+1])
    return []

for brand in ['valley', 'zimmatic', 'reinke']:
    arr = extract_array(html, brand)
    zeros = [d for d in arr if d.get('lat', 0) == 0]
    print(f"{brand}: {len(arr)} dealers, {len(zeros)} zero-lat")
    for d in arr[-3:]:
        print(f"  {d['name']} | {d['city']}, {d['state']} | {d['lat']},{d['lng']}")
