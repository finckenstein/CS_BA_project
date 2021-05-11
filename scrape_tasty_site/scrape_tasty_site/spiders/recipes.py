from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

# run commands in terminal:
# 1. source venv/bin/activate
# 2. scrapy crawl recipes //this will take roughly ~2hrs


def prepend_numbers(preparation):
    prep_list = {}
    i = 1
    for step in preparation:
        prep_list[i] = step
        i += 1
    return prep_list


def format_ingredients(ingredients_list):
    ing_string = ""
    temp_list = []
    i = 0

    for cur_elem in ingredients_list:
        if cur_elem[len(cur_elem) - 1] != ' ' and cur_elem[0] != ' ':
            prev_elem = ingredients_list[i - 1]

            if i == len(ingredients_list) - 1:
                next_elem = ingredients_list[0]
            else:
                next_elem = ingredients_list[i + 1]

            if prev_elem[len(prev_elem) - 1] != ' ' or (next_elem[0] != ' ' and next_elem[0] != ')'):
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

    if not (str(category[0]) in str(ingredients[0])):
        ingredients.insert(0, 'General')
        category.insert(0, 'General')

    while sec_index < len(category) and ing_index < len(ingredients):
        if str(category[sec_index]) in str(ingredients[ing_index]):
            if sec_index == len(category) - 1:
                i = len(ingredients) - 1
                while i >= 0:
                    if str(category[sec_index]) in str(ingredients[i]):
                        temp_ing_list.reverse()
                        dictionary[category[sec_index]] = temp_ing_list
                        temp_ing_list = []
                        break
                    temp_ing_list.append(ingredients[i])
                    i -= 1
            else:
                while ing_index < len(ingredients):
                    if str(category[sec_index + 1]) == str(ingredients[ing_index]):
                        if str(temp_ing_list[0]) == str(category[sec_index]):
                            temp_ing_list.pop(0)
                        dictionary[category[sec_index]] = temp_ing_list
                        temp_ing_list = []
                        break
                    temp_ing_list.append(ingredients[ing_index])
                    ing_index += 1

        sec_index += 1
    return dictionary


def format_time(time):
    formatted_time = ""
    i = 0
    while i < len(time):
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
        formatted_time += time[i]
        i += 1
    return formatted_time


def fetch_time(time1, time2):
    time = {}
    if len(time1) != 0:
        time['Total'] = format_time(time1[0])
        time['Preparation'] = format_time(time1[1])
        time['Cook'] = format_time(time1[2])
    elif len(time2) != 0:
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


class RecipesSpider(CrawlSpider):
    name = 'recipes'
    allowed_domains = ['tasty.co']
    start_urls = ['https://tasty.co/ingredient']
    rules = (Rule(LinkExtractor(deny='buzzfeed.com', allow='ingredient'), follow=True),
             Rule(LinkExtractor(deny='petbytasty.com', allow='topic'), follow=True),
             Rule(LinkExtractor(deny='instagram.com', allow='compilation'), follow=True),
             Rule(LinkExtractor(deny='facebook.com', allow='recipe'), callback='parse_item'))

    def parse_item(self, response):
        url = response.url
        print("\n" + url + "\n")
        if "tasty.co/recipe/" in url:
            print("\nIN BRANCH\n")

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

            yield {'URL': url,
                   'Title': title,
                   'Rating': rating,
                   'Serving': serving,
                   'Time': time,
                   'Categories': raw_ingredient_sections,
                   'Ingredients': ingredients,
                   'Preparation': prep_list,
                   'Nutritional Info': nutritional_val}
