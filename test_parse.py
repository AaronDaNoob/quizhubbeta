from quiz_generator_tk import heuristic_parse
import json

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
