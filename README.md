
# Supermarket Automation

Automates grocery shopping by scraping supermarket websites (starting with Albert Heijn) for ingredient prices, calculating meal costs, and visualizing price trends and savings.

## Project Structure
- `scrapers/`: Jupyter notebooks and scripts for scraping supermarket product data (e.g., `ingredient_scraper.ipynb`).
- `meal_planning/`: Excel files for ingredient lists, meal definitions, price history, and meal-ingredient mappings.
- `dashboards/`: Notebooks and Streamlit apps for meal price calculation and interactive dashboards.

## How It Works
1. **Scraping Ingredients:**
	- Run `scrapers/ingredient_scraper.ipynb` to fetch product info and prices from Albert Heijn using requests and BeautifulSoup.
	- Results are saved to `meal_planning/Ingredients.xlsx` and price history to `Ingredients_history.xlsx`.

2. **Meal Price Calculation:**
	- Use `dashboards/meal_price_calculator.ipynb` to combine ingredient prices with meal-ingredient mappings.
	- Calculates weekly meal costs and savings, saving results to `meal_planning/meal_prices_history.xlsx`.

3. **Dashboarding:**
	- Launch `dashboards/meal_price_dashboard.py` with Streamlit to visualize meal prices, savings, and ingredient price trends.
	- Filter by meal, week, date, and generate shopping lists for selected meals.


## Initial Setup

### Ingredients
Before you start scraping, prepare your ingredient list in an Excel file (see `Ingredients_sample.xlsx` for an example). The file should include the following columns: `IngredientID`, `Ingredient`, `URL`, `Supermarket`.

Fill in these columns for each ingredient you want to track. Once your list is ready, you can start the scraping process as described above and the other columns will fill.

### Meal Prices
Before calculating meal prices, you need a lookup table that maps meals to their ingredients. Create an Excel file (e.g., `meals_ingredients_sample.xlsx`) with columns: `MealID`, `Meal`, `IngredientID`, `Ingredient`. Each row should represent one ingredient used in a meal. This join table allows the system to determine which ingredients are required for each meal and vice versa.

### Meals
To define your meals, create an Excel file such as `meals_sample.xlsx`. This file should include columns like `MealID` and `Meal`, listing each meal you want to track. This setup allows you to manage and reference meals independently, making it easier to update meal definitions and link them to ingredients using the lookup table.

## Usage
1. Scrape latest ingredient prices: run the notebook in `scrapers/`.
2. Calculate meal prices: run the notebook in `dashboards/`.
3. Start the dashboard: `streamlit run dashboards/meal_price_dashboard.py`.

## Future Plans
- Add support for more supermarkets.
- Improve meal planning and optimization logic.
