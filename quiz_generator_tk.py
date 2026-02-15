#!/usr/bin/env python3
"""
quiz_generator_tk.py

Tkinter GUI to generate quizzes from pasted text.

Features:
- Paste raw content containing MCQs (or full quiz text).
- Parser modes: AI-assisted (OpenAI) or local heuristic.
- Preview parsed questions and export to JS or JSON using the same shape as the site expects.

AI mode: set environment variable `OPENAI_API_KEY` and choose 'AI' mode. The app will attempt
to use the `openai` package. If not available or no key provided, AI mode will warn and fall back.

Heuristic mode: a best-effort parser that looks for question lines (lines ending with '?', lines
starting with 'Q', or numbered lists) and collects following option lines (lettered or prefixed).

This is a convenience tool; manually review the preview before exporting.
"""
import os
import json
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import openai
except Exception:
    openai = None


def heuristic_parse(text):
    """Return a list of question dicts parsed heuristically from raw text.

    Behavior:
    - Detect numbered questions like "1 Question..." or "1. Question" or lines starting with a number.
    - Collect following lettered options (A/B/C/D), or lines starting with A., A) or just 'A ' + text.
    - Handle inline option separators (||, |, ;) when present.
    - Detect trailing correctness markers (A-D) in options and set `correct` index.
    """
    raw_lines = [l.rstrip() for l in text.splitlines()]
    lines = raw_lines
    questions = []
    i = 0
    n = len(lines)

    def clean_option_text(s):
        s = s.strip()
        s = re.sub(r"^[A-Za-z]\s*[\)\.\-:]\s*", "", s)
        s = re.sub(r"^[\-•]\s*", "", s)
        return s.strip()

    while i < n:
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Detect question start
        qtext = None
        # numbered like '1. Question' or '1 Question'
        mnum = re.match(r"^\s*(\d+)\s*[\).\-:]?\s*(.*)$", line)
        if mnum and (line.endswith('?') or '?' in line or len(mnum.group(2))>0):
            num = mnum.group(1)
            after = mnum.group(2).strip()
            # Reconstruct with number: "1. Question..."
            qtext = num + '. ' + after if after else line
            i += 1
        elif line.lower().startswith('q') and '?' in line:
            qtext = line
            i += 1
        elif line.endswith('?') or '........' in line or line.lower().startswith('question'):
            qtext = line
            i += 1
        else:
            # peek ahead for options - if present, treat this line as question
            j = i + 1
            opts_found = False
            while j < min(n, i + 6):
                if re.match(r'^[A-Da-d][\)\.\-: ]', lines[j].strip()) or re.match(r'^[\-•]\s+', lines[j].strip()):
                    opts_found = True
                    break
                j += 1
            if opts_found:
                qtext = line
                i += 1
            else:
                i += 1
                continue

        # collect options
        opts = []
        pending_correct_letter = None
        while i < n:
            s = lines[i].strip()
            if not s:
                i += 1
                break
            # single-letter line 'A' or 'B' etc -> correctness marker
            m_single = re.match(r'^([A-Da-d])[\.)]?$' , s)
            if m_single and len(s.strip()) <= 3:
                letter = m_single.group(1).upper()
                if opts:
                    correct_idx = ord(letter) - 65
                    if 0 <= correct_idx < len(opts):
                        # mark by replacing later - we set a variable here
                        pending_correct_letter = letter
                else:
                    # no options collected yet; remember and apply after options collected
                    pending_correct_letter = letter
                i += 1
                continue
            # next question detection
            if re.match(r'^\s*\d+\s*[\).\-:]?\s*', s) and (s.endswith('?') or len(s.split())>2):
                break
            if re.match(r'^[A-Da-d][\)\.\-: ]', s) or re.match(r'^[\-•]\s+', s):
                cleaned = clean_option_text(s)
                if cleaned:
                    opts.append(cleaned)
                i += 1
                continue
            if '||' in s or ('|' in s and s.count('|')>1) or ';' in s:
                parts = re.split(r"\|\||\||;", s)
                for p in parts:
                    p = p.strip()
                    if p:
                        opts.append(clean_option_text(p))
                i += 1
                continue
            if ',' in s and len(s) < 120 and len(opts) == 0:
                parts = [p.strip() for p in s.split(',') if p.strip()]
                if len(parts) >= 2:
                    for p in parts:
                        opts.append(clean_option_text(p))
                    i += 1
                    continue
            # short line starting with capital could be an option
            if re.match(r'^[A-Z][a-z].{0,120}$', s) and len(s.split()) <= 8 and len(opts) < 6:
                opts.append(clean_option_text(s))
                i += 1
                continue
            break

        # detect trailing single-letter correctness markers
        correct_index = None
        for idx, o in enumerate(opts):
            m = re.search(r"(?:\(|\[)?\b([A-D])\b(?:\)|\])?[\.]?$", o)
            if m:
                new_o = re.sub(r"(?:\(|\[)?\b([A-D])\b(?:\)|\])?[\.]?$", '', o).strip()
                if new_o:
                    opts[idx] = new_o
                else:
                    opts[idx] = o.strip()
                if correct_index is None:
                    correct_index = idx

        # if we encountered a standalone letter line, apply it now
        if correct_index is None and pending_correct_letter is not None:
            ci = ord(pending_correct_letter) - 65
            if 0 <= ci < len(opts):
                correct_index = ci

        questions.append({'text': qtext.strip(), 'options': opts, 'correct': correct_index, 'explanation': ''})

    return questions


def ai_parse(text, model='gpt-3.5-turbo'):
    """Use OpenAI to extract MCQs into the standard quiz format.

    Returns a list of question dicts with keys: text, options, correct (None), explanation.
    """
    if openai is None:
        raise RuntimeError('openai package not installed')
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not set')
    openai.api_key = api_key

    prompt = (
        "Extract multiple-choice questions from the following text.\n"
        "Return only valid JSON: an array of objects like {\"text\":..., \"options\":[...], \"correct\": null, \"explanation\": \"\"}.\n"
        "If you cannot find choices for a question, set \"options\" to an empty array.\n\n"
        "Text:\n" + text
    )

    # Use ChatCompletion but tolerate different OpenAI client versions
    try:
        resp = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': prompt}], temperature=0.0)
        content = resp.choices[0].message.content
    except AttributeError:
        # fallback to older Completion API
        resp = openai.Completion.create(engine=model, prompt=prompt, max_tokens=1500, temperature=0.0)
        content = resp.choices[0].text

    # extract JSON array from response
    start = content.find('[')
    end = content.rfind(']')
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError('AI response did not contain a JSON array:\n' + content)
    json_text = content[start:end+1]
    try:
        data = json.loads(json_text)
    except Exception as e:
        raise RuntimeError('Failed to parse JSON from AI response: ' + str(e) + '\n' + content)

    out = []
    for it in data:
        out.append({'text': it.get('text','').strip(), 'options': it.get('options',[]), 'correct': it.get('correct'), 'explanation': it.get('explanation','')})
    return out


def dump_js(quizzes, out_path, func_name='getGeneratedQuizzes'):
    js = f"function {func_name}() {{\n  return " + json.dumps(quizzes, ensure_ascii=False, indent=2) + ";\n}\n"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(js)


class App:
    def __init__(self, root):
        self.root = root
        root.title('Quiz Generator (GUI)')
        frm = ttk.Frame(root, padding=10)
        frm.grid(sticky='nsew')

        # text input
        ttk.Label(frm, text='Paste raw quiz text here:').grid(row=0, column=0, sticky='w')
        self.text = tk.Text(frm, width=90, height=18)
        self.text.grid(row=1, column=0, columnspan=4, sticky='nsew', pady=6)

        # parser mode
        ttk.Label(frm, text='Parser:').grid(row=2, column=0, sticky='w')
        self.mode = tk.StringVar(value='heuristic')
        ttk.Radiobutton(frm, text='Heuristic', variable=self.mode, value='heuristic').grid(row=2, column=1)
        ttk.Radiobutton(frm, text='AI (OpenAI)', variable=self.mode, value='ai').grid(row=2, column=2)

        # metadata
        ttk.Label(frm, text='Quiz ID:').grid(row=3, column=0, sticky='e')
        self.quiz_id = ttk.Entry(frm); self.quiz_id.grid(row=3, column=1, sticky='w')
        ttk.Label(frm, text='Subject:').grid(row=3, column=2, sticky='e')
        self.subject = ttk.Entry(frm); self.subject.grid(row=3, column=3, sticky='w')
        ttk.Label(frm, text='Unit:').grid(row=4, column=0, sticky='e')
        self.unit = ttk.Entry(frm, width=6); self.unit.grid(row=4, column=1, sticky='w')
        ttk.Label(frm, text='Cycle:').grid(row=4, column=2, sticky='e')
        self.cycle = ttk.Combobox(frm, values=['chemistry','physics','general']); self.cycle.grid(row=4, column=3, sticky='w')

        # buttons
        ttk.Button(frm, text='Parse / Preview', command=self.parse_preview).grid(row=5, column=0, pady=8)
        ttk.Button(frm, text='Export JS', command=self.export_js).grid(row=5, column=1)
        ttk.Button(frm, text='Export JSON', command=self.export_json).grid(row=5, column=2)
        ttk.Button(frm, text='Clear', command=lambda: self.text.delete('1.0','end')).grid(row=5, column=3)

        # preview area
        ttk.Label(frm, text='Preview (parsed questions):').grid(row=6, column=0, sticky='w')
        self.preview = tk.Text(frm, width=90, height=12, state='disabled')
        self.preview.grid(row=7, column=0, columnspan=4, pady=6)

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.parsed = []

    def parse_preview(self):
        raw = self.text.get('1.0', 'end').strip()
        if not raw:
            messagebox.showinfo('Empty', 'Please paste text to parse.')
            return
        mode = self.mode.get()
        try:
            if mode == 'ai':
                try:
                    parsed = ai_parse(raw)
                except Exception as e:
                    messagebox.showwarning('AI error', str(e) + '\nFalling back to heuristic.')
                    parsed = heuristic_parse(raw)
            else:
                parsed = heuristic_parse(raw)
        except Exception as e:
            messagebox.showerror('Parse error', str(e))
            return

        self.parsed = parsed
        self._update_preview()

    def _update_preview(self):
        self.preview.configure(state='normal')
        self.preview.delete('1.0', 'end')
        for i, q in enumerate(self.parsed, start=1):
            self.preview.insert('end', f"{i}. {q['text']}\n")
            for j, o in enumerate(q.get('options', [])):
                self.preview.insert('end', f"   {chr(65+j)}. {o}\n")
            self.preview.insert('end', '\n')
        self.preview.configure(state='disabled')

    def _build_quiz_object(self):
        qid = self.quiz_id.get().strip() or 'gen-1'
        subj = self.subject.get().strip() or 'General'
        unit_raw = self.unit.get().strip()
        try:
            unit = int(unit_raw) if unit_raw != '' else None
        except Exception:
            unit = None
        cycle = self.cycle.get().strip() or None

        quiz = {
            'id': qid,
            'subject': subj,
            'name': self.quiz_id.get().strip() or qid,
            'questions': []
        }
        if unit is not None:
            quiz['unit'] = unit
        if cycle:
            quiz['cycle'] = cycle

        for q in self.parsed:
            # question shape: text, options, correct (index or None), explanation
            quiz['questions'].append({'text': q.get('text',''), 'options': q.get('options',[]), 'correct': q.get('correct'), 'explanation': q.get('explanation','')})
        return [quiz]

    def export_js(self):
        if not self.parsed:
            messagebox.showinfo('Nothing to export', 'Parse some questions first.')
            return
        out = filedialog.asksaveasfilename(defaultextension='.js', filetypes=[('JavaScript', '*.js')])
        if not out:
            return
        quizzes = self._build_quiz_object()
        dump_js(quizzes, out)
        messagebox.showinfo('Saved', f'Wrote {len(quizzes)} quiz to {out}')

    def export_json(self):
        if not self.parsed:
            messagebox.showinfo('Nothing to export', 'Parse some questions first.')
            return
        out = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')])
        if not out:
            return
        quizzes = self._build_quiz_object()
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(quizzes, f, ensure_ascii=False, indent=2)
        messagebox.showinfo('Saved', f'Wrote {len(quizzes)} quiz to {out}')


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
