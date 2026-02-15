#!/usr/bin/env python3
"""
parser_standalone.py - Heuristic quiz parser without Tk/GUI dependencies
"""
import re
import json


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
        # remove leading letter+punctuation like "A) " or "A. " or "A: " or "A "
        s = re.sub(r"^[A-Za-z]\s*[\)\.\-:]\s*", "", s)
        # also try simple letter+space if no punctuation
        if re.match(r'^[A-D]\s+', s):
            s = re.sub(r'^[A-D]\s+', "", s)
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
                # remember the marker
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


if __name__ == '__main__':
    sample = '''1 Which of the following is not a feature of a village?
A Less population
B Less diversity
C Impersonal relationship
D Predominance of primary sector and allied activities
2 Which among the following is not a form of diversity in India?
A Geographical diversity
B Linguistic diversity D
C Religious diversity
D None of the above
3 Caste is not a/an ........................
A Endogamous system
D
B Hereditary system
C Hierarchical system
D Exogamous system
4 Marriage of one man with several sisters is called ......................
A Monogamous marriage
'''
    parsed = heuristic_parse(sample)
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
