"""
ShopSphere seed script — run inside the product-service container:
  docker exec -it shopsphere-product-service-1 python3 //app/seed.py
"""
import json, os, uuid
from datetime import datetime, timezone, timedelta
from database import SessionLocal, engine
from models import Base, Category, Product
from elasticsearch import Elasticsearch

es = Elasticsearch(os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200"))
ES_INDEX = "products"

Base.metadata.create_all(engine)
db = SessionLocal()

# ── 1. Get or create the admin/seed vendor ID ─────────────────────────────────
# Uses a fixed UUID so re-runs are idempotent
SEED_VENDOR_ID = "00000000-0000-0000-0000-000000000001"

# ── 2. Categories ─────────────────────────────────────────────────────────────
CATEGORIES = [
    ("Electronics",  None),
    ("Mobiles",      "Electronics"),
    ("Laptops",      "Electronics"),
    ("Accessories",  "Electronics"),
    ("Fashion",      None),
    ("Men",          "Fashion"),
    ("Women",        "Fashion"),
    ("Home",         None),
    ("Kitchen",      "Home"),
    ("Furniture",    "Home"),
    ("Sports",       None),
    ("Beauty",       None),
    ("Books",        None),
]

cat_map = {}   # name → id
parent_map = {}

# First pass — top-level
for name, parent in CATEGORIES:
    existing = db.query(Category).filter(Category.name == name).first()
    if existing:
        cat_map[name] = existing.id
    else:
        c = Category(id=str(uuid.uuid4()), name=name, parent_id=None)
        db.add(c)
        db.flush()
        cat_map[name] = c.id
    parent_map[name] = parent

# Second pass — set parent IDs
for name, parent in CATEGORIES:
    if parent:
        c = db.query(Category).filter(Category.name == name).first()
        if c:
            c.parent_id = cat_map.get(parent)

db.commit()
print(f"[seed] Categories ready: {len(cat_map)}")

# ── 3. Products ───────────────────────────────────────────────────────────────
PRODUCTS = [
    # Laptops
    ("NexGen Lightweight Laptop 13\"",    "Ultra-thin 13-inch laptop with 12-hour battery, perfect for students and professionals.", 45999,  "Laptops", 25),
    ("TrueCore Pro Laptop 15\"",           "High-performance 15-inch laptop with dedicated GPU and 16GB RAM.",                        89999,  "Laptops", 15),
    ("EcoBliss Premium Laptop 14\"",       "Eco-friendly laptop made from recycled materials with full-day battery life.",            54999,  "Laptops", 18),
    ("SwiftBook Air Ultra",                "Featherlight laptop at just 900g, designed for travel.",                                  72999,  "Laptops", 10),
    ("ProMax Gaming Laptop",               "144Hz display, RTX 4060, 32GB RAM — dominate every game.",                               129999, "Laptops", 8),
    ("BudgetBook 11\" Student Laptop",     "Affordable 11-inch laptop ideal for schoolwork and browsing.",                           18999,  "Laptops", 40),

    # Mobiles
    ("Pixel Flash X Pro",                  "6.7-inch AMOLED, 108MP camera, 5000mAh battery.",                                        79999,  "Mobiles", 30),
    ("Nova S23 Ultra",                     "Flagship smartphone with S-Pen, 200MP camera, 12GB RAM.",                                99999,  "Mobiles", 20),
    ("Moto Edge 40 Neo",                   "Slim 5G phone with 144Hz display and clean Android experience.",                         24999,  "Mobiles", 50),
    ("iVision 15 Plus",                    "Premium smartphone with A17 chip, ProRAW camera, Dynamic Island.",                       119999, "Mobiles", 12),
    ("RedMi Note 13 Pro",                  "Budget 5G phone with 200MP camera and 67W fast charging.",                               19999,  "Mobiles", 60),
    ("OnePlus Nord CE 4",                  "Smooth 120Hz display, Snapdragon 7s, 100W SUPERVOOC charging.",                          27999,  "Mobiles", 35),

    # Electronics / Accessories
    ("AirSound Pro Wireless Earbuds",      "Active noise cancellation, 30-hour total battery, IPX5 water resistant.",                5999,   "Accessories", 80),
    ("BoomBox Mini Bluetooth Speaker",     "360° sound, 12-hour battery, waterproof design.",                                        2499,   "Accessories", 100),
    ("UltraCharge 65W GaN Charger",        "Compact 65W GaN charger with 3 ports — charge laptop, phone and tablet simultaneously.", 1999,   "Accessories", 150),
    ("SmartWatch Series 8",                "1.9-inch AMOLED, health monitoring, GPS, 18-day battery.",                               12999,  "Accessories", 45),
    ("4K Webcam Pro",                      "Ultra HD webcam with auto-focus and built-in ring light for video calls.",                4499,   "Accessories", 60),
    ("MechKey RGB Keyboard",               "Tactile mechanical keyboard with RGB backlighting and aluminium frame.",                  3999,   "Accessories", 55),
    ("ErgoMouse Wireless",                 "Ergonomic vertical mouse, 2.4GHz wireless, 6-month battery life.",                       1799,   "Accessories", 90),
    ("USB-C Hub 7-in-1",                   "HDMI 4K, 3×USB-A, SD card, PD charging — all in one slim hub.",                         1599,   "Accessories", 120),

    # Fashion — Men
    ("ClassicFit Oxford Shirt",            "100% cotton slim-fit Oxford shirt, available in 8 colours.",                             1299,   "Men", 200),
    ("Urban Cargo Pants",                  "Relaxed-fit cargo pants with 8 pockets, moisture-wicking fabric.",                       1799,   "Men", 150),
    ("LeatherCraft Bifold Wallet",          "Genuine leather slim wallet with RFID blocking.",                                        899,    "Men", 300),
    ("RunMax Pro Sneakers",                "Lightweight running shoes with CloudFoam sole and breathable mesh.",                      3499,   "Men", 80),
    ("Formal Suit Blazer",                 "Slim-fit blazer in premium wool blend, perfect for office or events.",                    4999,   "Men", 40),

    # Fashion — Women
    ("Floral Wrap Midi Dress",             "Breezy floral wrap dress in sustainable viscose, perfect for summer.",                   1599,   "Women", 120),
    ("High-Waist Denim Jeans",             "Classic high-waist skinny jeans in stretch denim.",                                      2199,   "Women", 100),
    ("Pearl Drop Earrings",                "Freshwater pearl drop earrings with gold-plated hooks.",                                  799,    "Women", 250),
    ("Canvas Tote Bag",                    "Large canvas tote with inner zip pocket, eco-friendly and stylish.",                     999,    "Women", 180),
    ("Silk Scrunchie Set (5-pack)",        "Soft silk scrunchies in assorted colours, gentle on hair.",                              399,    "Women", 400),

    # Home & Kitchen
    ("Ceramic Non-Stick Cookware Set",     "5-piece ceramic non-stick cookware set, PFOA-free, induction compatible.",               4999,   "Kitchen", 35),
    ("French Press Coffee Maker",          "Double-wall stainless steel 1L French press for rich, bold coffee.",                     1299,   "Kitchen", 70),
    ("Bamboo Cutting Board Set",           "Set of 3 bamboo cutting boards with juice grooves.",                                     799,    "Kitchen", 120),
    ("Smart Air Fryer 5.5L",               "Digital air fryer with 8 presets, 5.5L capacity, 80% less oil.",                         6999,   "Kitchen", 25),
    ("Stainless Steel Water Bottle 1L",    "Insulated 1L bottle keeps drinks cold 24h / hot 12h.",                                   899,    "Kitchen", 200),

    # Furniture
    ("Ergonomic Office Chair",             "Lumbar support, adjustable armrests, mesh back, up to 150kg.",                          12999,  "Furniture", 15),
    ("Minimalist Bookshelf 5-Tier",        "Industrial-style 5-tier bookshelf in walnut and black metal.",                           7999,   "Furniture", 20),
    ("Foldable Study Desk",                "Space-saving foldable desk with cable management and cup holder.",                       4499,   "Furniture", 30),

    # Sports
    ("Yoga Mat Premium 6mm",               "Eco-friendly TPE yoga mat with alignment lines and carry strap.",                        1499,   "Sports", 100),
    ("Adjustable Dumbbell Set 20kg",       "Quick-adjust dumbbells from 2kg to 20kg, space-saving design.",                         8999,   "Sports", 20),
    ("Resistance Bands Set (5 levels)",    "Latex-free resistance bands with door anchor and carry bag.",                            999,    "Sports", 150),
    ("Running Belt Waist Pack",            "Lightweight water-resistant running belt with phone pocket.",                            699,    "Sports", 200),
    ("Jump Rope Speed Cable",              "Ball-bearing speed rope with aluminium handles and adjustable cable.",                   499,    "Sports", 300),

    # Beauty
    ("Vitamin C Brightening Serum 30ml",   "10% Vitamin C + Niacinamide serum for glowing, even-toned skin.",                       899,    "Beauty", 150),
    ("Hydra-Boost Face Moisturiser",       "Lightweight gel-cream moisturiser with hyaluronic acid, suits all skin types.",          699,    "Beauty", 200),
    ("Rose Gold Makeup Brush Set 12pc",    "Vegan synthetic brushes with rose-gold ferrules and pouch.",                             1299,   "Beauty", 80),
    ("Argan Oil Hair Mask 200ml",          "Deep conditioning mask with Moroccan argan oil, repairs damaged hair.",                  599,    "Beauty", 120),

    # Books
    ("Atomic Habits — James Clear",        "The #1 bestselling guide to building good habits and breaking bad ones.",                499,    "Books", 500),
    ("Deep Work — Cal Newport",            "Rules for focused success in a distracted world.",                                       449,    "Books", 300),
    ("The Alchemist — Paulo Coelho",       "A timeless fable about following your dreams.",                                          299,    "Books", 600),
    ("Zero to One — Peter Thiel",          "Notes on startups and how to build the future.",                                         549,    "Books", 250),
    ("Sapiens — Yuval Noah Harari",        "A brief history of humankind from the Stone Age to the present.",                       599,    "Books", 400),
]

inserted = 0
skipped  = 0
base_date = datetime(2025, 6, 1, tzinfo=timezone.utc)

for i, (name, desc, price, cat_name, stock) in enumerate(PRODUCTS):
    existing = db.query(Product).filter(Product.name == name).first()
    if existing:
        skipped += 1
        continue

    created = base_date + timedelta(days=i * 3)
    p = Product(
        id          = str(uuid.uuid4()),
        name        = name,
        description = desc,
        price       = float(price),
        vendor_id   = SEED_VENDOR_ID,
        category_id = cat_map.get(cat_name),
        stock       = stock,
        avg_rating  = 0.0,
        review_count= 0,
        images      = "[]",
        created_at  = created,
    )
    db.add(p)
    db.flush()

    # Index in ES immediately
    try:
        es.index(index=ES_INDEX, id=p.id, document={
            "id":           p.id,
            "name":         p.name,
            "description":  p.description,
            "price":        p.price,
            "vendor_id":    p.vendor_id,
            "category_id":  p.category_id,
            "stock":        p.stock,
            "avg_rating":   0.0,
            "review_count": 0,
            "created_at":   created.isoformat(),
            "images":       [],
        })
    except Exception as e:
        print(f"  [ES] Failed to index {name}: {e}")

    inserted += 1

db.commit()
db.close()
print(f"\n[seed] Done — {inserted} products inserted, {skipped} already existed.")
print(f"[seed] Total in DB: {inserted + skipped + 2} products")
V