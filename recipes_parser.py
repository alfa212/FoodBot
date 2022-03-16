import json
import os
from random import choice
from string import digits

import requests
from requests import HTTPError
from bs4 import BeautifulSoup


DIET_TYPES = ['classic_diet', 'keto_diet', 'vegan_diet']
ALLERGY_TYPES = ['eggs', 'lactose', 'nuts']


def save_recipes_json(recipes):
    file_name = 'recipes.json'
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(recipes, json_file, ensure_ascii=False)


def get_image(recipe_image_url, title, folder='images/'):
    url = recipe_image_url

    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f'{title}.jpg')
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)

    return file_path


def parse_recipe_page(soup):
    title = soup.find('article', class_='item-bl item-about').find('h1').text

    ingredients = soup.find('div', class_='ingredients-bl').find_all('li')
    recipe_ingredients = []
    for ingredient in ingredients:
        ingredient_name = ingredient.find('a').find('span').text
        amount = ingredient.find_all('span')[-1].text
        if amount[0] in digits:
            amount = amount
            recipe_ingredients.append(f'{ingredient_name} - {amount}')
        else:
            recipe_ingredients.append(ingredient_name)

    cooking_time = soup.find('time', itemprop='totalTime').text

    cooking_steps = soup.find_all('div', class_='cooking-bl')
    recipe_by_steps = []
    for step, step_text in enumerate(cooking_steps, 1):
        recipe_step = step_text.find("p").text.replace('\r\n', '')
        recipe_by_steps.append(f'{step}. {recipe_step}')

    recipe_image_url = soup.find('div', class_='m-img').find('img')['src']
    image_path = get_image(recipe_image_url, title)

    recipe = {
        'title': title,
        'ingredients': recipe_ingredients,
        'cooking_time': cooking_time,
        'recipe_steps': recipe_by_steps,
        'diet': choice(DIET_TYPES),
        'allergies': choice(ALLERGY_TYPES),
        'image_path': image_path,
    }
    return recipe


def parse_recipes(count_recipes):
    recipe_num = 1
    recipes = {}

    while len(recipes) < count_recipes:
        url = f'https://www.povarenok.ru/recipes/show/{recipe_num}'
        try:
            response = requests.get(url)
            response.raise_for_status()
        except HTTPError:
            recipe_num += 1
            continue

        soup = BeautifulSoup(response.text, 'lxml')

        recipe = parse_recipe_page(soup)
        recipes[recipe_num] = recipe
        recipe_num += 1

    save_recipes_json(recipes)


def main():
    count_recipes = 50
    parse_recipes(count_recipes)


if __name__ == '__main__':
    main()