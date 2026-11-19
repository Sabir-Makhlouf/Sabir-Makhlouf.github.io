import json
import math
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# All 58 Algerian Wilayas (code, Arabic, English, French, center lat, center lng)
WILAYAS = [
    ("01", "أدرار", "Adrar", "Adrar", 27.8742, -0.2939),
    ("02", "الشلف", "Chlef", "Chlef", 36.1652, 1.3345),
    ("03", "الأغواط", "Laghouat", "Laghouat", 33.8000, 2.8651),
    ("04", "أم البواقي", "Oum El Bouaghi", "Oum El Bouaghi", 35.8754, 7.1135),
    ("05", "باتنة", "Batna", "Batna", 35.5559, 6.1741),
    ("06", "بجاية", "Bejaia", "Béjaïa", 36.7509, 5.0567),
    ("07", "بسكرة", "Biskra", "Biskra", 34.8504, 5.7280),
    ("08", "بشار", "Bechar", "Béchar", 31.6167, -2.2167),
    ("09", "البليدة", "Blida", "Blida", 36.4700, 2.8277),
    ("10", "البويرة", "Bouira", "Bouira", 36.3749, 3.9020),
    ("11", "تمنراست", "Tamanrasset", "Tamanrasset", 22.7850, 5.5228),
    ("12", "تبسة", "Tebessa", "Tébessa", 35.4042, 8.1242),
    ("13", "تلمسان", "Tlemcen", "Tlemcen", 34.8783, -1.3150),
    ("14", "تيارت", "Tiaret", "Tiaret", 35.3710, 1.3170),
    ("15", "تيزي وزو", "Tizi Ouzou", "Tizi Ouzou", 36.7118, 4.0459),
    ("16", "الجزائر", "Algiers", "Alger", 36.7538, 3.0588),
    ("17", "الجلفة", "Djelfa", "Djelfa", 34.6728, 3.2630),
    ("18", "جيجل", "Jijel", "Jijel", 36.8205, 5.7667),
    ("19", "سطيف", "Setif", "Sétif", 36.1905, 5.4106),
    ("20", "سعيدة", "Saida", "Saïda", 34.8303, 0.1517),
    ("21", "سكيكدة", "Skikda", "Skikda", 36.8762, 6.9092),
    ("22", "سيدي بلعباس", "Sidi Bel Abbes", "Sidi Bel Abbès", 35.1899, -0.6308),
    ("23", "عنابة", "Annaba", "Annaba", 36.9000, 7.7667),
    ("24", "قالمة", "Guelma", "Guelma", 36.4621, 7.4261),
    ("25", "قسنطينة", "Constantine", "Constantine", 36.3650, 6.6147),
    ("26", "المدية", "Medea", "Médéa", 36.2642, 2.7539),
    ("27", "مستغانم", "Mostaganem", "Mostaganem", 35.9311, 0.0892),
    ("28", "المسيلة", "M'Sila", "M'Sila", 35.7058, 4.5419),
    ("29", "معسكر", "Mascara", "Mascara", 35.3966, 0.1403),
    ("30", "ورقلة", "Ouargla", "Ouargla", 31.9493, 5.3250),
    ("31", "وهران", "Oran", "Oran", 35.6969, -0.6331),
    ("32", "البيض", "El Bayadh", "El Bayadh", 33.6832, 1.0193),
    ("33", "إليزي", "Illizi", "Illizi", 26.4833, 8.4667),
    ("34", "برج بوعريريج", "Bordj Bou Arreridj", "Bordj Bou Arréridj", 36.0732, 4.7611),
    ("35", "بومرداس", "Boumerdes", "Boumerdès", 36.7664, 3.4772),
    ("36", "الطارف", "El Tarf", "El Tarf", 36.7672, 8.3138),
    ("37", "تندوف", "Tindouf", "Tindouf", 27.6711, -8.1474),
    ("38", "تيسمسيلت", "Tissemsilt", "Tissemsilt", 35.6072, 1.8108),
    ("39", "الوادي", "El Oued", "El Oued", 33.3683, 6.8674),
    ("40", "خنشلة", "Khenchela", "Khenchela", 35.4358, 7.1433),
    ("41", "سوق أهراس", "Souk Ahras", "Souk Ahras", 36.2864, 7.9511),
    ("42", "تيبازة", "Tipaza", "Tipaza", 36.5897, 2.4475),
    ("43", "ميلة", "Mila", "Mila", 36.4503, 6.2644),
    ("44", "عين الدفلى", "Ain Defla", "Aïn Defla", 36.2640, 1.9679),
    ("45", "النعامة", "Naama", "Naâma", 33.2667, -0.3167),
    ("46", "عين تموشنت", "Ain Temouchent", "Aïn Témouchent", 35.2975, -1.1404),
    ("47", "غرداية", "Ghardaia", "Ghardaïa", 32.4909, 3.6735),
    ("48", "غليزان", "Relizane", "Relizane", 35.7373, 0.5560),
    ("49", "تيميمون", "Timimoun", "Timimoun", 29.2639, 0.2310),
    ("50", "برج باجي مختار", "Bordj Badji Mokhtar", "Bordj Badji Mokhtar", 21.3278, 0.9556),
    ("51", "أولاد جلال", "Ouled Djellal", "Ouled Djellal", 34.4167, 5.0667),
    ("52", "بني عباس", "Beni Abbes", "Béni Abbès", 30.1322, -2.1670),
    ("53", "عين صالح", "In Salah", "In Salah", 27.1935, 2.4607),
    ("54", "عين قزام", "In Guezzam", "In Guezzam", 19.5686, 5.7694),
    ("55", "تقرت", "Touggourt", "Touggourt", 33.1053, 6.0580),
    ("56", "جانت", "Djanet", "Djanet", 24.5542, 9.4840),
    ("57", "المغير", "El M'Ghair", "El M'Ghair", 33.9506, 5.9242),
    ("58", "المنيعة", "El Meniaa", "El Meniaa", 30.5833, 2.8833),
]

QUERY = """
[out:json][timeout:180];
area["ISO3166-1"="DZ"][admin_level=2]->.dz;
(
  node["amenity"~"^(restaurant|fast_food|cafe|ice_cream|food_court)$"](area.dz);
  way["amenity"~"^(restaurant|fast_food|cafe|ice_cream|food_court)$"](area.dz);
);
out center tags;
"""


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def nearest_wilaya(lat, lng):
    best_code = "16"
    best_dist = float("inf")
    for code, _, _, _, wlat, wlng in WILAYAS:
        d = haversine_km(lat, lng, wlat, wlng)
        if d < best_dist:
            best_dist = d
            best_code = code
    return best_code


def fetch_overpass():
    encoded = urllib.parse.urlencode({"data": QUERY}).encode("utf-8")
    for mirror in OVERPASS_MIRRORS:
        for attempt in range(2):
            try:
                req = urllib.request.Request(
                    mirror,
                    data=encoded,
                    headers={"User-Agent": "DZRestoGuideUpdater/1.0 (TechScienceLab)"},
                )
                with urllib.request.urlopen(req, timeout=200) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                print(f"Mirror {mirror} attempt {attempt + 1} failed: {e}")
                time.sleep(10)
    raise RuntimeError("All Overpass mirrors failed.")


def main():
    raw = fetch_overpass()
    elements = raw.get("elements", [])
    by_wilaya = {w[0]: [] for w in WILAYAS}

    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:ar") or tags.get("name:fr") or tags.get("name:en")
        if not name:
            continue

        lat = el.get("lat") or el.get("center", {}).get("lat")
        lng = el.get("lon") or el.get("center", {}).get("lon")
        if lat is None or lng is None:
            continue

        code = nearest_wilaya(lat, lng)
        item = {
            "osmId": f"{el.get('type', 'n')}_{el.get('id')}",
            "name": name,
            "nameAr": tags.get("name:ar", ""),
            "nameFr": tags.get("name:fr", ""),
            "nameEn": tags.get("name:en", ""),
            "category": tags.get("amenity", "restaurant"),
            "cuisine": tags.get("cuisine", ""),
            "wilayaCode": code,
            "city": tags.get("addr:city", ""),
            "address": tags.get("addr:full") or tags.get("addr:street", ""),
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "phone": tags.get("phone") or tags.get("contact:phone", ""),
            "openingHours": tags.get("opening_hours", ""),
            "website": tags.get("website") or tags.get("contact:website", ""),
            "facebook": tags.get("contact:facebook", ""),
            "instagram": tags.get("contact:instagram", ""),
            "delivery": tags.get("delivery") == "yes",
            "takeaway": tags.get("takeaway") == "yes",
            "outdoorSeating": tags.get("outdoor_seating") == "yes",
            "wheelchair": tags.get("wheelchair") == "yes",
            "wifi": tags.get("internet_access") in ("wlan", "yes"),
        }
        by_wilaya[code].append(item)

    os.makedirs("data/wilayas", exist_ok=True)
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    index_summary = []

    for code, name_ar, name_en, name_fr, _, _ in WILAYAS:
        items = sorted(by_wilaya[code], key=lambda x: x["name"].lower())
        payload = {
            "wilayaCode": code,
            "updatedAt": updated_at,
            "count": len(items),
            "restaurants": items,
        }
        with open(f"data/wilayas/{code}.json", "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        index_summary.append({
            "code": code,
            "nameAr": name_ar,
            "nameEn": name_en,
            "nameFr": name_fr,
            "count": len(items),
        })

    with open("data/wilayas/index.json", "w", encoding="utf-8") as f:
        json.dump(
            {"updatedAt": updated_at, "total": sum(x["count"] for x in index_summary), "wilayas": index_summary},
            f,
            ensure_ascii=False,
            separators=(",", ":"),
        )
    print(f"Done! Saved {sum(x['count'] for x in index_summary)} places across 58 wilayas.")


if __name__ == "__main__":
    main()
