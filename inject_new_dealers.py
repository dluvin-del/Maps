import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('new_dealers_geocoded.json', 'r', encoding='utf-8') as f:
    new_dealers = json.load(f)

# Fix FARM-TECH Adams MN — geocoder returned Ohio coords
for d in new_dealers.get('reinke', []):
    if 'FARM-TECH' in d['name'] and 'Adams' in d['city'] and d['state'] == 'Minnesota':
        d['lat'] = 43.7944
        d['lng'] = -92.7238
        print(f"Fixed coords for {d['name']}")

# Remove any lat=0 entries
for brand in new_dealers:
    before = len(new_dealers[brand])
    new_dealers[brand] = [d for d in new_dealers[brand] if d['lat'] != 0]
    if before != len(new_dealers[brand]):
        print(f"Removed {before - len(new_dealers[brand])} zero-coord entries from {brand}")

print("New dealers to add:")
for brand, dealers in new_dealers.items():
    print(f"  {brand}: {len(dealers)}")

# Load HTML and extract existing arrays
with open('irrigation_dealers_map_2.html', 'r', encoding='utf-8') as f:
    html = f.read()

def extract_json_array(html, key):
    pattern = key + r'\s*:\s*\['
    m = re.search(pattern, html)
    if not m:
        return [], 0, 0
    start = m.end() - 1
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(html)):
        c = html[i]
        if escape:
            escape = False
            continue
        if c == '\\' and in_string:
            escape = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return json.loads(html[start:i+1]), start, i+1
    return [], 0, 0

# Process each brand
html_new = html
offset = 0

for brand in ['valley', 'zimmatic', 'reinke']:
    additions = new_dealers.get(brand, [])
    if not additions:
        continue

    existing_arr, arr_start, arr_end = extract_json_array(html_new, brand)
    combined = existing_arr + additions
    new_json = json.dumps(combined, separators=(',', ':'))

    html_new = html_new[:arr_start] + new_json + html_new[arr_end:]
    print(f"{brand}: {len(existing_arr)} + {len(additions)} = {len(combined)} dealers")

# Update stat pills
valley_count = len(extract_json_array(html_new, 'valley')[0])
zimmatic_count = len(extract_json_array(html_new, 'zimmatic')[0])
reinke_count = len(extract_json_array(html_new, 'reinke')[0])

html_new = re.sub(r'Valley: \d+', f'Valley: {valley_count}', html_new)
html_new = re.sub(r'Zimmatic: \d+', f'Zimmatic: {zimmatic_count}', html_new)
html_new = re.sub(r'Reinke: \d+', f'Reinke: {reinke_count}', html_new)

with open('irrigation_dealers_map_2.html', 'w', encoding='utf-8') as f:
    f.write(html_new)

print(f"\nStat pills updated: Valley {valley_count} | Zimmatic {zimmatic_count} | Reinke {reinke_count}")
print(f"File size: {len(html_new):,} bytes")
