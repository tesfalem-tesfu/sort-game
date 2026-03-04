# backend/generate_questions.py
# Improved version – more variety, better question phrasing, optional truncation,
# progress feedback, idempotency, and category support

import random
import string
from typing import List
from app import app, db
from app.models import Question  # make sure this model exists


def generate_number_questions(count: int = 400, asc: bool = True) -> List[Question]:
    questions = []
    for i in range(count):
        size = random.randint(5, 9)
        nums = random.sample(range(1, 301), size)  # wider range = more challenge
        shuffled = nums[:]
        random.shuffle(shuffled)

        direction = "ascending" if asc else "descending"
        q = Question(
            type="numbers",
            question=f"Sort these {size} numbers in {direction} order",
            items=",".join(map(str, shuffled)),
            answer=",".join(
                map(str, sorted(nums) if asc else sorted(nums, reverse=True))
            ),
            difficulty=random.choice(["easy", "medium", "hard"])
            if random.random() < 0.4
            else None,
        )
        questions.append(q)
    return questions


def generate_letter_questions(count: int = 400, asc: bool = True) -> List[Question]:
    questions = []
    for i in range(count):
        size = random.randint(5, 9)
        # Mix upper & lower for more realism
        use_upper = random.random() < 0.35
        pool = string.ascii_uppercase if use_upper else string.ascii_lowercase
        letters = random.sample(pool, size)
        shuffled = letters[:]
        random.shuffle(shuffled)

        direction = "alphabetical" if asc else "reverse alphabetical"
        case_word = "uppercase" if use_upper else "lowercase"
        q = Question(
            type="letters",
            question=f"Sort these {size} {case_word} letters in {direction} order",
            items=",".join(shuffled),
            answer=",".join(sorted(letters) if asc else sorted(letters, reverse=True)),
            difficulty=random.choice(["easy", "medium"])
            if random.random() < 0.5
            else None,
        )
        questions.append(q)
    return questions


def generate_color_questions(count: int = 250) -> List[Question]:
    # Expanded realistic color names (feel free to add 50–100 more)
    colors = [
        "red",
        "blue",
        "green",
        "yellow",
        "purple",
        "orange",
        "pink",
        "brown",
        "black",
        "white",
        "gray",
        "cyan",
        "magenta",
        "lime",
        "indigo",
        "violet",
        "turquoise",
        "maroon",
        "olive",
        "navy",
        "teal",
        "coral",
        "salmon",
        "gold",
        "silver",
        "beige",
        "lavender",
        "plum",
        "crimson",
        "azure",
    ]

    questions = []
    for _ in range(count):
        size = random.randint(4, 7)
        selected = random.sample(colors, size)
        shuffled = selected[:]
        random.shuffle(shuffled)

        # Two modes: alphabetical or "length of name" (proxy for visual complexity)
        mode = random.choice(["alpha", "length"])
        if mode == "alpha":
            q_text = "Sort these colors in alphabetical order"
            ans = sorted(selected)
        else:
            q_text = "Sort these colors by name length (shortest to longest)"
            ans = sorted(selected, key=len)

        q = Question(
            type="colors",
            question=q_text,
            items=",".join(shuffled),
            answer=",".join(ans),
        )
        questions.append(q)
    return questions


def generate_category_questions(count: int = 300) -> List[Question]:
    # Very basic version – real game would need bin mapping, not single answer string
    # For now we store flattened correct order as placeholder
    categories = {
        "fruits": [
            "apple",
            "banana",
            "mango",
            "orange",
            "strawberry",
            "pineapple",
            "kiwi",
            "grape",
            "peach",
            "pear",
            "cherry",
            "lemon",
            "lime",
            "avocado",
            "papaya",
        ],
        "animals": [
            "lion",
            "tiger",
            "elephant",
            "giraffe",
            "monkey",
            "zebra",
            "bear",
            "wolf",
            "fox",
            "deer",
            "kangaroo",
            "penguin",
            "dolphin",
            "shark",
            "eagle",
        ],
        "vehicles": [
            "car",
            "bus",
            "truck",
            "motorcycle",
            "bicycle",
            "train",
            "airplane",
            "helicopter",
            "ship",
            "submarine",
            "tractor",
            "ambulance",
        ],
        "countries": [
            "ethiopia",
            "kenya",
            "egypt",
            "nigeria",
            "ghana",
            "south africa",
            "morocco",
            "algeria",
            "tanzania",
            "uganda",
            "somalia",
        ],
    }

    questions = []
    for _ in range(count):
        # Pick 2–3 categories to mix
        selected_cats = random.sample(list(categories.keys()), random.randint(2, 3))
        pool = []
        for cat in selected_cats:
            pool.extend(categories[cat])

        size = random.randint(8, 14)
        selected_items = random.sample(pool, size)
        random.shuffle(selected_items)

        # For simplicity: correct answer = alphabetical across all
        # Real version should store JSON { "Fruits": [...], "Animals": [...] }
        q = Question(
            type="categories",
            question="Sort these items alphabetically (mixed categories)",
            items=",".join(selected_items),
            answer=",".join(sorted(selected_items)),
            # Later: metadata=json.dumps({"categories": selected_cats})
        )
        questions.append(q)
    return questions


def main(target_total: int = 1500):
    with app.app_context():
        existing = Question.query.count()
        print(f"Current questions in database: {existing}")

        if existing >= target_total:
            print("Target already reached. Nothing to do.")
            return

        needed = target_total - existing
        print(f"Need to generate ≈ {needed} more questions...\n")

        batches = [
            generate_number_questions(450, asc=True),
            generate_number_questions(300, asc=False),
            generate_letter_questions(400, asc=True),
            generate_letter_questions(250, asc=False),
            generate_color_questions(300),
            generate_category_questions(350),
        ]

        all_new = []
        for batch in batches:
            all_new.extend(batch)

        # Shuffle globally so types are nicely mixed
        random.shuffle(all_new)

        # Take only what we need
        to_add = all_new[:needed]

        if to_add:
            db.session.bulk_save_objects(to_add)
            db.session.commit()
            print(f"Successfully added {len(to_add)} new questions.")
        else:
            print("No new questions needed after shuffling.")

        final_count = Question.query.count()
        print(f"Final total: {final_count} questions")


if __name__ == "__main__":
    main(target_total=1800)  # ← change this number to whatever you want
