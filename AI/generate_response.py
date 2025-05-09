import numpy as np
import random
import re
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import http.client
import json
import os

def get_recipe_from_api(requirements):
    api_key = os.environ.get("OPENAI_API_KEY", "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")  # Better practice: use environment variable
    conn = http.client.HTTPSConnection("api.openai.com")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    meal_type = requirements.get("meal_type", "any meal")
    calories = requirements.get("calories", "")
    protein = requirements.get("protein", "")
    carbs = requirements.get("carbs", "")
    fat = requirements.get("fat", "")
    restrictions = ", ".join(requirements.get("restrictions", []))
    allergies = ", ".join(requirements.get("allergies", []))
    
    prompt = f"""Generate a single healthy {meal_type} recipe with the following criteria:
    - Target calories: approximately {calories} calories
    - Target macros: approximately {protein}g protein, {carbs}g carbs, {fat}g fat
    """
    
    if restrictions:
        prompt += f"- Dietary restrictions: {restrictions}\n"
    if allergies:
        prompt += f"- Must avoid (allergies): {allergies}\n"
    
    prompt += """Format your response as a JSON object with the following structure:
    {
      "name": "Recipe Name",
      "calories": 350,
      "protein": 20,
      "carbs": 40,
      "fat": 10,
      "ingredients": "List of ingredients with quantities",
      "recipe": "Step by step cooking instructions"
    }
    
    The response must be valid JSON. Only include the JSON object in your response, nothing else.
    """
    
    body = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a professional nutritionist and chef specializing in healthy meal planning."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        conn.request("POST", "/v1/chat/completions", body=json.dumps(body), headers=headers)
        response = conn.getresponse()
        
        data = response.read().decode()
        result = json.loads(data)
        
        recipe_json_str = result["choices"][0]["message"]["content"].strip()
        
        # Remove any markdown code block indicators if present
        recipe_json_str = re.sub(r'^```json\s*|\s*```$', '', recipe_json_str, flags=re.MULTILINE)
        
        recipe = json.loads(recipe_json_str)
        return recipe
        
    except Exception as e:
        print(f"Error in API request: {e}")
        return {
            "name": f"Backup {meal_type.capitalize()}",
            "calories": requirements.get("calories", 350),
            "protein": requirements.get("protein", 20),
            "carbs": requirements.get("carbs", 40),
            "fat": requirements.get("fat", 10),
            "ingredients": "Please check API connection. Using backup recipe.",
            "recipe": "API connection error. This is a placeholder recipe."
        }

recipes_cache = {}

def get_or_generate_recipe(meal_type, targets, user_info):
    restrictions_key = "-".join(sorted(user_info.get("restrictions", [])))
    allergies_key = "-".join(sorted(user_info.get("allergies", [])))
    cache_key = f"{meal_type}-{targets['calories']}-{restrictions_key}-{allergies_key}"
    
    if cache_key in recipes_cache:
        recipes = recipes_cache[cache_key]
        if recipes:
            recipe = recipes.pop(0)
            recipes.append(recipe)
            return recipe
    
    requirements = {
        "meal_type": meal_type,
        "calories": targets["calories"],
        "protein": targets["protein"],
        "carbs": targets["carbs"],
        "fat": targets["fat"],
        "restrictions": user_info.get("restrictions", []),
        "allergies": user_info.get("allergies", [])
    }
    
    recipe = get_recipe_from_api(requirements)
    
    if cache_key not in recipes_cache:
        recipes_cache[cache_key] = []
    recipes_cache[cache_key].append(recipe)
    
    return recipe

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
Each recipe is custom-generated based on your requirements using AI.

Ready to begin? Type 'START' to continue.
"""

user_info = {
    "state": "initial",
    "calories": 0,
    "protein_percent": 0,
    "carbs_percent": 0,
    "fat_percent": 0,
    "restrictions": [],
    "allergies": []
}

def create_meal_plan(user_info):
    meal_plan = {}
    today = datetime.now()
    
    protein_calories = user_info["calories"] * (user_info["protein_percent"] / 100)
    carbs_calories = user_info["calories"] * (user_info["carbs_percent"] / 100)
    fat_calories = user_info["calories"] * (user_info["fat_percent"] / 100)
    
    protein_grams = protein_calories / 4
    carbs_grams = carbs_calories / 4
    fat_grams = fat_calories / 9
    
    daily_targets = {
        "calories": user_info["calories"],
        "protein": protein_grams,
        "carbs": carbs_grams,
        "fat": fat_grams
    }
    
    meal_distribution = {
        "breakfast": 0.25,
        "lunch": 0.35,
        "dinner": 0.40
    }
    
    for i in range(7):
        day = (today + timedelta(days=i+1)).strftime("%A, %B %d")
        
        meal_targets = {}
        for meal_type, percentage in meal_distribution.items():
            meal_targets[meal_type] = {
                "calories": int(daily_targets["calories"] * percentage),
                "protein": int(daily_targets["protein"] * percentage),
                "carbs": int(daily_targets["carbs"] * percentage),
                "fat": int(daily_targets["fat"] * percentage)
            }
        
        breakfast = get_or_generate_recipe("breakfast", meal_targets["breakfast"], user_info)
        lunch = get_or_generate_recipe("lunch", meal_targets["lunch"], user_info)
        dinner = get_or_generate_recipe("dinner", meal_targets["dinner"], user_info)
        
        day_calories = breakfast["calories"] + lunch["calories"] + dinner["calories"]
        day_protein = breakfast["protein"] + lunch["protein"] + dinner["protein"]
        day_carbs = breakfast["carbs"] + lunch["carbs"] + dinner["carbs"]
        day_fat = breakfast["fat"] + lunch["fat"] + dinner["fat"]
        
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

def format_meal_plan(meal_plan, daily_targets):
    plan_text = "📅 YOUR 7-DAY MEAL PLAN 📅\n\n"
    plan_text += f"Daily Targets: {daily_targets['calories']} calories, {daily_targets['protein']:.0f}g protein, "
    plan_text += f"{daily_targets['carbs']:.0f}g carbs, {daily_targets['fat']:.0f}g fat\n\n"
    
    days = []
    calories = []
    proteins = []
    carbs = []
    fats = []
    
    for day, meals in meal_plan.items():
        days.append(day.split(',')[0])
        calories.append(meals["totals"]["calories"])
        proteins.append(meals["totals"]["protein"])
        carbs.append(meals["totals"]["carbs"])
        fats.append(meals["totals"]["fat"])
        
        plan_text += f"--- {day} ---\n"
        plan_text += f"Breakfast: {meals['breakfast']['name']} ({meals['breakfast']['calories']} cal)\n"
        plan_text += f"  Ingredients: {meals['breakfast']['ingredients']}\n"
        plan_text += f"  Recipe: {meals['breakfast']['recipe']}\n\n"
        
        plan_text += f"Lunch: {meals['lunch']['name']} ({meals['lunch']['calories']} cal)\n"
        plan_text += f"  Ingredients: {meals['lunch']['ingredients']}\n"
        plan_text += f"  Recipe: {meals['lunch']['recipe']}\n\n"
        
        plan_text += f"Dinner: {meals['dinner']['name']} ({meals['dinner']['calories']} cal)\n"
        plan_text += f"  Ingredients: {meals['dinner']['ingredients']}\n"
        plan_text += f"  Recipe: {meals['dinner']['recipe']}\n\n"
        
        plan_text += f"Daily Totals: {meals['totals']['calories']} calories, "
        plan_text += f"{meals['totals']['protein']}g protein, {meals['totals']['carbs']}g carbs, {meals['totals']['fat']}g fat\n\n"
    
    nutrition_data = {
        'Day': days,
        'Calories': calories,
        'Protein (g)': proteins,
        'Carbs (g)': carbs,
        'Fat (g)': fats
    }
    
    return plan_text, nutrition_data

def create_nutrition_charts(nutrition_data):
    try:
        df = pd.DataFrame(nutrition_data)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        
        ax1.bar(df['Day'], df['Calories'], color='skyblue')
        ax1.set_title('Daily Calorie Distribution')
        ax1.set_ylabel('Calories')
        ax1.axhline(y=df['Calories'].mean(), color='r', linestyle='--', label=f'Average: {df["Calories"].mean():.0f} cal')
        ax1.legend()
        
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
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"meal_plan_nutrition_{timestamp}.png"
        plt.savefig(filename)
        plt.close()
        return filename
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None

def process_input(user_input):
    user_input = user_input.strip().lower()
    
    if user_input == "reset":
        user_info.update({"state": "initial", "calories": 0, "protein_percent": 0, "carbs_percent": 0, "fat_percent": 0, "restrictions": [], "allergies": []})
        return "🔄 Meal planner reset!\n" + welcome_message
    
    if user_input == "exit":
        return "👋 Thanks for using SmartMealPlanner. Stay healthy and happy!"
    
    if user_input == "help":
        return help_message
    
    if user_info["state"] == "initial":
        if user_input == "start":
            user_info["state"] = "asking_calories"
            return "⚡ Let's get started!\nHow many calories would you like to consume daily? (e.g., 2000)"
        return "❓ Type **START** to begin your meal planning journey."
    
    elif user_info["state"] == "asking_calories":
        try:
            calories = int(user_input)
            if calories < 1200 or calories > 4000:
                return "Please enter a reasonable daily calorie goal between 1200 and 4000 calories."
            user_info["calories"] = calories
            user_info["state"] = "asking_protein"
            return f"💪 Great! Now, what percentage of your calories should come from **protein**? (e.g., 30)"
        except ValueError:
            return "🚫 Please enter a valid number for calories (e.g., 2000)."
    
    elif user_info["state"] == "asking_protein":
        try:
            protein_percent = int(user_input)
            if protein_percent < 10 or protein_percent > 50:
                return "Please enter a reasonable protein percentage between 10% and 50%."
            user_info["protein_percent"] = protein_percent
            user_info["state"] = "asking_carbs"
            return f"🍞 Got it. What percentage should come from **carbohydrates**? (e.g., 40)"
        except ValueError:
            return "🚫 Please enter a number like 30."
    
    elif user_info["state"] == "asking_carbs":
        try:
            carbs_percent = int(user_input)
            if carbs_percent < 10 or carbs_percent > 60:
                return "Please enter a reasonable carbohydrate percentage between 10% and 60%."
            
            if user_info["protein_percent"] + carbs_percent > 100:
                return "⚠️ Total macros exceed 100%. Try a lower carb %."
            
            user_info["carbs_percent"] = carbs_percent
            user_info["state"] = "asking_fat"
            remaining = 100 - user_info["protein_percent"] - carbs_percent
            return f"🥑 And the remaining {remaining}% is for **fat**. Please enter: {remaining}"
        except ValueError:
            return "🚫 Please enter a valid percentage."
    
    elif user_info["state"] == "asking_fat":
        try:
            val = int(user_input)
            total = user_info["protein_percent"] + user_info["carbs_percent"] + val
            if total != 100:
                return f"⚠️ Your total macros must equal 100%. You entered {total}%."
            user_info["fat_percent"] = val
            user_info["state"] = "asking_restrictions"
            return "Great! Now, do you have any dietary restrictions? (e.g., vegetarian, vegan, gluten-free, none)"
        except ValueError:
            return "🚫 Please enter a valid fat percentage."
            
    elif user_info["state"] == "asking_restrictions":
        if user_input == "none":
            user_info["restrictions"] = []
        else:
            user_info["restrictions"] = [r.strip() for r in user_input.split(",")]
        
        user_info["state"] = "asking_allergies"
        return "Got it! Do you have any food allergies? (e.g., nuts, dairy, eggs, none)"
    
    elif user_info["state"] == "asking_allergies":
        if user_input == "none":
            user_info["allergies"] = []
        else:
            user_info["allergies"] = [a.strip() for a in user_input.split(",")]
        
        user_info["state"] = "planning"
        return "⏳ Awesome! I'm preparing your meal plan now using AI-generated recipes... This may take a moment, as I'm generating personalized recipes for you. 🍳(type: 'okay')"
    
    elif user_info["state"] == "planning":
        print("Generating meal plan with API...")
        meal_plan, daily_targets = create_meal_plan(user_info)
        plan_text, nutrition_data = format_meal_plan(meal_plan, daily_targets)
        chart_filename = create_nutrition_charts(nutrition_data)
        
        user_info["state"] = "complete"
        
        response = "✅ Your personalized 7-day meal plan is ready! 🎉\n\n"
        response += "I've created a personalized meal plan based on your requirements:\n"
        response += f"- Daily Calorie Goal: {user_info['calories']} calories\n"
        response += f"- Macros: {user_info['protein_percent']}% protein, {user_info['carbs_percent']}% carbs, {user_info['fat_percent']}% fat\n"
        
        if user_info["restrictions"]:
            response += f"- Dietary Restrictions: {', '.join(user_info['restrictions'])}\n"
        if user_info["allergies"]:
            response += f"- Food Allergies: {', '.join(user_info['allergies'])}\n"
        
        response += "\n" + plan_text
        
        if chart_filename:
            response += f"\nI've also created nutrition charts to help you visualize your meal plan. Chart saved as '{chart_filename}'.\n\n"
            
        response += "\n🔁 Type 'RESET' to create another plan or 'EXIT' to quit."
        return response, chart_filename
    
    elif user_info["state"] == "complete":
        return "🔁 To create a new plan, type 'RESET'. To exit, type 'EXIT'."
    
    else:
        user_info["state"] = "initial"
        return "⚠️ Something went wrong. Type 'RESET' to try again."

def generate_meal_plan(user_input):
    return process_input(user_input)
    
if __name__ == "__main__":
    print(welcome_message)