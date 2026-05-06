import json
import pandas as pd
import re

# === CHANCE ===
with open('../data/raw/chance_all_responses_identifiable.json') as f:
    data = json.load(f)

rows = []
seen = set()

def get_condition(exp):
    # graded condition from video filename (game_intro_pt1_XX.mp4)
    for k, v in exp.items():
        if isinstance(v, dict):
            video = v.get('videoShown', '')
            if 'game_intro_pt' in video:
                match = re.search(r'_(\d+)\.mp4', video)
                if match:
                    return match.group(1)
    return 'NA'

def get_counterbalancing(exp):
    for k, v in exp.items():
        if isinstance(v, dict):
            audio = v.get('audioPlayed', '')
            if '_flipped' in audio:
                return 'flipped'
    return 'not_flipped'

def get_attention_check(exp):
    for k in exp:
        if 'control-question' in k:
            events = exp[k].get('eventTimings', [])
            for e in events:
                if e.get('eventType') == 'exp-lookit-images-audio:clickImage':
                    sel = e.get('imageId', '')
                    if sel == 'star': return 'correct'
                    elif sel == 'dash': return 'incorrect'
    return 'NA'

def get_prediction(exp):
    for k, v in exp.items():
        if 'prediction-question' in k:
            sel = v.get('selectedImage', '')
            if sel == 'three_stars': return 3
            elif sel == 'two_stars': return 2
            elif sel == 'one_star': return 1
            elif sel == 'all_dash': return 0
    return 'NA'

def get_surprise_binary(exp):
    for k, v in exp.items():
        if 'surprise-rating-yes-no' in k:
            return v.get('selectedImage', 'NA')
    return 'NA'

def get_surprise_graded(exp, binary):
    if binary == 'not_surprised': return 'not_surprised'
    for k, v in exp.items():
        if 'surprise-rating-graded' in k:
            sel = v.get('selectedImage', '')
            if sel in {'a_little_surprised', 'pretty_surprised', 'very_surprised'}:
                return sel
    return 'NA'

for e in data:
    try:
        child = e['child']
        hid = child['hashed_id']
        if hid in seen: continue
        resp = e['response']
        exp = e['exp_data']
        binary = get_surprise_binary(exp)

        rows.append({
            'uuid': resp['uuid'],
            'child_hashed_id': hid,
            'parent_hashed_id': e['participant']['hashed_id'],
            'response_date_created': str(resp['date_created']),
            'completed': resp['completed'],
            'age_in_days': child['age_in_days'],
            'age_years': round(float(child['age_in_days'])/365.25, 2),
            'child_age': child['age_rounded'],
            'child_gender': child['gender'],
            'condition': get_condition(exp),
            'counterbalancing': get_counterbalancing(exp),
            'attention_check_1': get_attention_check(exp),
            'prediction': get_prediction(exp),
            'surprise_binary': binary,
            'surprise_likert': get_surprise_graded(exp, binary)
        })
        seen.add(hid)
    except: continue

df = pd.DataFrame(rows)
df.to_csv('../data/chance_data.csv', index=False)
print(f'CHANCE: {len(df)} rows')
print(f'  Condition: {df["condition"].value_counts().to_dict()}')
print(f'  Counterbalancing: {df["counterbalancing"].value_counts().to_dict()}')


# === MEMORY ===
with open('../data/raw/memory_all_responses_identifiable.json') as f:
    data = json.load(f)

rows = []
seen = set()
star_cards = {'47', '26', '13'}

def get_condition_mem(exp, seq):
    seq_str = ' '.join(seq)
    if '-surprising' in seq_str and '-unsurprising' not in seq_str:
        return 'surprising'
    elif '-unsurprising' in seq_str:
        return 'unsurprising'
    return 'NA'

def get_card_choices(exp):
    choices = {1: 'NA', 2: 'NA', 3: 'NA'}
    for k, v in exp.items():
        if 'select-1' in k and 'combined' not in k:
            choices[1] = v.get('selectedImage', 'NA')
        elif 'select-2' in k and 'combined' not in k:
            choices[2] = v.get('selectedImage', 'NA')
        elif 'select-3' in k and 'combined' not in k:
            choices[3] = v.get('selectedImage', 'NA')
    return choices[1], choices[2], choices[3]

def count_star_cards(c1, c2, c3):
    choices = {str(c1), str(c2), str(c3)}
    choices.discard('NA')
    return len(choices.intersection(star_cards))

def card_to_pos(cid):
    try:
        cid = int(cid)
        if 1 <= cid <= 50:
            return (cid-1)//10, (cid-1)%10
    except: pass
    return None

def dist_to_marked(cid):
    pos = card_to_pos(cid)
    if not pos: return 'NA'
    dists = []
    for m in star_cards:
        mp = card_to_pos(m)
        if mp:
            dists.append(abs(pos[0]-mp[0]) + abs(pos[1]-mp[1]))
    return min(dists) if dists else 'NA'

for e in data:
    try:
        child = e['child']
        hid = child['hashed_id']
        if hid in seen: continue
        resp = e['response']
        exp = e['exp_data']
        seq = resp.get('sequence', [])
        c1, c2, c3 = get_card_choices(exp)
        binary = get_surprise_binary(exp)

        rows.append({
            'uuid': resp['uuid'],
            'child_hashed_id': hid,
            'parent_hashed_id': e['participant']['hashed_id'],
            'response_date_created': str(resp['date_created']),
            'is_preview': resp.get('is_preview', False),
            'completed': resp['completed'],
            'age_in_days': child['age_in_days'],
            'age_years': round(float(child['age_in_days'])/365.25, 2),
            'child_age': child['age_rounded'],
            'child_gender': child['gender'],
            'condition': get_condition_mem(exp, seq),
            'counterbalancing': get_counterbalancing(exp),
            'attention_check': get_attention_check(exp),
            'first_choice': c1,
            'first_choice_dist': dist_to_marked(c1),
            'second_choice': c2,
            'second_choice_dist': dist_to_marked(c2),
            'third_choice': c3,
            'third_choice_dist': dist_to_marked(c3),
            'n_star_cards_selected': count_star_cards(c1, c2, c3),
            'prediction': get_prediction(exp),
            'surprise_binary': binary,
            'surprise_likert': get_surprise_graded(exp, binary)
        })
        seen.add(hid)
    except: continue

df = pd.DataFrame(rows)
df.to_csv('../data/memory_data.csv', index=False)
print(f'MEMORY: {len(df)} rows')
print(f'  Condition: {df["condition"].value_counts().to_dict()}')
print(f'  Counterbalancing: {df["counterbalancing"].value_counts().to_dict()}')
