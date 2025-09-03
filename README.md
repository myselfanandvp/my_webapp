# 🌊 WaveLift – Full-Stack E-Commerce Website 🎧

**WaveLift** is a fully functional and responsive **e-commerce platform** built using **Django**, **Tailwind CSS**, and **modern JavaScript**. It allows users to explore and shop products, manage carts, checkout, use referral codes and coupons, and more. It also features an admin panel for managing the platform end-to-end.

![Django](https://img.shields.io/badge/Django-4.x-green?style=flat-square&logo=django)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.x-blue?style=flat-square&logo=tailwind-css)
![Responsive](https://img.shields.io/badge/Responsive-Design-important?style=flat-square&logo=css3)
![Ecommerce](https://img.shields.io/badge/Project_Type-Ecommerce-red?style=flat-square&logo=css3)

---

## 🛒 Features

### 🧑‍💼 User Side
- 👤 User Signup, Login, OTP-based verification
- 🔐 Password reset/change with SweetAlert2 feedback
- 🛍️ Browse products by categories
- 🛒 Add to Cart / Remove from Cart
- 💳 Coupon support & Referrals
- ✅ Checkout with order confirmation
- 📦 Order tracking & return/refund initiation
- 📩 Alerts with Django Messages & SweetAlert2
- 📱 Fully responsive design (Mobile-First)

### 🛠️ Admin Side
- 📦 Manage Products, Categories, Banners
- 🧾 View Orders, Sales Reports
- 🧑‍🤝‍🧑 Manage Users, Referrals, Coupons
- 📊 Dashboard with key metrics
- 🧹 Admin authentication and logout

---

## 🖼️ Screenshots

| Home Page             | Product Page         | Checkout Page         |
|-----------------------|----------------------|------------------------|
| ![](https://via.placeholder.com/300x180.png?text=Home+Page) | ![](https://via.placeholder.com/300x180.png?text=Product+Details) | ![](https://via.placeholder.com/300x180.png?text=Checkout) |

---

## ⚙️ Tech Stack

| Tech        | Usage                |
|-------------|----------------------|
| **Django**  | Backend, Auth, ORM   |
| **Tailwind**| Styling, Layout      |
| **SQLite** / PostgreSQL | Database     |
| **SweetAlert2** | UX Alerts & Feedback |
| **Django Messages** | Flash Messaging |
| **HTML5 + JS** | Interactions |

---

## 📦 Installation

### 🧰 Prerequisites
- Python 3.9+
- pip
- virtualenv

### ⚙️ Setup Instructions

```bash
# Clone the repo
git clone https://github.com/yourusername/wavelift.git
cd wavelift

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser (for admin)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
