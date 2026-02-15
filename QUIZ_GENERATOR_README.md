Quiz Generator
===============

This small Python CLI converts a CSV of quiz questions into a JavaScript function or JSON file that you can paste into `index4.html` or load into the site.

CSV columns (header row required):
- `quiz_id` : groups rows into quizzes (all rows with same id belong to one quiz)
- `subject` : e.g., Chemistry, Physics
- `unit` : integer unit number (optional)
- `name` : quiz display name
- `cycle` : e.g., chemistry or physics (optional)
- `difficulty` : optional
- `question_text` : the full question text
- `options` : answer choices separated by `||` (double pipe)
- `correct` : either the 0-based index of the correct option or the exact option text
- `explanation` : optional explanation shown after answering

Example CSV row:

chem-u1-1,Chemistry,1,Unit 1 - Example,chemistry,medium,What is pH?,7||6||8,0,Pure water has pH 7

Usage:

```bash
python quiz_generator.py --csv QUIZ_TEMPLATE.csv --out generated_quizzes.js --format js
```

The resulting `generated_quizzes.js` will contain a function `getGeneratedQuizzes()` that returns an array of quiz objects with fields matching the site's format.

Integration:
- Open `enhanced/index4.html` and add the output contents directly into the script area, or include the generated JS file via a `<script>` tag and call `getGeneratedQuizzes()` from your `init()` to merge with `allQuizzes`.

Example integration snippet (in JS):

```js
// after loading generated_quizzes.js
allQuizzes = [...getGeneratedQuizzes(), ...allQuizzes];
allQuizzes.forEach(q => { if (!q.cycle) q.cycle = 'chemistry'; });
renderFilters();
renderQuizzes();
```

License: use as you like.
