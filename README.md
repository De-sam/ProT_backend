Here’s the complete `README.md` documentation with all endpoints included:

---

# Tailoring and User Authentication API Documentation

This document provides an overview of all available API endpoints for the tailoring and user authentication system, along with JavaScript examples for frontend integration (e.g., Next.js).

## Table of Contents

1. [User Authentication](#user-authentication)
   - [Register a New User](#register-a-new-user)
   - [User Login](#user-login)
   - [User Logout](#user-logout)
   - [Password Reset Request](#password-reset-request)
   - [Password Reset Confirm](#password-reset-confirm)
   - [Account Activation](#account-activation)
2. [User Profile](#user-profile)
   - [View User Profile](#view-user-profile)
3. [Tailoring](#tailoring)
   - [Add Customer Measurement](#add-customer-measurement)
   - [Edit Customer Measurement](#edit-customer-measurement)
   - [View Tailors (for Customer)](#view-tailors-for-customer)
   - [Create a New Design (for Tailor)](#create-a-new-design-for-tailor)
   - [List Available Designs](#list-available-designs)
   - [Create an Order (for Customer)](#create-an-order-for-customer)
   - [List Orders](#list-orders)
   - [Confirm an Order (for Tailor)](#confirm-an-order-for-tailor)
   - [Release Funds (for Customer)](#release-funds-for-customer)
   - [Request Refund (for Tailor)](#request-refund-for-tailor)

---

## User Authentication

### Register a New User

- **Endpoint**: `POST /api/userauth/register/`
- **Description**: Registers a new user as either a `CUSTOMER` or a `TAILOR`.

```javascript
async function registerUser() {
  const response = await fetch('/api/userauth/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      first_name: 'John',
      last_name: 'Doe',
      email: 'johndoe@example.com',
      password1: 'password123',
      password2: 'password123',
      role: 'CUSTOMER', // or 'TAILOR'
    }),
  });
  const data = await response.json();
  console.log(data);
}
```

### User Login

- **Endpoint**: `POST /api/userauth/login/`
- **Description**: Logs in a user and returns an access token.

```javascript
async function loginUser() {
  const response = await fetch('/api/userauth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'johndoe@example.com',
      password: 'password123',
    }),
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  console.log(data);
}
```

### User Logout

- **Endpoint**: `POST /api/userauth/logout/`
- **Description**: Logs out the user and invalidates their token.

```javascript
async function logoutUser() {
  const refreshToken = localStorage.getItem('refresh_token');
  const response = await fetch('/api/userauth/logout/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${refreshToken}`,
    },
    body: JSON.stringify({ refresh: refreshToken }),
  });
  localStorage.removeItem('access_token');
  console.log(await response.json());
}
```

### Password Reset Request

- **Endpoint**: `POST /api/userauth/password-reset/`
- **Description**: Requests a password reset email.

```javascript
async function requestPasswordReset() {
  const response = await fetch('/api/userauth/password-reset/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'johndoe@example.com' }),
  });
  console.log(await response.json());
}
```

### Password Reset Confirm

- **Endpoint**: `POST /api/userauth/password-reset-confirm/:uid/:token/`
- **Description**: Resets the user password using a token from the password reset email.

```javascript
async function confirmPasswordReset(uid, token) {
  const response = await fetch(`/api/userauth/password-reset-confirm/${uid}/${token}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      new_password: 'newpassword123',
      confirm_password: 'newpassword123',
    }),
  });
  console.log(await response.json());
}
```

### Account Activation

- **Endpoint**: `GET /api/userauth/activate/:uid/:token/`
- **Description**: Activates a user’s account based on the activation email link.

```javascript
async function activateAccount(uid, token) {
  const response = await fetch(`/api/userauth/activate/${uid}/${token}/`, {
    method: 'GET',
  });
  console.log(await response.json());
}
```

---

## User Profile

### View User Profile

- **Endpoint**: `GET /api/tailoring/user/profile/`
- **Description**: Retrieves profile details, including the Algorand wallet balance for both `CUSTOMER` and `TAILOR`.

```javascript
async function getUserProfile() {
  const accessToken = localStorage.getItem('access_token');
  const response = await fetch('/api/tailoring/user/profile/', {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  const data = await response.json();
  console.log(data);
}
```

---

## Tailoring

### Add Customer Measurement

- **Endpoint**: `POST /api/tailoring/add-measurement/<str:customer_id>/`
- **Description**: Adds a new measurement for a customer. Only accessible by tailors.

```javascript
async function addMeasurement(customerId) {
  const accessToken = localStorage.getItem('access_token');
  const response = await fetch(`/api/tailoring/add-measurement/${customerId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      category: 1,
      neck_circumference_cm: 40,
      shoulder_width_cm: 50,
    }),
  });
  console.log(await response.json());
}
```

### Edit Customer Measurement

- **Endpoint**: `PUT /api/tailoring/edit-measurement/<int:measurement_id>/`
- **Description**: Allows a tailor to edit a specific customer's measurement.

```javascript
async function editMeasurement(measurementId) {
  const accessToken = localStorage.getItem('access_token');
  const response = await fetch(`/api/tailoring/edit-measurement/${measurementId}/`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      neck_circumference_cm: 41,  // Example updated values
    }),
  });
  console.log(await response.json());
}
```

### View Tailors (for Customer)

- **Endpoint**: `GET /api/tailoring/customer/tailors/`
- **Description**: Retrieves a list of tailors associated with a customer.

```javascript
async function fetchTailors() {
  const accessToken = localStorage.getItem('access_token');
  const response = await fetch('/api/tailoring/customer/tailors/', {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  console.log(await response.json());
}
```

### Create a New Design (for Tailor)

- **Endpoint**: `POST /api/tailoring/designs/add/`
- **Description**: Allows a tailor to create a new design.

```javascript
async function createDesign() {
  const accessToken = localStorage.getItem('access_token');
  const formData = new FormData();
  formData.append('name', 'Casual Shirt');
  formData.append('description', 'A stylish casual shirt');
  formData.append('price', '29.99');
  formData.append('image', selectedFile);
  
  const response = await fetch('/api/tailoring/designs/add/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${accessToken}` },
    body: formData,
  });
  console.log(await response.json());
}
```

### List Available Designs

- **Endpoint**: `GET /api/tailoring/designs/`
- **Description**: Retrieves a list of designs, filtered by the user role.

```javascript
async function listDesigns() {
  const accessToken = localStorage.getItem('access_token');
  const response = await fetch('/api/tailoring/designs/', {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  console.log(await response.json());
}
```

### Create an Order (for Customer)

- **Endpoint**: `POST /api/tailoring/orders/create/<int:design_id>/`
- **Description**: Places an order for a specific design.

```javascript
async function createOrder(designId) {
  const accessToken = localStorage.getItem('access_token');
  const response = await fetch(`/api/tailoring/orders/create/${designId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
  });
  console

.log(await response.json());
}
```

### List Orders

- **Endpoint**: `GET /api/tailoring/orders/`
- **Description**: Lists orders based on the role (customer or tailor).

```javascript
async function listOrders() {
  const accessToken = localStorage.getItem('access_token');
  const response = await fetch('/api/tailoring/orders/', {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  console.log(await response.json());
}
```

### Confirm an Order (for Tailor)

- **Endpoint**: `POST /api/tailoring/orders/confirm/<int:order_id>/`
- **Description**: Confirms that an order has been completed by the tailor.

```javascript
async function confirmOrder(orderId) {
  const accessToken = localStorage.getItem('access_token');
  const response = await fetch(`/api/tailoring/orders/confirm/${orderId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
  });
  console.log(await response.json());
}
```

### Release Funds (for Customer)

- **Endpoint**: `POST /api/tailoring/orders/release-funds/<int:order_id>/`
- **Description**: Allows a customer to release funds to the tailor for an order via the Algorand smart contract.

```javascript
async function releaseFunds(orderId) {
  const accessToken = localStorage.getItem('access_token');
  const response = await fetch(`/api/tailoring/orders/release-funds/${orderId}/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  console.log(await response.json());
}
```

### Request Refund (for Tailor)

- **Endpoint**: `POST /api/tailoring/orders/refund-funds/<int:order_id>/`
- **Description**: Allows a tailor to request a refund from the smart contract if the order has not been approved by the customer.

```javascript
async function requestRefund(orderId) {
  const accessToken = localStorage.getItem('access_token');
  const response = await fetch(`/api/tailoring/orders/refund-funds/${orderId}/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  console.log(await response.json());
}
```
