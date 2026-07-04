/* Insect Kingdom — front-end interactions
   Kept intentionally small: the site is server-rendered Flask,
   this file only powers the Quick View modal. */

(function () {
  "use strict";

  const modalEl = document.getElementById("ikQuickViewModal");
  if (!modalEl) return;

  const modal = new bootstrap.Modal(modalEl);
  const body = document.getElementById("ikQuickViewBody");

  function starString(rating) {
    const full = Math.round(rating);
    return "★".repeat(full) + "☆".repeat(5 - full);
  }

  function renderProduct(p) {
    body.innerHTML = `
      <div class="row g-4">
        <div class="col-md-6">
          <img src="/static/images/${p.image}" alt="${p.name}" class="ik-quickview-img">
        </div>
        <div class="col-md-6">
          <span class="ik-tag">${p.category || "Insect"}</span>
          <h4 class="mt-2 mb-1">${p.name}</h4>
          <p class="ik-scientific">${p.scientific_name || ""}</p>
          <div class="ik-rating mb-2">${starString(p.rating)} <span class="count">(${p.review_count} reviews)</span></div>
          <h4 class="ik-price mb-3">₹${p.price.toFixed(2)}</h4>
          <p class="text-muted small">${p.short_description || ""}</p>
          <p class="mb-3">
            ${p.stock > 0
              ? `<span class="badge bg-success-subtle text-success border border-success-subtle px-3 py-2">In Stock (${p.stock} available)</span>`
              : `<span class="badge bg-danger-subtle text-danger border border-danger-subtle px-3 py-2">Out of Stock</span>`}
          </p>
          <a href="/product/${p.id}" class="btn ik-btn-primary">View Full Details</a>
        </div>
      </div>
    `;
  }

  document.addEventListener("click", function (e) {
    const trigger = e.target.closest("[data-quickview]");
    if (!trigger) return;
    e.preventDefault();

    const productId = trigger.getAttribute("data-quickview");
    body.innerHTML = `
      <div class="text-center py-5">
        <div class="spinner-border" style="color: var(--ik-forest);" role="status"></div>
        <p class="text-muted mt-3 mb-0">Loading specimen details…</p>
      </div>
    `;
    modal.show();

    fetch(`/quick-view/${productId}`)
      .then((res) => {
        if (!res.ok) throw new Error("Not found");
        return res.json();
      })
      .then(renderProduct)
      .catch(() => {
        body.innerHTML = `<p class="text-center text-muted py-5">Sorry, we couldn't load this specimen right now.</p>`;
      });
  });

  // Product-detail gallery: clicking a thumbnail swaps the main image.
  document.querySelectorAll("[data-gallery-thumb]").forEach((thumb) => {
    thumb.addEventListener("click", function () {
      const mainImg = document.getElementById("ikMainProductImage");
      if (!mainImg) return;
      mainImg.src = this.getAttribute("data-gallery-thumb");
      document.querySelectorAll(".ik-thumb").forEach((t) => t.classList.remove("active"));
      this.classList.add("active");
    });
  });
})();
