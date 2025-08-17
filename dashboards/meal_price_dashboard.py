import streamlit as st
import pandas as pd
import plotly.express as px
import socket

# --- Add page navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Shopping List"])

# --- Load data for both pages ---
data_path = 'meal_planning/meal_prices_history.xlsx'
@st.cache_data
def load_data():
    return pd.read_excel(data_path)
df = load_data()
df['Date'] = pd.to_datetime(df['Date'],dayfirst=True)
df['Year'] = df['Date'].dt.year
df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
df['Month'] = df['Date'].dt.strftime('%Y-%m')
df['Week'] = df['Date'].dt.strftime('%Y-W%U')
df['Day'] = df['Date'].dt.strftime('%Y-%m-%d')
df['Date_str'] = df['Date'].dt.strftime('%d-%m-%Y')
df['Day_str'] = df['Date'].dt.strftime('%d-%m-%Y')

if page == "Dashboard":
    st.title("Meal Price Dashboard")

    # Sidebar filters
    st.sidebar.header("Filters")
    all_meals = df['Gerecht'].dropna().unique().tolist()
    selected_meals = st.sidebar.multiselect("Select meals (Gerecht)", all_meals, default=all_meals)
    all_weeks = sorted(df['WeekNr'].dropna().unique())
    selected_weeks = st.sidebar.multiselect("Select week numbers", all_weeks, default=all_weeks)

    # Sidebar date hierarchy filters
    if 'Date' in df.columns:
        st.sidebar.header('Date Hierarchy Filters')
        years = sorted(df['Year'].dropna().unique())
        selected_years = st.sidebar.multiselect('Year', years, default=years)
        quarters = sorted(df[df['Year'].isin(selected_years)]['Quarter'].dropna().unique())
        selected_quarters = st.sidebar.multiselect('Quarter', quarters, default=quarters)
        months = sorted(df[(df['Year'].isin(selected_years)) & (df['Quarter'].isin(selected_quarters))]['Month'].dropna().unique())
        selected_months = st.sidebar.multiselect('Month', months, default=months)
        weeks = sorted(df[(df['Year'].isin(selected_years)) & (df['Quarter'].isin(selected_quarters)) & (df['Month'].isin(selected_months))]['Week'].dropna().unique())
        selected_weeks_hier = st.sidebar.multiselect('Week', weeks, default=weeks)
        days = sorted(df[(df['Year'].isin(selected_years)) & (df['Quarter'].isin(selected_quarters)) & (df['Month'].isin(selected_months)) & (df['Week'].isin(selected_weeks_hier))]['Day'].dropna().unique())
        selected_days = st.sidebar.multiselect('Day', days, default=days)
    else:
        selected_years = selected_quarters = selected_months = selected_weeks_hier = selected_days = []

    # Apply all filters
    filtered_df = df[
        df['Gerecht'].isin(selected_meals) &
        df['WeekNr'].isin(selected_weeks) &
        df['Year'].isin(selected_years) &
        df['Quarter'].isin(selected_quarters) &
        df['Month'].isin(selected_months) &
        df['Week'].isin(selected_weeks_hier) &
        df['Day'].isin(selected_days)
    ]

    # Main table
    st.subheader("Meal Prices Table")
    # Show Date as dd-mm-yyyy in table
    table_df = filtered_df.copy()
    if not table_df.empty:
        table_df['Date'] = table_df['Date'].dt.strftime('%d-%m-%Y')
    st.dataframe(table_df.sort_values(['WeekNr', 'Gerecht', 'MealID']))

    # Plotly chart: Meal price over time
    st.subheader("Meal Price Trends")
    if len(selected_meals) > 0:
        fig = px.line(
            filtered_df,
            x='Date_str',  # Use formatted date
            y='MealPrice_Current',
            color='Gerecht',
            markers=True,
            title="Meal Price Over Time"
        )
        fig.update_layout(xaxis_title="Date (dd-mm-yyyy)")
        st.plotly_chart(fig, use_container_width=True)

    # Plotly chart: Savings over time
    st.subheader("Meal Savings Trends")
    if len(selected_meals) > 0:
        fig2 = px.line(
            filtered_df,
            x='Date_str',  # Use formatted date
            y='Savings abs',
            color='Gerecht',
            markers=True,
            title="Meal Savings Over Time"
        )
        fig2.update_layout(xaxis_title="Date (dd-mm-yyyy)")
        st.plotly_chart(fig2, use_container_width=True)

    # --- Ingredient price trends for all selected meals and weeks ---
    st.subheader("Ingredient Price Trends (All Selected Meals)")
    # Load mappings and ingredient history
    meal_ingredients = pd.read_excel('meal_planning/meals_ingredients.xlsx')
    ingredients_history = pd.read_excel('meal_planning/ingredients_history.xlsx')
    # Ensure Date is datetime for filtering
    if 'Date' in ingredients_history.columns:
        ingredients_history['Date'] = pd.to_datetime(ingredients_history['Date'])
        ingredients_history['Date_str'] = ingredients_history['Date'].dt.strftime('%d-%m-%Y')
    # Get all relevant ingredients for selected meals
    relevant_ingredients = meal_ingredients[meal_ingredients['Gerecht'].isin(selected_meals)]['Ingredient'].unique().tolist()
    # Filter ingredient history for relevant ingredients and selected weeks (by date)
    if not filtered_df.empty:
        min_date = filtered_df['Date'].min()
        max_date = filtered_df['Date'].max()
        ing_hist_filtered = ingredients_history[
            (ingredients_history['Ingredient'].isin(relevant_ingredients)) &
            (ingredients_history['Date'] >= min_date) &
            (ingredients_history['Date'] <= max_date)
        ]
        if not ing_hist_filtered.empty:
            fig_all_ing = px.line(
                ing_hist_filtered,
                x='Date_str',  # Use formatted date
                y='Latest price',
                color='Ingredient',
                markers=True,
                title="Latest Ingredient Prices Over Time (Filtered)"
            )
            fig_all_ing.update_layout(xaxis_title="Date (dd-mm-yyyy)")
            st.plotly_chart(fig_all_ing, use_container_width=True)
        else:
            st.info("No ingredient price data available for the selected meals and weeks.")

    # Show current host IP for network access
    st.sidebar.markdown("---")
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        st.sidebar.info(f"App running on: http://{local_ip}:8501/")
    except Exception:
        st.sidebar.info("App running on your local machine.")

    st.markdown("---")
    st.markdown("Built with Streamlit and Plotly. Data source: meal_prices_history.xlsx")
else:
    st.title("Shopping List")
    # Load required data
    meal_ingredients = pd.read_excel('meal_planning/meals_ingredients.xlsx')
    ingredients_df = pd.read_excel('meal_planning/ingredients.xlsx')
    meals_df = pd.read_excel('meal_planning/meals.xlsx')
    # Ensure current week is selected
    current_week = df['WeekNr'].max()
    week_df = df[df['WeekNr'] == current_week]
    # Meal selection
    available_meals = meals_df['Gerecht'].dropna().unique().tolist()
    selected_meals = st.multiselect("Select dishes for your shopping list", available_meals)
    if selected_meals:
        # Get MealIDs for selected dishes
        selected_meal_ids = meals_df[meals_df['Gerecht'].isin(selected_meals)]['MealID'].tolist()
        # Get all ingredients for selected meals, and always get Gerecht from meals_df
        selected_ingredients = meal_ingredients[meal_ingredients['MealID'].isin(selected_meal_ids)].copy()
        # Merge with ingredient names (FullName) and prices
        selected_ingredients = pd.merge(
            selected_ingredients,
            ingredients_df[['IngredientID', 'FullName', 'Latest price']],
            on='IngredientID',
            how='left'
        )
        selected_ingredients = pd.merge(
            selected_ingredients,
            meals_df[['MealID', 'Gerecht']],
            on='MealID',
            how='left',
            suffixes=('', '_meal')
        )
        # Restore merge logic for FullName columns
        selected_ingredients['FullName'] = selected_ingredients['FullName_x'].combine_first(selected_ingredients['FullName_y'])

        # Always merge Gerecht from meals_df to avoid ambiguity
        selected_ingredients = pd.merge(
            selected_ingredients,
            meals_df[['MealID', 'Gerecht']],
            on='MealID',
            how='left',
            suffixes=('', '_meal')
        )
        # Use Gerecht from meals_df (now in 'Gerecht' column)
        group_cols = ['MealID', 'Gerecht', 'IngredientID', 'FullName']
        rename_dict = {
            'MealID': 'MealID',
            'Gerecht': 'Meal',
            'FullName': 'Ingredient',
            'Quantity': 'Total Quantity',
            'Latest price': 'Unit Price (€)',
            'Total price': 'Total Price (€)'
        }

        shopping_list_grouped = selected_ingredients.groupby(group_cols).agg({
            'Quantity': 'sum',
            'Latest price': 'first'
        }).reset_index()
        shopping_list_grouped['Total price'] = (shopping_list_grouped['Quantity'] * shopping_list_grouped['Latest price']).round(2)

        # Display shopping list with MealID and Meal columns
        st.subheader(f"Shopping List for Week {current_week}")
        st.dataframe(shopping_list_grouped.rename(columns=rename_dict))

        # Show totals for the shopping list
        total_price = shopping_list_grouped['Total price'].sum().round(2)
        ingredient_count = shopping_list_grouped.shape[0]
        st.markdown(f"**Total ingredients:** {ingredient_count}")
        st.markdown(f"**Total price:** € {total_price}")

        # --- Per-meal cost summary (reuse logic from dashboard) ---
        st.subheader("Total Cost Per Meal and Per Portion")
        # For selected meals, get per-meal cost and per-portion from df (history)
        per_meal_df = df[
            (df['WeekNr'] == current_week) &
            (df['MealID'].isin(selected_meal_ids))
        ][['MealID', 'Gerecht', 'MealPrice_Current', 'Price_per_portion']]
        per_meal_df = per_meal_df.drop_duplicates(['MealID', 'Gerecht'])
        per_meal_df = per_meal_df.rename(columns={
            'Gerecht': 'Meal',
            'MealPrice_Current': 'Total Meal Price (€)',
            'Price_per_portion': 'Price per Portion (€)'
        })
        st.dataframe(per_meal_df)

        # Download button for shopping list
        csv = shopping_list_grouped.rename(columns=rename_dict).to_csv(index=False)
        st.download_button("Download Shopping List as CSV", csv, "shopping_list.csv", "text/csv")
    else:
        st.info("Select one or more dishes to generate your shopping list.")
