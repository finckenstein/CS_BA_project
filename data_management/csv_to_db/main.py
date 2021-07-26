#!/usr/bin/env python3
# from kitchenware_to_db import KitchenwareToDB
# from recipes_to_db import RecipesToDB
# from tools_to_db import ToolsToDB
# from recipes_with_video_to_db import RecipesWithVideoToDB
from recipes_with_video_stored_to_db import RecipesWithVideoStoredToDB
from recipes_with_video_not_stored_to_db import RecipesWithVideoNotStoredToDB
from recipes_without_video_to_db import RecipesWithoutVideoToDB
from recipes_with_1to1_video_to_db import RecipesWith1To1VideoToDB
from recipes_without_1to1_video_to_db import RecipesWithout1To1VideoToDB


if __name__ == '__main__':
    RecipesWithVideoStoredToDB()
    RecipesWithVideoNotStoredToDB()
    RecipesWithoutVideoToDB()
    RecipesWith1To1VideoToDB()
    RecipesWithout1To1VideoToDB()

