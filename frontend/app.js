const gatewayBaseUrl = "/api";
const authStorageKey = "reliabilityHubAuth";

function getSavedAuth() {
  const savedAuth = localStorage.getItem(authStorageKey);
  if (!savedAuth) {
    return null;
  }
  return JSON.parse(savedAuth);
}

function saveAuth(authData) {
  localStorage.setItem(authStorageKey, JSON.stringify(authData));
}

function clearAuth() {
  localStorage.removeItem(authStorageKey);
}

function getAuthHeaders() {
  const savedAuth = getSavedAuth();
  if (!savedAuth) {
    return {};
  }
  return {
    Authorization: `Bearer ${savedAuth.access_token}`,
  };
}

function updateNavigation() {
  const savedAuth = getSavedAuth();
  const navigation = document.querySelector("nav");
  if (!navigation) {
    return;
  }

  const loginLink = navigation.querySelector('a[href="login.html"]');
  const registerLink = navigation.querySelector('a[href="register.html"]');
  if (loginLink) {
    loginLink.style.display = savedAuth ? "none" : "";
  }
  if (registerLink) {
    registerLink.style.display = savedAuth ? "none" : "";
  }

  let logoutButton = navigation.querySelector("#logoutButton");
  if (savedAuth && !logoutButton) {
    logoutButton = document.createElement("button");
    logoutButton.id = "logoutButton";
    logoutButton.className = "logout-button";
    logoutButton.textContent = "Logout";
    logoutButton.addEventListener("click", () => {
      clearAuth();
      window.location.href = "index.html";
    });
    navigation.appendChild(logoutButton);
  }
  if (!savedAuth && logoutButton) {
    logoutButton.remove();
  }
}

function parseErrorBody(body) {
  if (!body) {
    return "Request failed";
  }
  if (body instanceof Error) {
    return body.message || body.toString();
  }
  if (typeof body === "string") {
    return body;
  }
  if (typeof body.detail === "string") {
    return body.detail;
  }
  if (Array.isArray(body.detail)) {
    return body.detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item?.msg) {
          if (item?.loc) {
            return `${item.loc.join(".")}: ${item.msg}`;
          }
          return item.msg;
        }
        return JSON.stringify(item);
      })
      .join("; ");
  }
  if (body.message) {
    return body.message;
  }
  return JSON.stringify(body);
}

async function requestJson(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  const response = await fetch(`${gatewayBaseUrl}${path}`, {
    ...options,
    headers,
  });

  const text = await response.text();
  let responseBody;
  try {
    responseBody = text ? JSON.parse(text) : null;
  } catch {
    responseBody = text;
  }

  if (!response.ok) {
    throw new Error(parseErrorBody(responseBody));
  }
  return responseBody;
}

function showError(element, message) {
  const text = typeof message === "string" ? message : parseErrorBody(message);
  element.innerHTML = `<p class="error-text">${text}</p>`;
}

function setStatus(element, isHealthy) {
  element.textContent = isHealthy ? "Healthy" : "Down";
  element.classList.toggle("down", !isHealthy);
}

async function checkServiceStatus(path, element) {
  try {
    await requestJson(path);
    setStatus(element, true);
  } catch {
    setStatus(element, false);
  }
}

async function updateServiceStatus() {
  const statusItems = [
    { path: "/auth/health", element: document.querySelector("#authStatus") },
    { path: "/users/health", element: document.querySelector("#userStatus") },
    {
      path: "/products/health",
      element: document.querySelector("#productStatus"),
    },
    { path: "/orders/health", element: document.querySelector("#orderStatus") },
    {
      path: "/payment/health",
      element: document.querySelector("#paymentStatus"),
    },
    { path: "/chat/health", element: document.querySelector("#chatStatus") },
  ];

  await Promise.all(
    statusItems
      .filter((statusItem) => statusItem.element)
      .map((statusItem) =>
        checkServiceStatus(statusItem.path, statusItem.element),
      ),
  );
}

async function loadProducts() {
  const productList = document.querySelector("#productList");
  if (!productList) {
    return;
  }

  try {
    const data = await requestJson("/products/products");
    productList.innerHTML = "";
    data.products.forEach((product) => {
      const productElement = document.createElement("div");
      productElement.className = "product-item";
      productElement.innerHTML = `
        <strong>${product.name}</strong>
        <span>${product.description}</span>
        <p>$${product.price} | Stock: ${product.available_quantity}</p>
        <div class="product-actions">
          <label>Quantity</label>
          <input id="productQty-${product.id}" type="number" min="1" value="1" class="quantity-input" />
          <button id="buyProduct-${product.id}" class="buy-button">Buy</button>
        </div>
      `;
      productList.appendChild(productElement);
      const buyButton = productElement.querySelector(
        `#buyProduct-${product.id}`,
      );
      buyButton?.addEventListener("click", () => buyProduct(product.id));
    });
  } catch (error) {
    productList.textContent = parseErrorBody(error);
  }
}

async function buyProduct(productId) {
  const productBuyResult = document.querySelector("#productBuyResult");
  if (!productBuyResult) {
    return;
  }

  const savedAuth = getSavedAuth();
  if (!savedAuth) {
    showError(productBuyResult, "Please log in before buying a product");
    return;
  }

  try {
    const quantityInput = document.querySelector(`#productQty-${productId}`);
    const quantity = Number(quantityInput?.value) || 1;

    const data = await requestJson("/orders/orders", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        product_id: productId,
        quantity,
      }),
    });

    productBuyResult.innerHTML = `
      <p class="success-text">Product purchased successfully</p>
      <p><strong>Order ID:</strong> ${data.id}</p>
      <p><strong>Product ID:</strong> ${data.product_id}</p>
      <p><strong>Quantity:</strong> ${data.quantity}</p>
      <p><strong>Status:</strong> ${data.status}</p>
      <p><strong>Payment:</strong> processed successfully</p>
    `;

    await loadProducts();
    await loadOrders();
  } catch (error) {
    showError(productBuyResult, error);
  }
}

async function loginUser() {
  const loginResult = document.querySelector("#loginResult");
  try {
    const data = await requestJson("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: document.querySelector("#emailInput").value,
        password: document.querySelector("#passwordInput").value,
      }),
    });
    saveAuth(data);
    updateNavigation();
    loginResult.innerHTML = `
      <p class="success-text">Login successful</p>
      <p><strong>User:</strong> ${data.user.full_name}</p>
      <p><strong>Email:</strong> ${data.user.email}</p>
      <p><strong>Role:</strong> ${data.user.role}</p>
      <p><strong>Token type:</strong> ${data.token_type}</p>
    `;
  } catch (error) {
    showError(loginResult, error);
  }
}

async function registerUser() {
  const registerResult = document.querySelector("#registerResult");
  try {
    const data = await requestJson("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        full_name: document.querySelector("#fullNameInput").value,
        email: document.querySelector("#registerEmailInput").value,
        password: document.querySelector("#registerPasswordInput").value,
      }),
    });
    registerResult.innerHTML = `
      <p class="success-text">${data.message}</p>
      <p><strong>User ID:</strong> ${data.user.id}</p>
      <p><strong>Name:</strong> ${data.user.full_name}</p>
      <p><strong>Email:</strong> ${data.user.email}</p>
      <p><strong>Role:</strong> ${data.user.role}</p>
    `;
  } catch (error) {
    showError(registerResult, error);
  }
}

async function createOrder() {
  const orderResult = document.querySelector("#orderResult");
  const savedAuth = getSavedAuth();
  if (!savedAuth) {
    showError(orderResult, "Please log in before creating an order");
    return;
  }

  try {
    // Call payment endpoint before creating order
    await requestJson("/payment/pay", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ amount: 0 }),
    });

    const data = await requestJson("/orders/orders", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        product_id: Number(document.querySelector("#productIdInput").value),
        quantity: Number(document.querySelector("#quantityInput").value),
      }),
    });
    orderResult.innerHTML = `
      <p class="success-text">Order created successfully</p>
      <p><strong>Payment:</strong> processed successfully</p>
      <p><strong>Order ID:</strong> ${data.id}</p>
      <p><strong>User ID:</strong> ${data.user_id}</p>
      <p><strong>Product ID:</strong> ${data.product_id}</p>
      <p><strong>Quantity:</strong> ${data.quantity}</p>
      <p><strong>Status:</strong> ${data.status}</p>
    `;
    await loadOrders();
  } catch (error) {
    showError(orderResult, error);
  }
}

async function simulatePayment() {
  const paymentResult = document.querySelector("#paymentResult");
  if (!paymentResult) {
    return;
  }

  try {
    const data = await requestJson("/payment/pay", {
      method: "POST",
      body: JSON.stringify({ amount: 1.0 }),
    });

    paymentResult.innerHTML = `
      <p class="success-text">Payment service check passed</p>
      <p><strong>Status:</strong> ${data.status}</p>
      <p><strong>Amount:</strong> ${data.amount}</p>
      <p>This payment service is ready for order processing.</p>
    `;
  } catch (error) {
    showError(paymentResult, error);
  }
}

async function loadOrders() {
  const orderList = document.querySelector("#orderList");
  if (!orderList) {
    return;
  }

  if (!getSavedAuth()) {
    orderList.innerHTML =
      '<p class="muted-text">Please log in to see your orders.</p>';
    return;
  }

  try {
    const data = await requestJson("/orders/orders", {
      headers: getAuthHeaders(),
    });
    orderList.innerHTML = "";
    if (data.orders.length === 0) {
      orderList.innerHTML = '<p class="muted-text">No orders yet.</p>';
      return;
    }
    data.orders.forEach((order) => {
      const orderElement = document.createElement("div");
      orderElement.className = "data-item";
      orderElement.innerHTML = `
        <strong>Order #${order.id}</strong>
        <span>User ID: ${order.user_id}</span>
        <span>Product ID: ${order.product_id}</span>
        <span>Quantity: ${order.quantity}</span>
        <span>Status: ${order.status}</span>
      `;
      orderList.appendChild(orderElement);
    });
  } catch (error) {
    orderList.innerHTML = `<p class="error-text">${parseErrorBody(error)}</p>`;
  }
}

async function sendMessage() {
  const chatResult = document.querySelector("#chatResult");
  const savedAuth = getSavedAuth();
  if (!savedAuth) {
    showError(chatResult, "Please log in before sending a message");
    return;
  }

  try {
    const data = await requestJson("/chat/messages", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        receiver_id: Number(document.querySelector("#receiverIdInput").value),
        message_text: document.querySelector("#messageInput").value,
      }),
    });
    chatResult.innerHTML = `
      <p class="success-text">Message sent successfully</p>
      <p><strong>Message ID:</strong> ${data.id}</p>
      <p><strong>Sender ID:</strong> ${data.sender_id}</p>
      <p><strong>Receiver ID:</strong> ${data.receiver_id}</p>
      <p><strong>Message:</strong> ${data.message_text}</p>
    `;
    await loadMessages();
  } catch (error) {
    showError(chatResult, error);
  }
}

async function loadMessages() {
  const messageList = document.querySelector("#messageList");
  if (!messageList) {
    return;
  }

  if (!getSavedAuth()) {
    messageList.innerHTML =
      '<p class="muted-text">Please log in to see your messages.</p>';
    return;
  }

  try {
    const data = await requestJson("/chat/messages", {
      headers: getAuthHeaders(),
    });
    messageList.innerHTML = "";
    if (data.messages.length === 0) {
      messageList.innerHTML = '<p class="muted-text">No messages yet.</p>';
      return;
    }
    data.messages.forEach((message) => {
      const messageElement = document.createElement("div");
      messageElement.className = "data-item";
      messageElement.innerHTML = `
        <strong>Message #${message.id}</strong>
        <span>From user ${message.sender_id} to user ${message.receiver_id}</span>
        <span>${message.message_text}</span>
      `;
      messageList.appendChild(messageElement);
    });
  } catch (error) {
    messageList.innerHTML = `<p class="error-text">${parseErrorBody(error)}</p>`;
  }
}

function connectButton(buttonId, action) {
  const button = document.querySelector(buttonId);
  if (button) {
    button.addEventListener("click", action);
  }
}

connectButton("#loginButton", loginUser);
connectButton("#registerButton", registerUser);
connectButton("#reloadProductsButton", loadProducts);
connectButton("#createOrderButton", createOrder);
connectButton("#reloadOrdersButton", loadOrders);
connectButton("#checkPaymentButton", simulatePayment);
connectButton("#sendMessageButton", sendMessage);
connectButton("#reloadMessagesButton", loadMessages);
connectButton("#reloadStatusButton", updateServiceStatus);

updateNavigation();
loadProducts();
loadOrders();
loadMessages();
updateServiceStatus();

if (document.querySelector("#reloadStatusButton")) {
  setInterval(updateServiceStatus, 5000);
}
