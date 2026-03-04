# seed_questions.py  (run once or when needed)
from app import app, db
from app.models import Question  # assume you have this model now
import random


def seed_large_set(total=1200):
    with app.app_context():
        existing = Question.query.count()
        if existing >= total:
            print(f"Already {existing} questions. Skipping.")
            return

        to_add = total - existing
        print(f"Adding {to_add} questions...")

        for i in range(to_add):
            q_type = random.choice(["numbers", "colors", "categories"])

            if q_type == "numbers":
                size = random.randint(5, 10)
                nums = random.sample(range(1, 200), size)
                unsorted = nums[:]
                random.shuffle(unsorted)
                q = Question(
                    type="numbers",
                    title=f"Sort {size} numbers ascending #{i + 1}",
                    items=",".join(map(str, unsorted)),
                    answer=",".join(map(str, sorted(nums))),
                )

            elif q_type == "colors":
                shades = [
                    "White",
                    "Ivory",
                    "Snow",
                    "Floral White",
                    "Light Yellow",
                    "Beige",
                    "Light Gray",
                    "Silver",
                    "Gray",
                    "Dim Gray",
                    "Dark Gray",
                    "Black",
                ]  # expand this list a lot
                size = random.randint(4, 7)
                selected = random.sample(shades * 3, size)  # allow repeats if needed
                random.shuffle(selected)
                sorted_shades = sorted(selected)  # improve with real lightness order
                q = Question(
                    type="colors",
                    title="Sort colors light → dark",
                    items=",".join(selected),
                    answer=",".join(sorted_shades),
                )

            else:
                # categories example — expand lists massively
                fruits = [
                    "Apple",
                    "Banana",
                    "Mango",
                    "Orange",
                    "Strawberry",
                    "Pineapple",
                    "Kiwi",
                    "Grape",
                    "Peach",
                    "Pear",
                    "Plum",
                    "Cherry",
                    "Lemon",
                    "Lime",
                    "Avocado",
                    "Papaya",
                    "Guava",
                    "Fig",
                    "Date",
                    "Coconut",
                ] * 3
                veggies = [
                    "Carrot",
                    "Potato",
                    "Onion",
                    "Tomato",
                    "Cucumber",
                    "Broccoli",
                    "Cauliflower",
                    "Spinach",
                    "Lettuce",
                    "Cabbage",
                    "Pepper",
                    "Eggplant",
                    "Zucchini",
                    "Pumpkin",
                    "Radish",
                    "Beet",
                    "Garlic",
                    "Ginger",
                ] * 3
                animals = [
                    "Lion",
                    "Tiger",
                    "Elephant",
                    "Giraffe",
                    "Monkey",
                    "Bear",
                    "Wolf",
                    "Fox",
                    "Deer",
                    "Zebra",
                    "Kangaroo",
                    "Penguin",
                    "Dolphin",
                    "Shark",
                    "Whale",
                    "Eagle",
                    "Parrot",
                    "Snake",
                    "Crocodile",
                    "Turtle",
                ] * 3

                all_items = fruits + veggies + animals
                size = random.randint(9, 15)
                selected = random.sample(all_items, size)
                random.shuffle(selected)

                q = Question(
                    type="categories",
                    title="Categorize these items",
                    items=",".join(selected),
                    answer="",  # or store correct mapping as JSON string if needed
                )

            db.session.add(q)

        db.session.commit()
        print(f"Done! Total now: {Question.query.count()}")


if __name__ == "__main__":
    seed_large_set(1500)  # or whatever number you want
