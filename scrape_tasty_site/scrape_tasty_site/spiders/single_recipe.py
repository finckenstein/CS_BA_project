import scrapy


def prepend_numbers(preparation):
    prep_list = {}
    i = 1
    for step in preparation:
        prep_list[i] = step
        i += 1
    return prep_list


def format_ingredients(ingredients_list):
    # print("BEFORE: " + str(ingredients_list))
    ing_string = ""
    temp_list = []
    i = 0

    for cur_elem in ingredients_list:
        # print("CURRENT ELEMENT: " + cur_elem)
        if cur_elem[len(cur_elem) - 1] != ' ' and cur_elem[0] != ' ':
            prev_elem = ingredients_list[i - 1]

            if i == len(ingredients_list) - 1:
                next_elem = ingredients_list[0]
            else:
                next_elem = ingredients_list[i + 1]

            # print("PREV: " + prev_elem)
            # print("NEXT: " + next_elem)

            if prev_elem[len(prev_elem) - 1] != ' ' or (next_elem[0] != ' ' and next_elem[0] != ')'):
                # print("FOUND SPLIT: " + cur_elem)
                ing_string += cur_elem
                temp_list.append(ing_string)
                ing_string = ""
                i += 1
                continue
        ing_string += cur_elem
        i += 1

    i = 0
    ing_list = []
    for cur_elem in temp_list:
        if cur_elem[0] == ',' and i != 0:
            prev_elem = temp_list[i - 1]
            entire_ingredient = str(prev_elem) + str(cur_elem)
            ing_list.pop()
            ing_list.append(entire_ingredient)
            i += 1
            continue
        ing_list.append(cur_elem)
        i += 1

    return ing_list


def categorize_ingredients(ingredients, category):
    dictionary = {}

    if len(category) == 0:
        category.insert(0, 'General')
        dictionary['General'] = ingredients
        return dictionary

    sec_index = 0
    ing_index = 0
    temp_ing_list = []

    print("BEFORE: " + str(ingredients))

    if not (str(category[0]) in str(ingredients[0])):
        ingredients.insert(0, 'General')
        category.insert(0, 'General')

    while sec_index < len(category) and ing_index < len(ingredients):
        if str(category[sec_index]) in str(ingredients[ing_index]):

            print("CURRENT INGREDIENT: " + ingredients[ing_index])
            print("CURRENT SECTION NAME: " + category[sec_index])

            if sec_index == len(category) - 1:
                i = len(ingredients) - 1
                print("IN branch")
                while i >= 0:
                    if str(category[sec_index]) in str(ingredients[i]):
                        temp_ing_list.reverse()
                        print("HELLLOOO")
                        print(str(temp_ing_list))
                        dictionary[category[sec_index]] = temp_ing_list
                        temp_ing_list = []
                        break
                    temp_ing_list.append(ingredients[i])
                    i -= 1
            else:
                print("IN ELSE")
                while ing_index < len(ingredients):
                    if str(category[sec_index + 1]) == str(ingredients[ing_index]):

                        print("category: " + str(category[sec_index + 1]))
                        print("ingredient: " + str(ingredients[ing_index]))

                        print("NEW SECTION NAME: " + category[sec_index + 1])
                        print(temp_ing_list)
                        if str(temp_ing_list[0]) == str(category[sec_index]):
                            temp_ing_list.pop(0)
                        dictionary[category[sec_index]] = temp_ing_list
                        temp_ing_list = []
                        break
                    temp_ing_list.append(ingredients[ing_index])
                    print(ing_index)
                    ing_index += 1

        print(sec_index)
        sec_index += 1

    return dictionary


def format_time(time):
    formatted_time = ""
    i = 0
    # print(time)
    while i < len(time):
        # print(time[i])
        if time[i] == ' ':
            i += 1
            continue
        elif time[i] == 'h' or time[i] == 'H':
            formatted_time += ':'
            i += 1
            while i < len(time) and (time[i] == 'r' or time[i] == 'o' or time[i] == 'u'):
                i += 1
            if i == len(time):
                formatted_time += "0"
                break
            elif time[i] == ' ':
                continue
        elif time[i] == 'm' or time[i] == 'M':
            if not (':' in formatted_time):
                temp = formatted_time
                formatted_time = ""
                formatted_time += "0:" + temp
            break
        elif time[i] == 'u' or time[i] == 'U':
            while time[i] != ' ' and i < len(time):
                i += 1
            if time[i] == ' ':
                continue
        print(formatted_time)
        formatted_time += time[i]
        i += 1
    return formatted_time


def fetch_time(time1, time2):
    time = {}
    if len(time1) != 0:
        print("TIME: " + str(time1))
        time['Total'] = format_time(time1[0])
        time['Preparation'] = format_time(time1[1])
        time['Cook'] = format_time(time1[2])
    elif len(time2) != 0:
        print("TIME: " + str(time2))
        time['Total'] = format_time(time2[0])

    return time


def format_nutritional_val(raw_nutritional_info):
    i = 0
    nutritional_val = {}
    while i < len(raw_nutritional_info) - 2:
        if raw_nutritional_info[i].lower() == "calories":
            nutritional_val['Calories'] = raw_nutritional_info[i + 2]
        elif raw_nutritional_info[i].lower() == "fat":
            nutritional_val['Fat'] = str(raw_nutritional_info[i + 2]) + str(raw_nutritional_info[i + 3])
        elif raw_nutritional_info[i].lower() == "carbs":
            nutritional_val['Carbs'] = str(raw_nutritional_info[i + 2]) + str(raw_nutritional_info[i + 3])
        elif raw_nutritional_info[i].lower() == "fiber":
            nutritional_val['Fiber'] = str(raw_nutritional_info[i + 2]) + str(raw_nutritional_info[i + 3])
        elif raw_nutritional_info[i].lower() == "sugar":
            nutritional_val['Sugar'] = str(raw_nutritional_info[i + 2]) + str(raw_nutritional_info[i + 3])
        elif raw_nutritional_info[i].lower() == "protein":
            nutritional_val['Protein'] = str(raw_nutritional_info[i + 2]) + str(raw_nutritional_info[i + 3])
        i += 1

    return nutritional_val


class SingleRecipeSpider(scrapy.Spider):
    name = 'single_recipe'
    allowed_domains = ['tasty.co/recipe/lisas-goutie']
    start_urls = ['https://tasty.co/recipe/lisas-goutie']

    def parse(self, response):
        title = response.xpath('//h1/text()').extract()
        raw_rating = response.xpath('//*[@class="tips-score-heading extra-bold caps xs-text-5"]//text()').extract()
        raw_serving = response.xpath(
            '//*[@class="col md-col-4 xs-mx2 xs-mt2 xs-pb3 md-mt0 xs-flex-order-2 md-flex-order-1"]/p/text()').extract()
        raw_time1 = response.xpath('//*[@class="xs-text-4 xs-hide md-block"]/text()').extract()
        raw_time2 = response.xpath('//*[@class="xs-text-5 extra-bold"]/text()').extract()
        raw_ingredient_sections = response.xpath(
            '//*[@class="ingredient-section-name xs-text-5 extra-bold caps xs-mb1"]/text()').extract()
        raw_ingredient_list = response.xpath('//*[@class="ingredients__section xs-mt1 xs-mb3"]//text()').extract()
        raw_preparation = response.xpath(
            '//*[@class="preparation col xs-flex-grow-1 md-col-8 xs-mx2 xs-mb2 xs-mt2 md-mt0 xs-flex-order-3 '
            'md-flex-order-2"]/ol/li/text()').extract()
        raw_nutritional_value = response.xpath('//*[@class="list-unstyled xs-mb1"]//text()').extract()

        serving = ""
        rating = ""
        if not len(raw_serving) == 0:
            serving = raw_serving[1]
        if not len(raw_rating) == 0:
            rating = raw_rating[0]

        temp_ing = format_ingredients(raw_ingredient_list)
        # raw_ingredient_sections may be modified in categorize_ingredients function
        ingredients = categorize_ingredients(temp_ing, raw_ingredient_sections)
        prep_list = prepend_numbers(raw_preparation)
        time = fetch_time(raw_time1, raw_time2)
        nutritional_val = format_nutritional_val(raw_nutritional_value)

        yield {'Title': title,
               'Rating': rating,
               'Serving': serving,
               'Time': time,
               'Categories': raw_ingredient_sections,
               'Ingredients': ingredients,
               'Preparation': prep_list,
               'Nutritional Info': nutritional_val}
