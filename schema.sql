-- ============================================================
-- Insect Kingdom — Database Schema & Seed Data
-- ============================================================
-- This file did not exist in the original project (it relied on
-- a MySQL database that was never exported). It is added here so
-- the improved app has real, consistent data to render — including
-- the educational fields (habitat / life cycle / care / facts),
-- a product image gallery, reviews, and wishlist support.
--
-- Run with:  mysql -u root -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS insect_store;
USE insect_store;

-- ---------------- CORE TABLES ---------------- --

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    product_name VARCHAR(150) NOT NULL,
    scientific_name VARCHAR(150),
    short_description VARCHAR(220),
    description TEXT,
    price DECIMAL(10,2) NOT NULL DEFAULT 0,
    stock INT NOT NULL DEFAULT 0,
    image VARCHAR(150) NOT NULL,
    badge VARCHAR(40),                 -- e.g. "Bestseller", "Rare Find", "New"
    rating DECIMAL(2,1) DEFAULT 4.5,
    review_count INT DEFAULT 0,
    habitat TEXT,
    life_cycle TEXT,
    care_instructions TEXT,
    fun_facts TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Extra images shown in the product-detail gallery.
CREATE TABLE IF NOT EXISTS product_gallery (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    image VARCHAR(150) NOT NULL,
    caption VARCHAR(150),
    sort_order INT DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS product_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    reviewer_name VARCHAR(100) NOT NULL,
    rating DECIMAL(2,1) NOT NULL DEFAULT 5.0,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(150) NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS wishlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(150) NOT NULL,
    product_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_wish (user_email, product_id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(150) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Placed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contact (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------- SEED: CATEGORIES ---------------- --

INSERT INTO categories (category_name, slug) VALUES
('Butterflies', 'butterflies'),
('Beetles', 'beetles'),
('Bees & Wasps', 'bees-wasps'),
('Ants', 'ants'),
('Rare & Limited Editions', 'rare-limited')
ON DUPLICATE KEY UPDATE category_name = VALUES(category_name);

-- ---------------- SEED: PRODUCTS ---------------- --
-- Every image in static/images is intentionally mapped to a product
-- or a gallery/education slot below — nothing is left unused.

INSERT INTO products
(category_id, product_name, scientific_name, short_description, description, price, stock, image, badge, rating, review_count, habitat, life_cycle, care_instructions, fun_facts)
VALUES
(
  (SELECT id FROM categories WHERE slug='butterflies'),
  'Monarch Butterfly Specimen', 'Danaus plexippus',
  'A museum-grade preserved Monarch, framed to showcase its full wingspan.',
  'Our Monarch Butterfly specimens are ethically sourced from licensed insect farms and preserved using archival techniques that keep their signature orange-and-black wings vivid for decades. Each specimen is hand-mounted and inspected for symmetry before it leaves our workshop, making it a centerpiece for any collection or classroom display.',
  1499.00, 18, 'butterfly-overview.jpg', 'Bestseller', 4.8, 132,
  'Monarchs thrive in open habitats rich in milkweed — meadows, prairies and roadside verges across North America. Milkweed is the only plant their larvae can eat, so its presence defines where breeding populations can survive.',
  'Life begins as a tiny egg laid on a milkweed leaf, hatching into a striped caterpillar within days. After roughly two weeks of feeding, the caterpillar forms a jade-green chrysalis, emerging 10–14 days later as a fully formed butterfly ready to begin the famous multi-generational migration to Mexico.',
  'Keep the mounted specimen away from direct sunlight and humidity to preserve wing color. Dust gently with a soft, dry brush. No feeding or watering required — this is a preserved display specimen.',
  'Monarchs are the only butterfly known to make a two-way migration like birds, travelling up to 3,000 miles between Canada and central Mexico across multiple generations.'
),
(
  (SELECT id FROM categories WHERE slug='bees-wasps'),
  'Giant Honeybee Specimen', 'Apis dorsata',
  'A striking Giant Honeybee mount, prized for its size and detail.',
  'The Giant Honeybee is one of the largest honeybee species in the world, native to South and Southeast Asia. This specimen highlights the dense hair banding and powerful wing structure that make it such a compelling subject for both collectors and entomology students.',
  1199.00, 24, 'bee.jpg', 'Popular', 4.6, 87,
  'Giant Honeybees build large, single-comb nests in the open — typically suspended from tall trees, cliff faces or building eaves — rather than in enclosed cavities like other honeybee species.',
  'A colony develops through complete metamorphosis: egg, larva, pupa, then adult. Worker bees emerge roughly three weeks after the egg is laid and immediately begin colony duties, from nursing brood to foraging.',
  'Store away from moisture in a sealed display case. If mounted under glass, avoid opening the case frequently to reduce dust exposure.',
  'A single Giant Honeybee colony can contain over 100,000 workers, and the species is known for a dramatic defensive "shimmering" display used to repel predators like hornets.'
),
(
  (SELECT id FROM categories WHERE slug='beetles'),
  'Rainbow Stag Beetle Specimen', 'Phalacrognathus muelleri',
  'An iridescent stag beetle with a metallic rainbow sheen.',
  'Native to the rainforests of Queensland, the Rainbow Stag Beetle is famous for an iridescent exoskeleton that shifts between emerald, copper and violet depending on the light. This specimen is a favorite among collectors seeking a true showpiece.',
  2199.00, 9, 'beetle.jpg', 'Rare Find', 4.9, 54,
  'Found in tropical and subtropical rainforest, particularly around rotting logs and leaf litter where larvae develop in decaying wood.',
  'Eggs are laid in decaying timber; larvae can take one to two years to mature, feeding on rotting wood before pupating and emerging as the adult beetle, which lives for several months.',
  'Display away from direct sunlight, which can dull the metallic cuticle over time. A microfiber cloth is recommended for occasional dusting.',
  'The metallic colors are not pigment — they come from microscopic layered structures in the exoskeleton that reflect light, the same principle used in some butterfly wings.'
),
(
  (SELECT id FROM categories WHERE slug='ants'),
  'Giant Forest Ant Specimen', 'Camponotus gigas',
  'One of the largest ant species in the world, mounted for display.',
  'The Giant Forest Ant is among the largest ants on Earth, with major workers reaching lengths that make individual anatomical features easy to study. This specimen is ideal for educators teaching insect anatomy and colony behavior.',
  899.00, 30, 'ant.jpg', 'Great for Students', 4.7, 61,
  'Native to Southeast Asian rainforests, nesting in large underground colonies or inside decaying logs, often near forest streams.',
  'Colonies are founded by a single queen; eggs develop into larvae, then pupae, before emerging as workers, soldiers or future queens depending on colony needs — a process that can take several weeks.',
  'Keep in a dry display case; avoid handling the specimen directly with bare hands to prevent oils from affecting the exoskeleton.',
  'Major workers can grow beyond 3 cm long and are almost entirely nocturnal, foraging for honeydew and small insects under cover of darkness.'
),
(
  (SELECT id FROM categories WHERE slug='rare-limited'),
  'Emerald Swallowtail — Limited Edition', 'Papilio palinurus',
  'A jewel-toned swallowtail from a small, limited production run.',
  'Part of our small-batch Rare & Limited collection, the Emerald Swallowtail is captured mid-wingspan to highlight its brilliant green scale patches against deep black wings. Only a limited number are released per quarter.',
  2799.00, 5, 'butterfly-rare1.jpg', 'Limited Edition', 5.0, 21,
  'Found in the lowland and montane forests of Southeast Asia, often near streams where males gather to feed on minerals in wet soil.',
  'Like all swallowtails, it passes through egg, caterpillar, chrysalis and adult stages, with the caterpillar mimicking bird droppings early on to avoid predation.',
  'Keep in a UV-filtered display case; the green patches are structurally colored and can appear duller under artificial lighting with high UV output.',
  'The emerald patches are made of transparent scales layered over black pigment — a structural color effect rather than a pigment-based one.'
),
(
  (SELECT id FROM categories WHERE slug='rare-limited'),
  'Blue Morpho — Limited Edition', 'Morpho menelaus',
  'The iconic electric-blue Morpho, from a small curated batch.',
  'The Blue Morpho needs no introduction — its dazzling, light-shifting blue is one of the most recognizable sights in the insect world. This limited release is hand-selected for wing symmetry and color saturation.',
  2599.00, 7, 'butterfly-rare2.jpg', 'Limited Edition', 4.9, 38,
  'Native to the rainforest canopy and understory of Central and South America, favoring sunlit clearings and riverbanks.',
  'Caterpillars feed on legume-family plants for several weeks before forming a jade chrysalis; adults typically live only a few weeks, spending most of their short lives searching for mates.',
  'Display flat and away from direct sun. The underside of the wings is a camouflaged brown — many collectors choose a case that shows both sides.',
  'The blue color is entirely structural, produced by microscopic ridges on the wing scales that scatter light — the wings contain no blue pigment at all.'
),
(
  (SELECT id FROM categories WHERE slug='rare-limited'),
  'Glasswing Butterfly — Limited Edition', 'Greta oto',
  'A translucent, glass-winged butterfly unlike anything else in nature.',
  'The Glasswing''s transparent wings make it one of the most unusual specimens in our catalog. Each one is mounted in a shadow-box style case that lets light pass through the wings for a striking display effect.',
  2999.00, 4, 'butterfly-rare3.jpg', 'Limited Edition', 5.0, 16,
  'Found in the tropical forests of Central and South America, typically at low elevation near streams and forest edges.',
  'Caterpillars feed on toxic nightshade plants, retaining the toxins into adulthood as a defense; adults emerge with fully transparent wings almost immediately after eclosion.',
  'Handle the display case by its base only — the illusion of transparency is best preserved by keeping the glass free of fingerprints.',
  'Its wings lack the colored scales most butterflies have; instead, tiny nanopillars on the wing surface reduce reflection, making the wing nearly as clear as glass.'
);

-- ---------------- SEED: GALLERY IMAGES ---------------- --
-- Reassigns previously-unused butterfly education photos into the
-- Monarch's gallery instead of leaving them orphaned.

INSERT INTO product_gallery (product_id, image, caption, sort_order) VALUES
((SELECT id FROM products WHERE image='butterfly-overview.jpg'), 'butterfly.jpg', 'Resting with wings closed', 1),
((SELECT id FROM products WHERE image='butterfly-overview.jpg'), 'butterfly-habitat.jpg', 'Natural milkweed habitat', 2),
((SELECT id FROM products WHERE image='butterfly-overview.jpg'), 'butterfly-life.jpg', 'Chrysalis to adult transition', 3),
((SELECT id FROM products WHERE image='butterfly-overview.jpg'), 'butterfly-diet.jpg', 'Feeding on nectar', 4),
((SELECT id FROM products WHERE image='bee.jpg'), 'bee.png', 'Wing and body detail illustration', 1);

-- ---------------- SEED: REVIEWS ---------------- --

INSERT INTO product_reviews (product_id, reviewer_name, rating, comment) VALUES
((SELECT id FROM products WHERE image='butterfly-overview.jpg'), 'Aditi R.', 5.0, 'Arrived in perfect condition and the colors are even better in person. Great for my classroom display.'),
((SELECT id FROM products WHERE image='butterfly-overview.jpg'), 'Marcus T.', 4.5, 'Beautiful specimen, well packaged. Wish the frame were slightly larger but overall very happy.'),
((SELECT id FROM products WHERE image='bee.jpg'), 'Priya S.', 4.5, 'Impressive size and detail, exactly as described. Fast shipping too.'),
((SELECT id FROM products WHERE image='beetle.jpg'), 'James O.', 5.0, 'The color-shifting shell is stunning under natural light. Worth every rupee.'),
((SELECT id FROM products WHERE image='ant.jpg'), 'Neha K.', 4.5, 'Great teaching aid — my students were fascinated by the size.'),
((SELECT id FROM products WHERE image='butterfly-rare2.jpg'), 'Daniel W.', 5.0, 'The Blue Morpho is the centerpiece of my collection now. Absolutely gorgeous.');
