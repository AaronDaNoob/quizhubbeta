from quiz_generator_tk import heuristic_parse

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

quiz = {
    'id': 'chem-u1',
    'subject': 'Chemistry',
    'unit': 1,
    'name': 'Unit 1 - Electrode & Energy Systems',
    'questions': parsed
}

# build JS text matching the exact style requested
lines = []
lines.append('{')
lines.append('  id: "' + quiz['id'] + '",')
lines.append('  subject: "' + quiz['subject'] + '",')
lines.append('  unit: ' + str(quiz['unit']) + ',')
lines.append('  name: "' + quiz['name'] + '",')
lines.append('  questions: [')

q_lines = []
for q in quiz['questions']:
    parts = []
    parts.append('{"text":"' + q['text'].replace('"','\\"') + '"')
    # options array
    opts = '[' + ','.join('"' + o.replace('"','\\"') + '"' for o in q.get('options',[])) + ']'
    parts.append('"options":' + opts)
    # correct
    c = q.get('correct')
    if c is None:
        parts.append('"correct":null')
    else:
        parts.append('"correct":' + str(c))
    # explanation if present and non-empty
    expl = q.get('explanation','')
    if expl:
        parts.append('"explanation":"' + expl.replace('"','\\"') + '"')
    q_lines.append('    {' + ','.join(parts) + '},')

# remove trailing comma on last question if desired - but example keeps commas between objects
if q_lines:
    # keep as-is
    pass

lines.extend(q_lines)
lines.append('  ]')
lines.append('},')

out_text = '\n'.join(lines) + '\n'

out_path = 'c:/Users/Hp/Documents/coding/enhanced/generated_quiz_output.js'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(out_text)

print('Wrote:', out_path)
