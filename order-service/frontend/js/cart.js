/**
 * Cart Page Logic
 * ===============
 * Handles all cart page interactions.
 */

// load cart when page opens
document.addEventListener(
    "DOMContentLoaded",
    function() {
        // show current user
        document.getElementById("currentUser")
            .textContent = getUserId();

        document.getElementById("userIdInput")
            .value = getUserId();

        // load cart
        loadCart();
    }
);

// set user id
function setUser() {
    const userId = document.getElementById(
        "userIdInput"
    ).value.trim();

    if (!userId) {
        showAlert("Please enter a user ID", "error");
        return;
    }

    setUserId(userId);
    document.getElementById("currentUser")
        .textContent = userId;

    showAlert(
        `User set to: ${userId}`,
        "success"
    );
    loadCart();
}

// load and display cart
async function loadCart() {
    showLoading("cartItems");

    try {
        const response = await CartAPI.getCart();

        if (response.success) {
            displayCart(response.data);
        } else {
            document.getElementById("cartItems")
                .innerHTML = `
                <div class="alert alert-error">
                    Failed to load cart.
                </div>
            `;
        }
    } catch (error) {
        document.getElementById("cartItems")
            .innerHTML = `
            <div class="alert alert-error">
                Cannot connect to server.
                Make sure Django is running!
            </div>
        `;
    }
}

// display cart items
function displayCart(cart) {
    const container = document.getElementById(
        "cartItems"
    );

    if (!cart.items || cart.items.length === 0) {
        container.innerHTML = `
            <div class="empty-state card">
                <h2>🛒 Your cart is empty</h2>
                <p>Add some items above to get started!</p>
            </div>
        `;
        updateSummary(0, 0);
        return;
    }

    // build items HTML
    let html = '<div class="card">';

    cart.items.forEach(function(item) {
        const subtotal = (
            item.price * item.quantity
        ).toFixed(2);

        html += `
            <div class="cart-item"
                 id="item-${item.product_id}">
                <div class="cart-item-info">
                    <h3>
                        Product: ${item.product_id}
                    </h3>
                    <p>
                        Price: ${formatPrice(item.price)}
                        each
                    </p>
                    <p>
                        Subtotal:
                        <strong>
                            ${formatPrice(subtotal)}
                        </strong>
                    </p>
                </div>
                <div class="cart-item-actions">
                    <div class="quantity-control">
                        <button onclick="
                            changeQuantity(
                                '${item.product_id}',
                                ${item.quantity - 1}
                            )
                        ">−</button>
                        <span>${item.quantity}</span>
                        <button onclick="
                            changeQuantity(
                                '${item.product_id}',
                                ${item.quantity + 1}
                            )
                        ">+</button>
                    </div>
                    <button
                        class="btn btn-danger"
                        style="padding:0.4rem 0.8rem"
                        onclick="
                            removeItem(
                                '${item.product_id}'
                            )
                        "
                    >
                        Remove
                    </button>
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;

    // update summary
    updateSummary(
        cart.items.length,
        cart.total || 0
    );
}

// update order summary
function updateSummary(itemCount, total) {
    document.getElementById("itemCount")
        .textContent = itemCount;
    document.getElementById("subtotal")
        .textContent = formatPrice(total);
    document.getElementById("cartTotal")
        .textContent = formatPrice(total);
}

// add item to cart
async function addItem() {
    const productId = document.getElementById(
        "productId"
    ).value.trim();
    const quantity = parseInt(
        document.getElementById("quantity").value
    );
    const price = parseFloat(
        document.getElementById("price").value
    );

    if (!productId) {
        showAlert(
            "Please enter a product ID",
            "error"
        );
        return;
    }

    try {
        const response = await CartAPI.addItem(
            productId, quantity, price
        );

        if (response.success) {
            showAlert(
                "Item added to cart!",
                "success"
            );
            displayCart(response.data);
        } else {
            showAlert(
                "Failed to add item",
                "error"
            );
        }
    } catch (error) {
        showAlert(
            "Cannot connect to server",
            "error"
        );
    }
}

// change item quantity
async function changeQuantity(productId, newQty) {
    if (newQty < 0) return;

    try {
        const response = await CartAPI.updateQuantity(
            productId,
            newQty
        );

        if (response.success) {
            displayCart(response.data);
            if (newQty === 0) {
                showAlert(
                    "Item removed",
                    "info"
                );
            }
        }
    } catch (error) {
        showAlert("Failed to update", "error");
    }
}

// remove item from cart
async function removeItem(productId) {
    try {
        const response = await CartAPI.removeItem(
            productId
        );

        if (response.success) {
            showAlert(
                "Item removed from cart",
                "info"
            );
            displayCart(response.data);
        }
    } catch (error) {
        showAlert(
            "Failed to remove item",
            "error"
        );
    }
}

// clear entire cart
async function clearEntireCart() {
    if (!confirm(
        "Are you sure you want to clear your cart?"
    )) return;

    try {
        const response = await CartAPI.clearCart();

        if (response.success) {
            showAlert(
                "Cart cleared!",
                "info"
            );
            loadCart();
        }
    } catch (error) {
        showAlert(
            "Failed to clear cart",
            "error"
        );
    }
}