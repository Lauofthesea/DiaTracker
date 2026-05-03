# Changelog

All notable changes to the ML Diabetes Tracker project will be documented in this file.

## [Unreleased] - 2026-05-03

### Added
- **Profile Setup Flow**: First-time users now complete profile setup (age, height, gender, pregnancy status, allergens, health conditions) before health check
- **Filipino Foods Database**: Populated with 90 authentic Filipino foods across 9 categories (Main Dish, Soup, Noodles, Appetizer, Seafood, Vegetable, Snack, Dessert, Porridge)
- **Category Filter**: Added "Common Foods" section with category filters (All, Viands, Snacks, Desserts) for easier food discovery
- **Delete Confirmation Modal**: Custom modal for meal history deletion with clear [Cancel] [Remove] actions
- **Risk Level Display**: Health check history now shows "Low Risk", "Medium Risk", or "High Risk" instead of classification names
- **Visual Icons**: Added icons to Predicted Peak (upward arrow), Calories (flame), and Carbs (bread) sections
- **Meal Type Selection**: Modal for selecting meal type (Breakfast/Lunch/Dinner/Snack) and serving type when adding foods
- **Serving Size Options**: Card-style selection for "Amount (pcs)" or "Serving Size" in manual entry

### Changed
- **Button Text**: Shortened "Confirm Meal & Predict Glucose" to "Confirm Meal" for better mobile display
- **UI Layout**: Moved "Added Items" and "Meal Summary" sections to appear right below "Manual Entry" button for better visibility
- **Glucose Trend Chart**: Implemented fixed color progression (Green → Green → Yellow-Green → Yellow → Yellow-Orange → Red) with smart highlighting
- **Color Synchronization**: "Current Estimate" text, glucose value, "mg/dL" text, and status badge now all match the trend bar color
- **Health Check Processing**: Each processing step now takes 4 seconds (24-28 seconds total) for thorough checking
- **Risk Classification**: Updated to use 75% confidence threshold and 30% diabetes probability for medium risk
- **Return to Dashboard**: Now properly navigates to home page instead of staying on health check page
- **Profile Pre-fill**: Health check form now pre-fills age and height from profile in read-only grey boxes
- **Attention Notice**: Only shows after health check completion AND when there's actual health concern

### Fixed
- **Zero Values Bug**: Fixed meal history showing 0 kcal and 0g carbs by populating nutrients table
- **Decimal Serialization**: Changed calories from Decimal to float for proper JSON serialization
- **Glucose Tracker Updates**: Added page reload after meal logging to update glucose predictions
- **Shadow Overlap**: Removed shadow from Current Estimate card that was overlapping Predicted Peak section
- **Trend Chart Highlighting**: Only current position bar is highlighted; predicted and other bars are greyed out

### Removed
- **Remember Section**: Removed redundant "Remember" alert from health check page (Medical Disclaimer already present in results)
- **X Button**: Removed close buttons from Profile Setup and Health Check modals (cannot be skipped)
- **Blood Emoji**: Removed from glucose tracker for more professional appearance

## Database Changes

### Migrations
- **003_add_age_height_to_profile.py**: Added age and height_cm fields to user_profile
- **004_add_gender_pregnancy.py**: Added gender and is_pregnant fields to user_profile

### Scripts
- **seed_nutrients.py**: Populates nutrients table with 8 base nutrients (Energy, Protein, Carbohydrates, Fat, Fiber, Sugars, Sodium, Water)
- **cleanup_custom_foods.py**: Removes old custom food entries with zero nutrients
- **populate_filipino_foods.py**: Populates database with 90 Filipino foods and their nutritional data

## UI/UX Improvements

### Glucose Tracker
- Fixed color progression for trend bars
- Smart highlighting based on current glucose level
- Pulsing dot indicator on current position
- Color-coded status badges (Green/Yellow/Orange/Red)
- Synchronized colors across all glucose-related elements

### Meal Logging
- Category-based food browsing
- Improved search functionality
- Modal-based food addition with meal type selection
- Real-time nutritional summary
- Glucose impact prediction

### Health Check
- Streamlined first-time user flow
- Profile data pre-filling
- Detailed processing indicators
- Risk-based result display
- Comprehensive recommendations

## Technical Details

### Frontend
- React 18+ with TypeScript
- Tailwind CSS for styling
- Zustand for state management
- React Router for navigation

### Backend
- FastAPI with Python 3.11+
- PostgreSQL 18 with pgcrypto
- SQLAlchemy ORM
- Alembic for migrations
- JWT authentication

### Security
- AES-256 encryption for sensitive data
- Bcrypt password hashing
- Input validation and sanitization
- HIPAA compliance measures

## Known Issues
- None currently

## Future Enhancements
- Historical trend data (past 7 days)
- Tooltips for trend chart bars
- Animation for glucose level changes
- Undo functionality for deleted entries
- Keyboard shortcuts for modals
- Food favorites/recently used section
- Meal templates for quick logging

---

For detailed information about specific features, see the documentation in the `docs/` directory.
