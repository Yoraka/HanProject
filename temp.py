import re
text = '通“奠”。祭奠。*清**段玉裁*《説文解字注·尸部》：“㞟，《太玄》假為天地奠位之奠。”按：今本《太玄·玄攡》作“天地奠位”。'
# Correct the regular expression to accurately handle cases with and without pinyin
pattern_correct_optional_pinyin = r'通“([^”]*?)(?:\（([^）]*)\）)?”。([^。]*。)'

# Use re.findall to accurately extract matches, now correctly handling optional pinyin
correct_all_matches_optional_pinyin = re.findall(pattern_correct_optional_pinyin, text)

# Prepare a more accurate result that includes the term, its pinyin (if provided), and the explanation
results_with_optional_pinyin = [{"term": match[0], "pinyin": match[1] if match[1] else "None", "explanation": match[2]} for match in correct_all_matches_optional_pinyin]

for result in results_with_optional_pinyin:
    # 检查每个结果的'explanation'字段是否存在特定字符
    if "《" in result['explanation'] or "》" in result['explanation'] or "*" in result['explanation']:
        # 如果存在，则将'explanation'设置为空字符串
        result['explanation'] = None
# Print the results
for result in results_with_optional_pinyin:
    if result['explanation'] is not None:
        print(result)
    else:
        print('None')
print(results_with_optional_pinyin)