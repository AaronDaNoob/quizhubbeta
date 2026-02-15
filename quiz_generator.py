"""
quiz_generator.py

Simple CLI to generate JavaScript quiz arrays compatible with the site's format.

Usage examples:
  # Convert a CSV to a JS file
  python quiz_generator.py --csv QUIZ_TEMPLATE.csv --out generated_quizzes.js

CSV format (header):
  quiz_id,subject,unit,name,cycle,difficulty,question_text,options,correct,explanation

- `quiz_id` groups questions into a quiz. All rows with same quiz_id belong to one quiz.
- `options` should be separated with the pipe symbol `||`.
- `correct` should be the index of the correct option (0-based) or the exact option text.

Output: a JS file exporting a function `getGeneratedQuizzes()` that returns an array of quiz objects.
Each quiz object includes at minimum: id, subject, unit (int), name, questions (array).
Each question object has: text, options (array), correct (index int), explanation.

"""
import argparse
import csv
import json
import sys
from collections import OrderedDict


def parse_csv(path):
    quizzes = OrderedDict()
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            qid = (row.get('quiz_id') or '').strip()
            if not qid:
                print(f"Skipping row {i}: missing quiz_id", file=sys.stderr)
                continue
            subject = (row.get('subject') or '').strip() or 'General'
            unit_raw = (row.get('unit') or '').strip()
            try:
                unit = int(unit_raw) if unit_raw != '' else None
            except ValueError:
                unit = None
            name = (row.get('name') or '').strip() or qid
            cycle = (row.get('cycle') or '').strip() or None
            difficulty = (row.get('difficulty') or '').strip() or None

            qtext = (row.get('question_text') or '').strip()
            options_raw = (row.get('options') or '').strip()
            options = [opt.strip() for opt in options_raw.split('||')] if options_raw else []
            correct_raw = (row.get('correct') or '').strip()
            explanation = (row.get('explanation') or '').strip() or ''

            # determine correct index
            correct_index = None
            if correct_raw != '':
                if correct_raw.isdigit():
                    try:
                        idx = int(correct_raw)
                        if 0 <= idx < len(options):
                            correct_index = idx
                    except Exception:
                        correct_index = None
                else:
                    # try to match option text
                    for idx, opt in enumerate(options):
                        if opt.strip().lower() == correct_raw.strip().lower():
                            correct_index = idx
                            break
            # fallback: 0
            if correct_index is None and options:
                correct_index = 0

            question_obj = {
                'text': qtext,
                'options': options,
                'correct': correct_index,
                'explanation': explanation
            }

            if qid not in quizzes:
                quizzes[qid] = {
                    'id': qid,
                    'subject': subject,
                    'unit': unit,
                    'name': name,
                    'cycle': cycle,
                    'difficulty': difficulty,
                    'questions': []
                }
            quizzes[qid]['questions'].append(question_obj)

    # Clean up None fields to match existing site's shape
    out = []
    for q in quizzes.values():
        obj = {k: v for k, v in q.items() if v is not None}
        out.append(obj)
    return out


def dump_as_js(quizzes, out_path, func_name='getGeneratedQuizzes'):
    # JSON -> JS function that returns the array
    js = f"function {func_name}() {{\n  return " + json.dumps(quizzes, ensure_ascii=False, indent=2) + ";\n}\n"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f"Wrote {len(quizzes)} quizzes to {out_path}")


def dump_as_json(quizzes, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(quizzes, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(quizzes)} quizzes to {out_path}")


def main():
    p = argparse.ArgumentParser(description='Generate JS/JSON quiz arrays for the Quiz Hub site')
    p.add_argument('--csv', help='Input CSV file (see header format in script doc)')
    p.add_argument('--out', default='generated_quizzes.js', help='Output file path')
    p.add_argument('--format', choices=['js','json'], default='js', help='Output format')
    p.add_argument('--func', default='getGeneratedQuizzes', help='If JS, function name to export')
    # Accept and ignore unknown args (debugger/launcher may inject flags)
    args, _unknown = p.parse_known_args()

    if not args.csv:
        p.print_help()
        # don't raise SystemExit in interactive/debugger sessions
        return

    # validate input file early and show friendly message
    try:
        open(args.csv, 'r', encoding='utf-8').close()
    except FileNotFoundError:
        print(f"Error: CSV file not found: {args.csv}", file=sys.stderr)
        return

    quizzes = parse_csv(args.csv)
    if args.format == 'js':
        dump_as_js(quizzes, args.out, func_name=args.func)
    else:
        dump_as_json(quizzes, args.out)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        # prevent debugger / interactive sessions from showing a non-zero exit
        pass
    except Exception:
        import traceback
        traceback.print_exc()
        # avoid forcing a non-zero exit when running under debuggers/launchers
        # so the VS Code Python debug console doesn't show Exit Code 1
        pass
