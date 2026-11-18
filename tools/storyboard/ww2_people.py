"""The cast of sb-ww2-both-sides: drawn presets for every kind of person in the story (ww2_fix.py, ww2_talk.py)."""
SUIT = {'coat': '#2e3440', 'coat2': '#e8e2d4', 'trim': '#6a6458'}
PEOPLE = {
 'WPH':   ('civilian', dict(SUIT, hair='#2a1d12')),                                   # William Patrick Hitler, in a 1930s suit
 'BOY':   ('civilian', {'coat': '#4a4a52', 'hair': '#3b2a1a'}),                      # William as a boy
 'WPHN':  ('us_sailor', {'hair': '#2a1d12'}),                                         # William in the US Navy
 'BRID':  ('woman', {'hair': '#6a3a1e', 'coat': '#3a4a5a'}),                          # Bridget Dowling
 'ALO':   ('civilian', {'coat': '#4a3a2a', 'beard': 'mustache', 'hair': '#3b2a1a'}), # Alois Hitler Jr.
 'AH':    ('hitler', {}),
 'EVA':   ('woman', {'hair': '#d8b86a', 'coat': '#2a2a3a'}),
 'GEROFF': ('us_officer', {'coat': '#5a5e5a', 'coat2': '#454a45', 'hatCol': '#454a45', 'trim': '#b8b8b8'}),   # German officer, field grey
 'GERSOL': ('worker', {'coat': '#5a5e5a', 'hat': 'helmet', 'hatCol': '#4a4e4a'}),                          # German soldier
 'GERCIV': ('clerk', {'coat': '#3a3a3a'}),                                                                   # German official / clerk
 'POLICE': ('civilian', {'coat': '#2f4a3a', 'hat': 'kepi', 'hatCol': '#2f4a3a'}),
 'POLIT':  ('civilian', {'coat': '#1e1e24', 'hat': 'tophat', 'hatCol': '#111', 'hair': '#9a9488'}),         # 1930s politician
 'BRITOFF': ('us_officer', {'coat': '#7a6a45', 'coat2': '#5f5235', 'hatCol': '#5f5235', 'trim': '#b3202a'}),  # British army officer
 'TOMMY': ('worker', {'coat': '#7a6a45', 'hat': 'helmet', 'hatCol': '#5f5a3a'}),
 'RAF':   ('civilian', {'coat': '#4a5a7a', 'coat2': '#d8d2c4', 'hair': '#5a3a22'}),
 'CHAM':  ('civilian', {'coat': '#1e1e24', 'hair': '#c8c2b8', 'beard': 'mustache'}),
 'FDR':   ('civilian', {'coat': '#2e3440', 'hair': '#9a9488', 'glasses': 1}),
 'USOFF': ('us_officer', {'coat': '#6b6448', 'coat2': '#55503a', 'hatCol': '#55503a'}),
 'USCLK': ('clerk', {'coat': '#3a3f4a'}),
 'SAILOR': ('us_sailor', {}),
 'GI':    ('worker', {'coat': '#6b6448', 'hat': 'helmet', 'hatCol': '#55603a'}),
 'POLE':  ('worker', {'coat': '#6a6a4a', 'hat': 'helmet', 'hatCol': '#5a5a3a'}),
 'POLCIV': ('clerk', {'coat': '#3b3a3f'}),
 'SOV':   ('soviet_officer', {}),
 'SOVSOL': ('worker', {'coat': '#5a6b3a', 'hat': 'helmet', 'hatCol': '#4a5a2e'}),
 'JPOFF': ('us_officer', {'coat': '#6b6a3a', 'coat2': '#5a5a30', 'hatCol': '#5a5a30', 'trim': '#c8102e', 'hair': '#1a1a1a', 'skin': '#e8c49a'}),
 'JPADM': ('rn_officer', {'hat': 'kepi', 'hatCol': '#111', 'hair': '#1a1a1a', 'skin': '#e8c49a'}),
 'JPCIV': ('clerk', {'hair': '#1a1a1a', 'skin': '#e8c49a', 'coat': '#2a2a30'}),
 'HIRO':  ('clerk', {'hair': '#1a1a1a', 'skin': '#e8c49a', 'coat': '#3a3a2a', 'beard': 'mustache'}),
 'COOK':  ('worker', {'coat': '#e8e2d4', 'coat2': '#e8e2d4'}),
 'LIV':   ('worker', {}),
 'LIVW':  ('woman', {'hair': '#3a2416', 'coat': '#5a4a3a'}),
 'CIV':   ('civilian', {}),
}
def who(code, **k):
    p, sp = PEOPLE[code]; extra = k.pop('spec', {}); q = dict(preset=p, **k)
    if sp or extra: q['spec'] = dict(sp, **extra)
    return q

