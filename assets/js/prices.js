<script>
// Single source of truth for prices
window.MG_PRICES = {
  currency: "USD",
  products: {
    "visual-ai-studio": "19.95",
    "ai-marketing-toolkit": "19.95",
    "ai-writing-workshop": "19.95",
    "ai-business-automation-roi": "19.95",
    "business-builder-bundle": "79.95",
    "chatgpt-mastery-simulator": "19.95",
    "pricing-for-profit-system": "54.95"
  }
};

// Replace any <span data-price="slug"></span> with $price
(function () {
  var products = (window.MG_PRICES && window.MG_PRICES.products) || {};
  document.querySelectorAll("[data-price]").forEach(function (el) {
    var slug = el.getAttribute("data-price");
    var price = products[slug];
    if (price) el.textContent = "$" + price;
  });
})();

// Optional: inject JSON-LD Offer on product pages for SEO
window.injectOfferJSONLD = function ({ slug, name, url }) {
  var price = window.MG_PRICES?.products?.[slug];
  if (!price) return;
  var node = document.createElement("script");
  node.type = "application/ld+json";
  node.text = JSON.stringify({
    "@context": "https://schema.org",
    "@type": "Product",
    "name": name,
    "url": url,
    "offers": {
      "@type": "Offer",
      "priceCurrency": window.MG_PRICES.currency || "USD",
      "price": price,
      "availability": "https://schema.org/InStock"
    }
  });
  document.head.appendChild(node);
};
</script>

