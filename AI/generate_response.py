import numpy as np
import time
import re
import random
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# ------------------- Database of Recipes -------------------
# Format: {recipe_name: {"calories": int, "protein": int, "carbs": int, "fat": int, "recipe": str, "ingredients": str}}
recipes_db = {
    # Breakfast recipes
    "Overnight Oats": {
        "calories": 350, 
        "protein": 15, 
        "carbs": 55, 
        "fat": 8,
        "ingredients": "1/2 cup rolled oats, 1/2 cup milk, 1/2 cup Greek yogurt, 1 tbsp honey, 1/2 banana sliced, 1 tbsp chia seeds",
        "recipe": "Mix oats, milk, yogurt, and chia seeds in a jar. Refrigerate overnight. Top with banana and honey before serving."
    },
    "Vegetable Omelette": {
        "calories": 320, 
        "protein": 20, 
        "carbs": 5, 
        "fat": 24,
        "ingredients": "3 eggs, 1/4 cup chopped bell peppers, 1/4 cup chopped onions, 1/4 cup chopped tomatoes, 2 tbsp olive oil, salt and pepper to taste",
        "recipe": "Beat eggs in a bowl. Heat oil in a pan, sauté vegetables until soft. Pour eggs over vegetables and cook until set. Fold and serve."
    },
    "Avocado Toast": {
        "calories": 380, 
        "protein": 10, 
        "carbs": 35, 
        "fat": 22,
        "ingredients": "2 slices whole grain bread, 1 ripe avocado, 2 eggs, salt, pepper, red pepper flakes",
        "recipe": "Toast bread. Mash avocado and spread on toast. Top with poached or fried eggs. Season with salt, pepper, and red pepper flakes."
    },
    "Protein Smoothie": {
        "calories": 300, 
        "protein": 25, 
        "carbs": 30, 
        "fat": 8,
        "ingredients": "1 scoop protein powder, 1 banana, 1 cup almond milk, 1 tbsp peanut butter, 1/2 cup frozen berries",
        "recipe": "Blend all ingredients until smooth. Add ice if desired."
    },
    "Greek Yogurt Parfait": {
        "calories": 290, 
        "protein": 18, 
        "carbs": 40, 
        "fat": 6,
        "ingredients": "1 cup Greek yogurt, 1/4 cup granola, 1/2 cup mixed berries, 1 tbsp honey",
        "recipe": "Layer yogurt, granola, and berries in a glass. Drizzle with honey."
    },

    # Lunch recipes
    "Chicken Salad": {
        "calories": 450, 
        "protein": 35, 
        "carbs": 15, 
        "fat": 28,
        "ingredients": "4 oz grilled chicken breast, 2 cups mixed greens, 1/4 cup cherry tomatoes, 1/4 cup cucumber, 2 tbsp olive oil, 1 tbsp balsamic vinegar",
        "recipe": "Grill chicken and slice. Toss with greens and vegetables. Dress with olive oil and vinegar."
    },
    "Quinoa Bowl": {
        "calories": 420, 
        "protein": 18, 
        "carbs": 60, 
        "fat": 12,
        "ingredients": "1 cup cooked quinoa, 1/2 cup black beans, 1/4 cup corn, 1/4 avocado, 1/4 cup salsa, lime juice",
        "recipe": "Mix quinoa, beans, and corn. Top with avocado and salsa. Squeeze lime juice over the top."
    },
    "Tuna Wrap": {
        "calories": 380, 
        "protein": 25, 
        "carbs": 40, 
        "fat": 14,
        "ingredients": "1 can tuna, 1 tbsp light mayo, 1 whole wheat wrap, 1/4 cup lettuce, 1/4 cup diced tomatoes",
        "recipe": "Mix tuna with mayo. Spread on wrap. Add lettuce and tomatoes. Roll up and serve."
    },
    "Lentil Soup": {
        "calories": 320, 
        "protein": 18, 
        "carbs": 45, 
        "fat": 8,
        "ingredients": "1 cup cooked lentils, 1/2 cup carrots, 1/2 cup celery, 1/2 cup onion, 2 cups vegetable broth, 1 tbsp olive oil, herbs and spices",
        "recipe": "Sauté vegetables in oil. Add lentils and broth. Simmer for 20 minutes. Season with herbs and spices."
    },
    "Mediterranean Pasta Salad": {
        "calories": 410, 
        "protein": 15, 
        "carbs": 55, 
        "fat": 16,
        "ingredients": "1 cup whole wheat pasta, 1/4 cup cherry tomatoes, 1/4 cup cucumber, 2 tbsp feta cheese, 2 tbsp olive oil, 1 tbsp red wine vinegar, herbs",
        "recipe": "Cook pasta and cool. Toss with vegetables, cheese, oil, vinegar, and herbs."
    },

    # Dinner recipes
    "Baked Salmon": {
        "calories": 480, 
        "protein": 40, 
        "carbs": 25, 
        "fat": 22,
        "ingredients": "6 oz salmon fillet, 1 cup roasted broccoli, 1/2 cup brown rice, 1 tbsp olive oil, lemon, herbs",
        "recipe": "Season salmon with herbs. Bake at 400°F for 15 minutes. Serve with roasted broccoli and brown rice."
    },
    "Stir-Fry Tofu": {
        "calories": 390, 
        "protein": 22, 
        "carbs": 45, 
        "fat": 16,
        "ingredients": "4 oz tofu, 1 cup mixed vegetables, 1/2 cup brown rice, 1 tbsp soy sauce, 1 tbsp sesame oil, ginger, garlic",
        "recipe": "Press and cube tofu. Stir-fry tofu and vegetables in sesame oil. Add soy sauce, ginger, and garlic. Serve over rice."
    },
    "Turkey Chili": {
        "calories": 420, 
        "protein": 35, 
        "carbs": 40, 
        "fat": 12,
        "ingredients": "4 oz ground turkey, 1/2 cup kidney beans, 1/2 cup diced tomatoes, 1/4 cup onion, 1/4 cup bell pepper, chili powder, cumin",
        "recipe": "Brown turkey. Add vegetables and spices. Simmer for 20 minutes. Add beans and tomatoes. Cook for 10 more minutes."
    },
    "Vegetable Curry": {
        "calories": 360, 
        "protein": 12, 
        "carbs": 50, 
        "fat": 14,
        "ingredients": "1 cup mixed vegetables, 1/2 cup chickpeas, 1/2 cup coconut milk, 1/2 cup brown rice, curry powder, turmeric, garlic, ginger",
        "recipe": "Sauté garlic and ginger. Add vegetables and spices. Pour in coconut milk. Simmer for 15 minutes. Add chickpeas. Serve over rice."
    },
    "Grilled Chicken with Sweet Potato": {
        "calories": 450, 
        "protein": 38, 
        "carbs": 35, 
        "fat": 16,
        "ingredients": "5 oz chicken breast, 1 medium sweet potato, 1 cup steamed green beans, 1 tbsp olive oil, herbs and spices",
        "recipe": "Season chicken with herbs and grill. Bake sweet potato at 400°F for 45 minutes. Steam green beans. Drizzle with olive oil."
    }
}

# Welcome message and instructions
welcome_message = """
🍽️ Welcome to SmartMealPlanner! 🍽️

I'll help you create a personalized 7-day meal plan based on your caloric needs and macronutrient preferences.

To get started, I'll need to collect some information:
1. Your daily calorie goal
2. Your macronutrient preferences (protein/carbs/fat percentages)
3. Any dietary restrictions or allergies

Ready to begin? Type 'START' to continue or 'HELP' for more information.
"""

help_message = """
📋 SmartMealPlanner Help 📋

Here are the commands you can use:
- START: Begin the meal planning process
- HELP: Show this help message
- RESET: Start over with new information
- EXIT: End the conversation

During the meal planning process, I'll ask you questions about your:
- Daily calorie goal (e.g., 2000)
- Macronutrient split (e.g., 30% protein, 40% carbs, 30% fat)
- Dietary restrictions (e.g., vegetarian, gluten-free)
- Food allergies (e.g., nuts, dairy)

After collecting this information, I'll generate a personalized 7-day meal plan with recipes and nutritional information.

Ready to begin? Type 'START' to continue.
"""

# User information dictionary
user_info = {
    "state": "initial",  # Possible states: initial, asking_calories, asking_protein, asking_carbs, asking_fat, asking_restrictions, planning, complete
    "calories": 0,
    "protein_percent": 0,
    "carbs_percent": 0,
    "fat_percent": 0,
    "restrictions": [],
    "allergies": []
}

# Function to generate meal plan based on user information
def create_meal_plan(user_info):
    meal_plan = {}
    today = datetime.now()
    
    # Filter recipes based on user restrictions and allergies
    # In a real implementation, this would be more sophisticated
    available_recipes = {
        "breakfast": ["Overnight Oats", "Vegetable Omelette", "Avocado Toast", "Protein Smoothie", "Greek Yogurt Parfait"],
        "lunch": ["Chicken Salad", "Quinoa Bowl", "Tuna Wrap", "Lentil Soup", "Mediterranean Pasta Salad"],
        "dinner": ["Baked Salmon", "Stir-Fry Tofu", "Turkey Chili", "Vegetable Curry", "Grilled Chicken with Sweet Potato"]
    }
    
    # Calculate macro targets
    protein_calories = user_info["calories"] * (user_info["protein_percent"] / 100)
    carbs_calories = user_info["calories"] * (user_info["carbs_percent"] / 100)
    fat_calories = user_info["calories"] * (user_info["fat_percent"] / 100)
    
    protein_grams = protein_calories / 4  # 4 calories per gram of protein
    carbs_grams = carbs_calories / 4      # 4 calories per gram of carbs
    fat_grams = fat_calories / 9          # 9 calories per gram of fat
    
    daily_targets = {
        "calories": user_info["calories"],
        "protein": protein_grams,
        "carbs": carbs_grams,
        "fat": fat_grams
    }
    
    # Generate 7-day meal plan
    for i in range(7):
        day = (today + timedelta(days=i+1)).strftime("%A, %B %d")
        
        # Randomly select meals for the day
        breakfast = random.choice(available_recipes["breakfast"])
        lunch = random.choice(available_recipes["lunch"])
        dinner = random.choice(available_recipes["dinner"])
        
        # Calculate daily nutrition totals
        day_calories = recipes_db[breakfast]["calories"] + recipes_db[lunch]["calories"] + recipes_db[dinner]["calories"]
        day_protein = recipes_db[breakfast]["protein"] + recipes_db[lunch]["protein"] + recipes_db[dinner]["protein"]
        day_carbs = recipes_db[breakfast]["carbs"] + recipes_db[lunch]["carbs"] + recipes_db[dinner]["carbs"]
        day_fat = recipes_db[breakfast]["fat"] + recipes_db[lunch]["fat"] + recipes_db[dinner]["fat"]
        
        meal_plan[day] = {
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner,
            "totals": {
                "calories": day_calories,
                "protein": day_protein,
                "carbs": day_carbs,
                "fat": day_fat
            }
        }
    
    return meal_plan, daily_targets

# Function to format meal plan as text
def format_meal_plan(meal_plan, daily_targets):
    plan_text = "📅 YOUR 7-DAY MEAL PLAN 📅\n\n"
    plan_text += f"Daily Targets: {daily_targets['calories']} calories, {daily_targets['protein']:.0f}g protein, "
    plan_text += f"{daily_targets['carbs']:.0f}g carbs, {daily_targets['fat']:.0f}g fat\n\n"
    
    # Store data for charts
    days = []
    calories = []
    proteins = []
    carbs = []
    fats = []
    
    for day, meals in meal_plan.items():
        days.append(day.split(',')[0])  # Just the day name for the chart
        calories.append(meals["totals"]["calories"])
        proteins.append(meals["totals"]["protein"])
        carbs.append(meals["totals"]["carbs"])
        fats.append(meals["totals"]["fat"])
        
        plan_text += f"--- {day} ---\n"
        plan_text += f"Breakfast: {meals['breakfast']} ({recipes_db[meals['breakfast']]['calories']} cal)\n"
        plan_text += f"  Ingredients: {recipes_db[meals['breakfast']]['ingredients']}\n"
        plan_text += f"  Recipe: {recipes_db[meals['breakfast']]['recipe']}\n\n"
        
        plan_text += f"Lunch: {meals['lunch']} ({recipes_db[meals['lunch']]['calories']} cal)\n"
        plan_text += f"  Ingredients: {recipes_db[meals['lunch']]['ingredients']}\n"
        plan_text += f"  Recipe: {recipes_db[meals['lunch']]['recipe']}\n\n"
        
        plan_text += f"Dinner: {meals['dinner']} ({recipes_db[meals['dinner']]['calories']} cal)\n"
        plan_text += f"  Ingredients: {recipes_db[meals['dinner']]['ingredients']}\n"
        plan_text += f"  Recipe: {recipes_db[meals['dinner']]['recipe']}\n\n"
        
        plan_text += f"Daily Totals: {meals['totals']['calories']} calories, "
        plan_text += f"{meals['totals']['protein']}g protein, {meals['totals']['carbs']}g carbs, {meals['totals']['fat']}g fat\n\n"
    
    # Create nutrition data for visualization
    nutrition_data = {
        'Day': days,
        'Calories': calories,
        'Protein (g)': proteins,
        'Carbs (g)': carbs,
        'Fat (g)': fats
    }
    
    return plan_text, nutrition_data

# Function to create nutrition charts
def create_nutrition_charts(nutrition_data):
    try:
        df = pd.DataFrame(nutrition_data)
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        
        # Plot 1: Daily calorie distribution
        ax1.bar(df['Day'], df['Calories'], color='skyblue')
        ax1.set_title('Daily Calorie Distribution')
        ax1.set_ylabel('Calories')
        ax1.axhline(y=df['Calories'].mean(), color='r', linestyle='--', label=f'Average: {df["Calories"].mean():.0f} cal')
        ax1.legend()
        
        # Plot 2: Macronutrient breakdown
        width = 0.25
        x = np.arange(len(df['Day']))
        
        ax2.bar(x - width, df['Protein (g)'], width, label='Protein', color='salmon')
        ax2.bar(x, df['Carbs (g)'], width, label='Carbs', color='lightgreen')
        ax2.bar(x + width, df['Fat (g)'], width, label='Fat', color='gold')
        
        ax2.set_title('Daily Macronutrient Breakdown')
        ax2.set_ylabel('Grams')
        ax2.set_xticks(x)
        ax2.set_xticklabels(df['Day'])
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig('meal_plan_nutrition.png')
        plt.close()
        return True
    except Exception as e:
        print(f"Error creating chart: {e}")
        return False

# Main function to process user input
def process_input(user_input):
    user_input = user_input.strip().lower()
    
    # Initial state: waiting for START command
    if user_info["state"] == "initial":
        if user_input == "start":
            user_info["state"] = "asking_calories"
            return "Great! Let's start by setting your daily calorie goal.\n\nHow many calories would you like to consume per day? (e.g., 1800, 2000, 2500)"
        elif user_input == "help":
            return help_message
        elif user_input == "exit":
            return "Thank you for using SmartMealPlanner. Goodbye!"
        else:
            return "I didn't understand that. Please type 'START' to begin, 'HELP' for more information, or 'EXIT' to quit."
    
    # Collecting calorie information
    elif user_info["state"] == "asking_calories":
        try:
            calories = int(user_input)
            if calories < 1200 or calories > 4000:
                return "Please enter a reasonable daily calorie goal between 1200 and 4000 calories."
            user_info["calories"] = calories
            user_info["state"] = "asking_protein"
            return f"Great! Your daily calorie goal is set to {calories} calories.\n\nNow, what percentage of your calories would you like to come from protein? (e.g., 30)"
        except ValueError:
            if user_input == "reset":
                user_info["state"] = "initial"
                return welcome_message
            elif user_input == "help":
                return help_message
            elif user_input == "exit":
                return "Thank you for using SmartMealPlanner. Goodbye!"
            else:
                return "Please enter a valid number for your daily calorie goal (e.g., 2000)."
    
    # Collecting protein percentage
    elif user_info["state"] == "asking_protein":
        try:
            protein_percent = int(user_input)
            if protein_percent < 10 or protein_percent > 50:
                return "Please enter a reasonable protein percentage between 10% and 50%."
            user_info["protein_percent"] = protein_percent
            user_info["state"] = "asking_carbs"
            return f"Great! {protein_percent}% of your calories will come from protein.\n\nWhat percentage of your calories would you like to come from carbohydrates? (e.g., 40)"
        except ValueError:
            if user_input == "reset":
                user_info["state"] = "initial"
                return welcome_message
            elif user_input == "help":
                return help_message
            elif user_input == "exit":
                return "Thank you for using SmartMealPlanner. Goodbye!"
            else:
                return "Please enter a valid number for your protein percentage (e.g., 30)."
    
    # Collecting carbs percentage
    elif user_info["state"] == "asking_carbs":
        try:
            carbs_percent = int(user_input)
            if carbs_percent < 10 or carbs_percent > 60:
                return "Please enter a reasonable carbohydrate percentage between 10% and 60%."
            user_info["carbs_percent"] = carbs_percent
            
            # Check if protein + carbs is already > 100%
            if user_info["protein_percent"] + carbs_percent > 100:
                return f"The combined percentage of protein and carbs ({user_info['protein_percent'] + carbs_percent}%) exceeds 100%. Please enter a lower carbohydrate percentage."
            
            user_info["state"] = "asking_fat"
            return f"Great! {carbs_percent}% of your calories will come from carbohydrates.\n\nWhat percentage of your calories would you like to come from fat? Note: Protein + Carbs + Fat should total 100%. Based on your inputs, this should be {100 - user_info['protein_percent'] - carbs_percent}%."
        except ValueError:
            if user_input == "reset":
                user_info["state"] = "initial"
                return welcome_message
            elif user_input == "help":
                return help_message
            elif user_input == "exit":
                return "Thank you for using SmartMealPlanner. Goodbye!"
            else:
                return "Please enter a valid number for your carbohydrate percentage (e.g., 40)."
    
    # Collecting fat percentage
    elif user_info["state"] == "asking_fat":
        try:
            fat_percent = int(user_input)
            total_percent = user_info["protein_percent"] + user_info["carbs_percent"] + fat_percent
            
            if fat_percent < 10 or fat_percent > 60:
                return "Please enter a reasonable fat percentage between 10% and 60%."
            
            if total_percent != 100:
                return f"The total of protein, carbs, and fat percentages ({total_percent}%) must equal 100%. Please enter {100 - user_info['protein_percent'] - user_info['carbs_percent']}% for fat."
            
            user_info["fat_percent"] = fat_percent
            user_info["state"] = "asking_restrictions"
            return "Great! Now, do you have any dietary restrictions? (e.g., vegetarian, vegan, gluten-free, none)"
        except ValueError:
            if user_input == "reset":
                user_info["state"] = "initial"
                return welcome_message
            elif user_input == "help":
                return help_message
            elif user_input == "exit":
                return "Thank you for using SmartMealPlanner. Goodbye!"
            else:
                return "Please enter a valid number for your fat percentage."
    
    # Collecting dietary restrictions
    elif user_info["state"] == "asking_restrictions":
        if user_input == "none":
            user_info["restrictions"] = []
        else:
            user_info["restrictions"] = [r.strip() for r in user_input.split(",")]
        
        user_info["state"] = "asking_allergies"
        return "Got it! Do you have any food allergies? (e.g., nuts, dairy, eggs, none)"
    
    # Collecting allergies
    elif user_info["state"] == "asking_allergies":
        if user_input == "none":
            user_info["allergies"] = []
        else:
            user_info["allergies"] = [a.strip() for a in user_input.split(",")]
        
        user_info["state"] = "planning"
        return "Thank you for providing all the necessary information! I'm now generating your personalized 7-day meal plan. This might take a moment..."
    
    # Generate meal plan
    elif user_info["state"] == "planning":
        meal_plan, daily_targets = create_meal_plan(user_info)
        plan_text, nutrition_data = format_meal_plan(meal_plan, daily_targets)
        chart_created = create_nutrition_charts(nutrition_data)
        
        user_info["state"] = "complete"
        
        response = "✅ Your 7-day meal plan is ready! ✅\n\n"
        response += "I've created a personalized meal plan based on your requirements:\n"
        response += f"- Daily Calorie Goal: {user_info['calories']} calories\n"
        response += f"- Macros: {user_info['protein_percent']}% protein, {user_info['carbs_percent']}% carbs, {user_info['fat_percent']}% fat\n"
        
        if user_info["restrictions"]:
            response += f"- Dietary Restrictions: {', '.join(user_info['restrictions'])}\n"
        if user_info["allergies"]:
            response += f"- Food Allergies: {', '.join(user_info['allergies'])}\n"
        
        response += "\n" + plan_text
        
        if chart_created:
            response += "\nI've also created nutrition charts to help you visualize your meal plan. Check out the 'meal_plan_nutrition.png' file.\n\n"
        
        response += "Would you like to start over with new information? Type 'RESET' to begin again, or 'EXIT' to quit."
        
        return response
    
    # Plan is complete, waiting for reset or exit
    elif user_info["state"] == "complete":
        if user_input == "reset":
            user_info["state"] = "initial"
            user_info["calories"] = 0
            user_info["protein_percent"] = 0
            user_info["carbs_percent"] = 0
            user_info["fat_percent"] = 0
            user_info["restrictions"] = []
            user_info["allergies"] = []
            return welcome_message
        elif user_input == "exit":
            return "Thank you for using SmartMealPlanner. Goodbye!"
        else:
            return "Your meal plan is complete. Type 'RESET' to start over with new information, or 'EXIT' to quit."
    
    # Default response for unknown states
    else:
        user_info["state"] = "initial"
        return "Something went wrong. Let's start over.\n\n" + welcome_message

# Function to handle user input - this is the main function called by the UI
def generate_meal_plan(user_input):
    # Check for global commands that work in any state
    user_input_lower = user_input.lower().strip()
    
    if user_input_lower == "exit":
        return "Thank you for using SmartMealPlanner. Goodbye!"
    elif user_input_lower == "help":
        return help_message
    elif user_input_lower == "reset":
        # Reset user info
        user_info["state"] = "initial"
        user_info["calories"] = 0
        user_info["protein_percent"] = 0
        user_info["carbs_percent"] = 0
        user_info["fat_percent"] = 0
        user_info["restrictions"] = []
        user_info["allergies"] = []
        return welcome_message
    else:
        # Process based on current state
        return process_input(user_input)

# Return welcome message on first run
if __name__ == "__main__":
    print(welcome_message)