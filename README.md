# Insect Kingdom — Reconstructed

A premium, educational marketplace for insect specimens — same Flask
architecture as before, rebuilt to feel like a niche nature brand
instead of a generic e-commerce clone.

## Setup

1. Create a MySQL database and load the schema + seed data:
   ```
   mysql -u root -p < schema.sql
   ```
   This file did not exist in the uploaded project (the app pointed at
   a local MySQL database that wasn't included), so it now contains
   the full schema **and** seed data for 7 products built entirely
   from the images already in `static/images/` — nothing invented.

2. Set your DB credentials via environment variables (recommended) or
   edit the fallback defaults in `config.py`:
   ```
   export DB_HOST=localhost
   export DB_USER=root
   export DB_PASSWORD=your_password
   export DB_NAME=insect_store
   export SECRET_KEY=change_this
   ```

3. Install dependencies and run:
   ```
   pip install -r requirements.txt
   python main.py
   ```

4. To get an admin account, register normally, then promote yourself
   from the MySQL shell:
   ```sql
   UPDATE users SET role = 'admin' WHERE email = 'you@example.com';
   ```

## What changed and why

**A note on the "Dragonfly" bug** — the brief mentioned a bug where a
Dragonfly product shows a Butterfly image and an unused Dragonfly
image exists. There is no dragonfly image or product in this upload
(only ant, bee, beetle and butterfly assets), so that specific bug
doesn't apply to this codebase. I did audit every image in
`static/images/` and fixed the mapping issues that *do* exist here:
`bee.png` and four `butterfly-*.jpg` education/detail photos were
present on disk but never referenced anywhere — they're now used in
the product gallery (Monarch Butterfly, Giant Honeybee) instead of
sitting unused.

**Data model** — `schema.sql` adds `short_description`, `badge`,
`rating`, `review_count`, `habitat`, `life_cycle`,
`care_instructions`, and `fun_facts` to `products`, plus new
`product_gallery`, `product_reviews`, and `wishlist` tables. All
seed content is written for the actual images in this project (no
placeholder filler unrelated to the assets).

**Design** — full CSS rewrite (`static/css/style.css`) around forest
green / olive / warm brown / cream with small gold accents, replacing
the previous amber/orange palette. Rounded cards, soft shadows, and
an editorial serif for headings (Playfair Display) paired with
Poppins for body text.

**Templates** — every page was rebuilt on the existing Flask routes
(no routes removed, only extended): richer product detail page with
gallery, tabs-free educational cards, reviews, related products and
"frequently bought together"; search + category + sort controls on
the collection page; a Quick View modal (`/quick-view/<id>` JSON
endpoint + `static/js/main.js`); a wishlist feature with its own page
and toggle route; validated contact form with inline error messages
and re-populated fields on failure; and an admin form extended to
capture the new educational fields.

**Cleanup** — replaced the raw `mysql.connector` calls scattered
through `database.py` with a single context-managed cursor helper so
every connection is guaranteed to close; removed duplicate
connection-handling code across ~20 functions.

**Accessibility / SEO** — skip link, aria-labels on icon-only
controls, alt text on every image, semantic breadcrumbs, per-page
`<title>` and meta description blocks, and Open Graph tags in
`base.html`.

## Known limitation

This app requires a live MySQL connection to run — no database file
was included in the original upload, so `schema.sql` is the seed
source of truth. There's no way for me to run/screenshot the live
site in this environment since it needs MySQL and outbound network
access, both of which are unavailable here — please run it locally
with the steps above.
