# Lily Rudloff Custom Hassio Addons

Welcome to the **Lily Rudloff Custom Hassio Addons** repository. This repository contains custom Home Assistant add-ons designed to enhance your Home Assistant experience with a variety of useful features and utilities.

## Addons

### 1. Personal Shopper

**Addon ID:** `personalshopper`  
**Version:** `0.1.15.17`  
**Description:** Add items to your shopping list using intelligence.

![Personal Shopper](https://img.shields.io/badge/version-0.1.15.17-blue) ![License](https://img.shields.io/badge/license-MIT-green)

#### Overview

**Personal Shopper** is a custom Home Assistant add-on that leverages intelligent suggestions to help you manage your shopping list efficiently. By integrating with your Home Assistant setup, it provides smart recommendations, categorizes items, and optimizes your shopping experience.

#### Features

- **Intelligent Suggestions:** Automatically suggest items based on your existing shopping list.
- **Category Management:** Organize your shopping items into categories for easier navigation.
- **Data Management:** Track usage and manage data purging to optimize database performance.
- **User-Friendly Interface:** Accessible through Home Assistant’s ingress with a responsive web interface.
- **Customizable Settings:** Configure suggestion count and cooldown periods to tailor the experience to your needs.

#### Installation

1. **Add Custom Repository:**
   - In Home Assistant, navigate to **Supervisor** > **Add-on Store**.
   - Click on the three dots in the top right corner and select **Repositories**.
   - Enter the repository URL: `https://github.com/sam2332/HaSS_Addons/` and click **Add**.

2. **Install Personal Shopper:**
   - After adding the repository, find **Personal Shopper** in the Add-on Store.
   - Click **Install**.
   - 
4. **Start the Add-on:**
   - Click **Start** to run the Personal Shopper add-on.
   - Optionally, enable **Start on Boot** for automatic startup.

