from contextlib import contextmanager

import mysql.connector
from config import DB_CONFIG


@contextmanager
def get_cursor(dictionary=True, commit=False):
    """Context-managed DB cursor. Ensures every connection/cursor is
    always closed, even if an exception is raised mid-query."""
    con = mysql.connector.connect(**DB_CONFIG)
    cur = con.cursor(dictionary=dictionary)
    try:
        yield cur
        if commit:
            con.commit()
    finally:
        cur.close()
        con.close()


# ---------------- PRODUCTS ---------------- #

def get_all_products(category_id=None, search=None, sort=None):
    """Returns products, optionally filtered by category / search term
    and sorted. Sort options: 'price_asc', 'price_desc', 'rating', 'newest'."""
    query = """
        SELECT p.*, c.category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE 1=1
    """
    params = []

    if category_id:
        query += " AND p.category_id = %s"
        params.append(category_id)

    if search:
        query += " AND (p.product_name LIKE %s OR p.scientific_name LIKE %s OR p.description LIKE %s)"
        like = f"%{search}%"
        params += [like, like, like]

    sort_map = {
        "price_asc": "p.price ASC",
        "price_desc": "p.price DESC",
        "rating": "p.rating DESC",
        "name": "p.product_name ASC",
        "newest": "p.id DESC",
    }
    query += f" ORDER BY {sort_map.get(sort, 'p.id DESC')}"

    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def get_product_by_id(product_id):
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, c.category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
        """, (product_id,))
        return cur.fetchone()


def get_product_gallery(product_id):
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM product_gallery WHERE product_id = %s ORDER BY sort_order",
            (product_id,)
        )
        return cur.fetchall()


def get_product_reviews(product_id):
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM product_reviews WHERE product_id = %s ORDER BY created_at DESC",
            (product_id,)
        )
        return cur.fetchall()


def get_related_products(product_id, category_id, limit=4):
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, c.category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = %s AND p.id != %s
            ORDER BY p.rating DESC
            LIMIT %s
        """, (category_id, product_id, limit))
        return cur.fetchall()


def get_frequently_bought_together(product_id, category_id, limit=2):
    """Simple heuristic: pick top-rated products from other categories,
    so the pairing feels curated rather than a raw category match."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, c.category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id != %s AND (p.category_id != %s OR p.category_id IS NULL)
            ORDER BY p.rating DESC
            LIMIT %s
        """, (product_id, category_id, limit))
        return cur.fetchall()


def add_product(category_id, name, scientific_name, description, price, stock, image,
                 short_description=None, habitat=None, life_cycle=None,
                 care_instructions=None, fun_facts=None, badge=None):
    with get_cursor(dictionary=False, commit=True) as cur:
        cur.execute("""
            INSERT INTO products
                (category_id, product_name, scientific_name, short_description, description,
                 price, stock, image, habitat, life_cycle, care_instructions, fun_facts, badge)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (category_id, name, scientific_name, short_description, description,
              price, stock, image, habitat, life_cycle, care_instructions, fun_facts, badge))


def delete_product(product_id):
    with get_cursor(dictionary=False, commit=True) as cur:
        cur.execute("DELETE FROM products WHERE id = %s", (product_id,))


def get_all_categories():
    with get_cursor() as cur:
        cur.execute("SELECT * FROM categories ORDER BY category_name")
        return cur.fetchall()


# ---------------- USERS ---------------- #

def create_user(fullname, email, password, role="user"):
    with get_cursor(dictionary=False, commit=True) as cur:
        cur.execute(
            "INSERT INTO users (fullname, email, password, role) VALUES (%s, %s, %s, %s)",
            (fullname, email, password, role)
        )


def get_user_by_email(email):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cur.fetchone()


# ---------------- CART ---------------- #

def add_to_cart(user_email, product_id, quantity=1):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "SELECT * FROM cart WHERE user_email = %s AND product_id = %s",
            (user_email, product_id)
        )
        existing = cur.fetchone()
        if existing:
            cur.execute(
                "UPDATE cart SET quantity = quantity + %s WHERE id = %s",
                (quantity, existing["id"])
            )
        else:
            cur.execute(
                "INSERT INTO cart (user_email, product_id, quantity) VALUES (%s, %s, %s)",
                (user_email, product_id, quantity)
            )


def get_cart_items(user_email):
    with get_cursor() as cur:
        cur.execute("""
            SELECT c.id AS cart_id, c.quantity, p.id AS product_id, p.product_name,
                   p.price, p.image, p.stock, (p.price * c.quantity) AS subtotal
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_email = %s
        """, (user_email,))
        return cur.fetchall()


def update_cart_quantity(cart_id, quantity):
    with get_cursor(dictionary=False, commit=True) as cur:
        if quantity <= 0:
            cur.execute("DELETE FROM cart WHERE id = %s", (cart_id,))
        else:
            cur.execute("UPDATE cart SET quantity = %s WHERE id = %s", (quantity, cart_id))


def remove_from_cart(cart_id):
    with get_cursor(dictionary=False, commit=True) as cur:
        cur.execute("DELETE FROM cart WHERE id = %s", (cart_id,))


def clear_cart(user_email):
    with get_cursor(dictionary=False, commit=True) as cur:
        cur.execute("DELETE FROM cart WHERE user_email = %s", (user_email,))


# ---------------- WISHLIST ---------------- #

def toggle_wishlist(user_email, product_id):
    """Adds the product if not present, removes it if present.
    Returns True if it is now wishlisted, False if it was removed."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            "SELECT id FROM wishlist WHERE user_email = %s AND product_id = %s",
            (user_email, product_id)
        )
        existing = cur.fetchone()
        if existing:
            cur.execute("DELETE FROM wishlist WHERE id = %s", (existing["id"],))
            return False
        cur.execute(
            "INSERT INTO wishlist (user_email, product_id) VALUES (%s, %s)",
            (user_email, product_id)
        )
        return True


def get_wishlist_product_ids(user_email):
    with get_cursor() as cur:
        cur.execute("SELECT product_id FROM wishlist WHERE user_email = %s", (user_email,))
        return {row["product_id"] for row in cur.fetchall()}


def get_wishlist_items(user_email):
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, c.category_name
            FROM wishlist w
            JOIN products p ON w.product_id = p.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE w.user_email = %s
            ORDER BY w.created_at DESC
        """, (user_email,))
        return cur.fetchall()


# ---------------- ORDERS ---------------- #

def create_order(user_email, total_amount):
    with get_cursor(dictionary=False, commit=True) as cur:
        cur.execute(
            "INSERT INTO orders (user_email, total_amount, status) VALUES (%s, %s, %s)",
            (user_email, total_amount, "Placed")
        )
        return cur.lastrowid


# ---------------- CONTACT ---------------- #

def save_contact_message(name, email, message):
    with get_cursor(dictionary=False, commit=True) as cur:
        cur.execute(
            "INSERT INTO contact (name, email, message) VALUES (%s, %s, %s)",
            (name, email, message)
        )


def get_all_messages():
    with get_cursor() as cur:
        cur.execute("SELECT * FROM contact ORDER BY created_at DESC")
        return cur.fetchall()


def delete_message(message_id):
    with get_cursor(dictionary=False, commit=True) as cur:
        cur.execute("DELETE FROM contact WHERE id = %s", (message_id,))
