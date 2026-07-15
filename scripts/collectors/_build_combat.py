import csv, json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(BASE)  # outputs/
CSV = os.path.join(OUT, "palworld_pals.csv")

# load scraped data
scraped = {}
for b in ("_raw_batch1.json","_raw_batch2.json","_raw_batch3.json"):
    with open(os.path.join(BASE,b),encoding="utf-8") as f:
        scraped.update(json.load(f))

def slugify(name):
    return name.strip().lower().replace("'","").replace(".","").replace(" ","-")

# work-column -> role tag map
WORKMAP = {
    "Kindling":"kindling", "Watering":"watering",
    "Generating_Electricity":"electricity", "Lumbering":"lumbering",
    "Mining":"mining", "Medicine":"medicine", "Cooling":"cooling",
    "Transporting":"transport", "Farming":"farming",
}
ALLWORK = ["Kindling","Watering","Planting","Generating_Electricity","Handiwork",
           "Gathering","Lumbering","Mining","Medicine","Cooling","Transporting","Farming"]

def num_or_none(v):
    return v if isinstance(v,(int,float)) else None

pals=[]
missing=[]
with open(CSV, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        name = row["Name"].strip()
        if not name:
            continue
        slug = slugify(name)
        d = scraped.get(slug)
        if d is None:
            missing.append((name,slug)); d={}

        elements=[]
        for col in ("Element_1","Element_2"):
            e=(row.get(col) or "").strip()
            if e: elements.append(e)

        # partner skill clean
        pn = d.get("pn")
        if pn in (None,"","-"): pn=None
        pe = d.get("pe") or ""
        pe = pe.split(" Contact us")[0].strip()
        if not pe: pe=None

        # mount type + reclassify swim
        ride = bool(d.get("r"))
        mt = d.get("mt")
        low = (pe or "").lower()
        if ride and ("travel on water" in low or "swim" in low):
            mt="swim"

        # role tags
        tags=[]
        if ride: tags.append("mount")
        if mt=="flying": tags.append("flyer")
        if mt=="swim": tags.append("swimmer")
        worked=False
        for col in ALLWORK:
            v=(row.get(col) or "").strip()
            if v and v!="0":
                worked=True
                if col in WORKMAP and WORKMAP[col] not in tags:
                    tags.append(WORKMAP[col])
        if worked: tags.append("base_worker")
        me=num_or_none(d.get("me")); sh=num_or_none(d.get("sh"))
        if (me and me>=120) or (sh and sh>=120): tags.append("fighter")
        if "fish" in low: tags.append("fishing")
        # order/dedupe by preferred order
        order=["mount","flyer","swimmer","fighter","base_worker","fishing","mining",
               "lumbering","farming","transport","electricity","kindling","watering",
               "cooling","medicine"]
        tags=[t for t in order if t in tags]

        pals.append({
            "name": name,
            "paldeck_number": (row.get("Number") or "").strip() or None,
            "elements": elements,
            "rarity": d.get("ra"),
            "hp": num_or_none(d.get("hp")),
            "melee_attack": me,
            "shot_attack": sh,
            "defense": num_or_none(d.get("df")),
            "support": num_or_none(d.get("su")),
            "stamina": num_or_none(d.get("st")),
            "price": num_or_none(d.get("pr")),
            "ride": ride,
            "mount_type": mt,
            "movement": {
                "walk": num_or_none(d.get("wk")),
                "run": num_or_none(d.get("rn")),
                "sprint": num_or_none(d.get("sp")),
            },
            "partner_skill": {"name": pn, "effect": pe},
            "notable_drops": d.get("dr") or [],
            "role_tags": tags,
        })

outpath=os.path.join(BASE,"pals_combat.json")
with open(outpath,"w",encoding="utf-8") as f:
    json.dump(pals,f,ensure_ascii=False,indent=2)

# validation report
n=len(pals)
def cnt(pred): return sum(1 for p in pals if pred(p))
print("count:",n)
print("missing_slug:",missing)
print("with_elements:",cnt(lambda p:len(p["elements"])>0))
print("with_hp:",cnt(lambda p:p["hp"] is not None))
print("with_shot:",cnt(lambda p:p["shot_attack"] is not None))
print("with_defense:",cnt(lambda p:p["defense"] is not None))
print("ride_true:",cnt(lambda p:p["ride"]))
print("mount_flying:",cnt(lambda p:p["mount_type"]=="flying"))
print("mount_ground:",cnt(lambda p:p["mount_type"]=="ground"))
print("mount_swim:",cnt(lambda p:p["mount_type"]=="swim"))
print("with_partner_name:",cnt(lambda p:p["partner_skill"]["name"]))
print("with_role_tags:",cnt(lambda p:len(p["role_tags"])>0))
print("with_drops:",cnt(lambda p:len(p["notable_drops"])>0))
for key in ("Jetragon","Anubis","Relaxaurus","Penking","Jormuntide","Nitewing","Neptilius","Frostallion"):
    p=next((x for x in pals if x["name"]==key),None)
    if p: print("CHK",key,"| ele",p["elements"],"| hp",p["hp"],"me",p["melee_attack"],"sh",p["shot_attack"],"df",p["defense"],"| ride",p["ride"],p["mount_type"],"| ps",p["partner_skill"]["name"],"| tags",p["role_tags"])
print("PATH:",outpath)
