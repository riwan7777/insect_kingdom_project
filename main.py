import re
import os

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

import database as db
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------- HELPERS ---------------- #

def is_logged_in():
    return "user_email" in session


def is_admin():
    return session.get("user_role") == "admin"


# ---------------- ⚡ FIXED CONTEXT PROCESSOR ---------------- #
# ❌ NO DB CALLS HERE (this was crashing your server)

@app.context_processor
def inject_globals():
    return dict(
        logged_in=is_logged_in(),
        is_admin=is_admin(),
        current_user=session.get("user_fullname"),
        cart_count=0,
        wishlist_ids=set()
    )


# ---------------- CORE ---------------- #

@app.route("/")
def home():
    products = db.get_all_products(sort="rating")[:6]
    return render_template("index.html", products=products)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/insects")
def insects():
    category_id = request.args.get("category")
    search = request.args.get("q", "").strip() or None
    sort = request.args.get("sort")

    products = db.get_all_products(category_id=category_id, search=search, sort=sort)
    categories = db.get_all_categories()

    return render_template(
        "insects.html",
        products=products,
        categories=categories,
        selected=category_id,
        search=search or "",
        sort=sort or "newest",
    )


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = db.get_product_by_id(product_id)

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("insects"))

    return render_template(
        "product_detail.html",
        product=product,
        gallery=db.get_product_gallery(product_id),
        reviews=db.get_product_reviews(product_id),
        related=db.get_related_products(product_id, product["category_id"]),
        bought_together=db.get_frequently_bought_together(product_id, product["category_id"]),
    )


@app.route("/quick-view/<int:product_id>")
def quick_view(product_id):
    product = db.get_product_by_id(product_id)

    if not product:
        return jsonify({"error": "Not found"}), 404

    return jsonify({
        "id": product["id"],
        "name": product["product_name"],
        "scientific_name": product["scientific_name"],
        "price": float(product["price"]),
        "stock": product["stock"],
        "rating": float(product["rating"] or 0),
        "review_count": product["review_count"],
        "image": product["image"],
        "short_description": product["short_description"] or (product["description"] or "")[:160],
        "category": product["category_name"],
    })


# ---------------- AUTH ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not fullname or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if not EMAIL_RE.match(email):
            flash("Invalid email address.", "danger")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("register"))

        if db.get_user_by_email(email):
            flash("Email already registered.", "warning")
            return redirect(url_for("login"))

        hashed = generate_password_hash(password)
        db.create_user(fullname, email, hashed, role="user")

        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = db.get_user_by_email(email)

        if user and check_password_hash(user["password"], password):
            session["user_email"] = user["email"]
            session["user_fullname"] = user["fullname"]
            session["user_role"] = user["role"]

            flash("Login successful!", "success")
            return redirect(url_for("admin" if user["role"] == "admin" else "home"))

        flash("Invalid credentials.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("home"))


# ---------------- CART ---------------- #

@app.route("/cart")
def cart():
    if not is_logged_in():
        return redirect(url_for("login"))

    items = db.get_cart_items(session["user_email"])
    total = sum(item["subtotal"] for item in items)

    return render_template("cart.html", items=items, total=total)


@app.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart_route(product_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    qty = max(1, int(request.form.get("quantity", 1)))
    db.add_to_cart(session["user_email"], product_id, qty)

    flash("Added to cart!", "success")
    return redirect(request.referrer or url_for("cart"))


@app.route("/update-cart/<int:cart_id>", methods=["POST"])
def update_cart_route(cart_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    qty = int(request.form.get("quantity", 1))
    db.update_cart_quantity(cart_id, qty)

    return redirect(url_for("cart"))


@app.route("/remove-from-cart/<int:cart_id>")
def remove_from_cart_route(cart_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    db.remove_from_cart(cart_id)
    flash("Item removed.", "info")
    return redirect(url_for("cart"))


# ---------------- WISHLIST ---------------- #

@app.route("/wishlist")
def wishlist():
    if not is_logged_in():
        return redirect(url_for("login"))

    return render_template(
        "wishlist.html",
        items=db.get_wishlist_items(session["user_email"])
    )


@app.route("/toggle-wishlist/<int:product_id>", methods=["POST"])
def toggle_wishlist_route(product_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    added = db.toggle_wishlist(session["user_email"], product_id)

    flash("Added" if added else "Removed", "success" if added else "info")
    return redirect(request.referrer or url_for("insects"))


# ---------------- CHECKOUT ---------------- #

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if not is_logged_in():
        return redirect(url_for("login"))

    items = db.get_cart_items(session["user_email"])

    if not items:
        flash("Cart is empty.", "info")
        return redirect(url_for("insects"))

    total = sum(item["subtotal"] for item in items)

    if request.method == "POST":
        order_id = db.create_order(session["user_email"], total)
        db.clear_cart(session["user_email"])
        return redirect(url_for("success", order_id=order_id))

    return render_template("cart.html", items=items, total=total, checkout_mode=True)


@app.route("/success")
def success():
    return render_template("success.html", order_id=request.args.get("order_id"))


# ---------------- CONTACT ---------------- #

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not EMAIL_RE.match(email) or len(message) < 10:
            flash("Invalid input.", "danger")
            return render_template("contact.html")

        db.save_contact_message(name, email, message)
        flash("Message sent!", "success")

        return redirect(url_for("contact"))

    return render_template("contact.html")


# ---------------- ADMIN ---------------- #

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not is_logged_in() or not is_admin():
        return redirect(url_for("login"))

    if request.method == "POST":
        db.add_product(
            category_id=request.form.get("category_id"),
            name=request.form.get("product_name"),
            scientific_name=request.form.get("scientific_name"),
            short_description=request.form.get("short_description"),
            description=request.form.get("description"),
            price=request.form.get("price"),
            stock=request.form.get("stock"),
            image=request.form.get("image"),
            habitat=request.form.get("habitat"),
            life_cycle=request.form.get("life_cycle"),
            care_instructions=request.form.get("care_instructions"),
            fun_facts=request.form.get("fun_facts"),
            badge=request.form.get("badge") or None,
        )

        flash("Product added!", "success")
        return redirect(url_for("admin"))

    return render_template(
        "admin.html",
        products=db.get_all_products(),
        categories=db.get_all_categories(),
        messages=db.get_all_messages()
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)