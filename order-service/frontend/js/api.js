/**
 * API Helper
 * ==========
 * All API calls to Django backend.
 * Change BASE_URL if your server
 * runs on different port.
 */

const BASE_URL = "http://127.0.0.1:8000";

// get user id from localStorage
// in real app this comes from JWT token
function getUserId() {
    return localStorage.getItem("user_id")
        || "demo-user-001";
}

// set user id
function setUserId(userId) {
    localStorage.setItem("user_id", userId);
}

/**
 * Cart API calls
 */
const CartAPI = {

    // get cart for current user
    getCart: async function() {
        const userId = getUserId();
        const res = await fetch(
            `${BASE_URL}/api/v1/cart/${userId}/`
        );
        return await res.json();
    },

    // add item to cart
    addItem: async function(
        productId, quantity, price, vendorId
    ) {
        const userId = getUserId();
        const res = await fetch(
            `${BASE_URL}/api/v1/cart/${userId}/add/`,
            {
                method:  "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity:   quantity,
                    price:      price,
                    vendor_id:  vendorId || "vendor-001"
                })
            }
        );
        return await res.json();
    },

    // remove item from cart
    removeItem: async function(productId) {
        const userId = getUserId();
        const res = await fetch(
            `${BASE_URL}/api/v1/cart/`
            + `${userId}/remove/${productId}/`,
            { method: "DELETE" }
        );
        return await res.json();
    },

    // update item quantity
    updateQuantity: async function(
        productId, quantity
    ) {
        const userId = getUserId();
        const res = await fetch(
            `${BASE_URL}/api/v1/cart/`
            + `${userId}/update/${productId}/`,
            {
                method:  "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ quantity })
            }
        );
        return await res.json();
    },

    // clear entire cart
    clearCart: async function() {
        const userId = getUserId();
        const res = await fetch(
            `${BASE_URL}/api/v1/cart/${userId}/clear/`,
            { method: "DELETE" }
        );
        return await res.json();
    }
};

/**
 * Order API calls
 */
const OrderAPI = {

    // checkout — creates order from cart
    checkout: async function() {
        const userId = getUserId();
        const res = await fetch(
            `${BASE_URL}/api/v1/orders/checkout/`,
            {
                method:  "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user_id: userId
                })
            }
        );
        return await res.json();
    },

    // get all orders for user
    getOrders: async function() {
        const userId = getUserId();
        const res = await fetch(
            `${BASE_URL}/api/v1/orders/user/${userId}/`
        );
        return await res.json();
    },

    // get single order
    getOrder: async function(orderId) {
        const res = await fetch(
            `${BASE_URL}/api/v1/orders/${orderId}/`
        );
        return await res.json();
    },

    // cancel order
    cancelOrder: async function(orderId) {
        const res = await fetch(
            `${BASE_URL}/api/v1/orders/${orderId}/cancel/`,
            { method: "PATCH" }
        );
        return await res.json();
    }
};

/**
 * Inventory API calls
 */
const InventoryAPI = {

    // check if product is in stock
    checkStock: async function(
        productId, quantity
    ) {
        const res = await fetch(
            `${BASE_URL}/api/v1/inventory/`
            + `${productId}/check/?quantity=${quantity}`
        );
        return await res.json();
    }
};

/**
 * Show alert message
 */
function showAlert(message, type = "info") {
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector(
        ".container"
    );
    container.insertBefore(
        alertDiv,
        container.firstChild
    );

    // auto remove after 3 seconds
    setTimeout(() => alertDiv.remove(), 3000);
}

/**
 * Show loading spinner
 */
function showLoading(containerId) {
    const container = document.getElementById(
        containerId
    );
    if (container) {
        container.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading...</p>
            </div>
        `;
    }
}

/**
 * Format currency
 */
function formatPrice(amount) {
    return `$${parseFloat(amount).toFixed(2)}`;
}

/**
 * Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
        year:  "numeric",
        month: "long",
        day:   "numeric"
    });
}