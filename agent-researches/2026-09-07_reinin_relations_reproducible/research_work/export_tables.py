"""Export exact tables and expand report placeholders, if a draft is present."""
from pathlib import Path
from collections import Counter
import json,csv,re,hashlib
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'normalized_data.json').read_text())
C=json.loads((ROOT/'catalogue.json').read_text())
AU=json.loads((ROOT/'source_audit.json').read_text())
V=json.loads((ROOT/'verification_results.json').read_text())
T={x:t for t,x in D['code'].items()}
names={h:n for n,h in D['trait_masks'].items()}
names[14]='Процесс (правые)'
parts=C['parts']; OUT=ROOT/'tables'; OUT.mkdir(exist_ok=True)
def table(headers,rows):
    def s(v):return str(v).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(map(s,headers))+' |','| '+' | '.join([':--']*len(headers))+' |']+['| '+' | '.join(map(s,r))+' |' for r in rows])+'\n'
def writecsv(name,headers,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(headers);w.writerows(rows)
def bits(x,n=4):return ''.join(str((x>>i)&1) for i in range(n))
def lin(h):return '+'.join(n for i,n in enumerate(['e','r','n','l']) if h>>i&1) or '0'
def setstr(xs):return '{'+', '.join(map(str,xs))+'}'
def formula(cl):
    if cl['kind']=='subset':return 'M'+setstr(cl['A'])+' ⊆ '+setstr(cl['F'])
    aa=['('+', '.join(s)+')' for s in cl['A']]
    ff=['('+', '.join(map(str,s))+')' for s in cl['F']]
    if cl['kind']=='partition':return 'M{'+', '.join(aa)+'} = {'+', '.join(ff)+'}'
    return 'M['+' > '.join(aa)+'] = ['+' > '.join(ff)+'] (цикл)'
def conjunction(block):return '; и '.join(formula(cl) for cl in block['clauses'])
def cycles(pp):
    seen=set();out=[]
    for i in range(len(pp)):
        if i in seen:continue
        c=[];j=i
        while j not in seen:seen.add(j);c.append(j+1);j=pp[j]
        if len(c)>1:out.append('('+ ' '.join(map(str,c))+')')
    return ' '.join(out) or '1'
rel={0:'Тождество',1:'Погашение',2:'Квазитождество',3:'Зеркало',4:'Деловые',5:'Полудуальность',6:'Подзаказный → заказчик',7:'Ревизор → подревизный',8:'Родственные',9:'Мираж',10:'Заказчик → подзаказный',11:'Подревизный → ревизор',12:'Суперэго',13:'Дуальность',14:'Активация',15:'Конфликт'}

traits=[[h,names[h],lin(h),'3' if h in [1,2,3] else ('8' if 4<=h<=11 else ('4' if h else 'постоянный'))] for h in range(16)]
writecsv('trait_dictionary.csv',['mask','positive_name','negative_linear_form','class'],traits)
models=[[i,T[i]]+D['models'][T[i]] for i in range(16)]
writecsv('models.csv',['code','type']+list(range(1,9)),models)
writecsv('reinin.csv',['type']+D['traits_header'],[[T[x]]+D['bits'][T[x]] for x in range(16)])
dictionary=[[x,T[x],bits(x),cycles(D['permutations'][str(x)]),D['orders'][str(x)],rel[x]] for x in range(16)]
writecsv('operator_dictionary.csv',['code','type','ernl_bits','permutation_cycles','order','relation_from_ILE'],dictionary)
writecsv('cayley.csv',['left/right']+list(range(16)),[[i]+D['cayley'][i] for i in range(16)])
writecsv('relative_operators.csv',['source/target']+[T[i] for i in range(16)],[[T[i]]+[D['cayley'][j][D['inverse'][str(i)]] for j in range(16)] for i in range(16)])
writecsv('partitions.csv',['id','direction_codes','dual_masks','group_type','L_invariant','R_invariant'],[[p['id'],' '.join(map(str,p['direction'])),' '.join(map(str,p['dual'])),p['group_type'],p['L_invariant'],p['R_invariant']] for p in parts])
writecsv('blocks.csv',['partition','types','codes','exact_formula','support_closure','cost'],[[p['id'],' '.join(b['types']),' '.join(map(str,b['codes'])),conjunction(b),' '.join(b['support_closure']),str(b['cost'])] for p in parts for b in p['blocks_detail']])
writecsv('positional_bounds.csv',['partition','types','aspect','allowed_functions'],[[p['id'],' '.join(b['types']),a,' '.join(map(str,fs))] for p in parts for b in p['blocks_detail'] for a,fs in b['all_positional_bounds'].items()])
errors=[r for r in AU['formulas'] if r['status']=='fails']
writecsv('source_errors.csv',['file','line','block','kind','formula','counterexamples','actual_truth_set','corrected_target_union'],[[r['file'],r['line'],' '.join(r['types']),r['kind'],r['formula'],' '.join(r['counterexamples']),' '.join(r['satisfying_types']),r.get('corrected_target_union','')] for r in errors])
writecsv('source_all_formulas.csv',['file','line','block','kind','formula','status','actual_truth_set'],[[r['file'],r['line'],' '.join(r['types']),r['kind'],r['formula'],r['status'],' '.join(r['satisfying_types'])] for r in AU['formulas']])
writecsv('missing_pairs.csv',['octa','type1','type2'],[[p['octa']]+p['pair'] for p in C['missing_octa_pairs']])

blocks=[]
for prefix,heading in [('D','Дихотомии'),('T','Тетрахотомии'),('O','Октохотомии')]:
    blocks.append('## '+heading+'\n')
    for p in [p for p in parts if p['id'].startswith(prefix)]:
        label=names[p['dual'][0]] if prefix=='D' else (' / '.join(names[h] for h in p['dual']) if prefix=='T' else 'направление '+T[p['direction'][1]])
        blocks.append('### '+p['id']+'. '+label+'\n')
        invariant=('L и R' if p['L_invariant'] and p['R_invariant'] else ('L' if p['L_invariant'] else ('R' if p['R_invariant'] else 'ни L, ни R')))
        blocks.append('Направление U: '+setstr(p['direction'])+'. Постоянные маски: '+setstr(p['dual'])+'. Инвариантность: '+invariant+'. Подгруппа направления: '+(p['group_type'] or 'не является подгруппой')+'. Позиционное замыкание блока: '+str(len(p['blocks_detail'][0]['support_closure']))+' типов.\n')
        blocks.append(table(['Блок типов','Точное условие'],[(', '.join(b['types']),conjunction(b)) for b in p['blocks_detail']]))

orbit_rows=[]
lookup={frozenset(p['direction']):p['id'] for p in parts}
for autkey,groupname in [('ring_automorphisms','32 общих автоморфизма'),('ring_aut_representation','16 с сохранением представления')]:
    for size in [8,4,2]:
        rem={frozenset(p['direction']) for p in parts if len(p['direction'])==size}
        os=[]
        while rem:
            u=min(rem,key=lambda z:sorted(z));o={frozenset(g[x] for x in u) for g in D[autkey]}
            assert o<=rem
            rem-=o;os.append(sorted(lookup[z] for z in o))
        for o in sorted(os,key=lambda z:(len(z),z)):orbit_rows.append([groupname,{8:'D',4:'T',2:'O'}[size],len(o),', '.join(o)])
writecsv('partition_orbits.csv',['automorphism_group','family','orbit_size','partition_ids'],orbit_rows)

errorrows=[]
for r in errors:
    tag=('P5' if r['file'].startswith('04') else 'P6')+':'+str(r['line'])
    t=r['counterexamples'][0]
    if r['kind']=='subset':
        aa=re.findall(r'Ч[ИЭСЛ]|Б[ИЭСЛ]',r['formula'].split(']')[0])
        actual=sorted({D['models'][t].index(a)+1 for a in aa})
        detail=setstr(aa)+' → '+setstr(actual)
    else:detail='нарушено '+('циклическое направление' if r['kind']=='cycle' else 'равенство семейств пар')
    errorrows.append([tag,t,detail])

fp=ROOT/'report-source.md'
if fp.exists() and '<!-- TRAITS_TABLE -->' in fp.read_text():
    s=fp.read_text()
    content={
      'TRAITS_TABLE':table(['Маска h','Положительный признак','Бит отрицательного полюса h(x)','Класс'],[[h,n,'$'+f+'$',c] for h,n,f,c in traits]),
      'ASPECT_FUNCTION_COORDS':table(['Код u+2v+4w','Биты (u,v,w)','Аспект','Функция'],[[x,bits(x,3),next(a for a,v in D['aspect_codes'].items() if v==x),next(f for f,v in D['function_codes'].items() if v==x)] for x in range(8)]),
      'DICTIONARY':table(['i','ТИМ','(e,r,n,l)','Перестановка P','Порядок','Отношение от ИЛЭ'],dictionary),
      'MEMBERSHIP_CORRECTIONS':table(['Раздел P5','Строка','Напечатано','Исправлено'],[['T%02d'%r['section'],r['line'],', '.join(r['old']),', '.join(r['new'])] for r in C['membership_corrections']]),
      'MODELS_TABLE':table(['i','ТИМ']+list(range(1,9)),models),
      'REININ_TABLES':'\n\n'.join(table(['ТИМ']+[str(h) for h in range(start,start+8)],[[T[x]]+[1-((x&h).bit_count()%2) for h in range(start,start+8)] for x in range(16)]) for start in [0,8]),
      'EIGHT_SIGN_TABLES':'Столбцы аспектов: 0 сущ.; 1 верт.; 2 дельта/бета; 3 отвлечённые/вовлечённые; 4 альфа/гамма; 5 неявные/явные; 6 нальность; 7 тальность.\n\n'+table(['Аспект']+list(range(8)),[[a]+['+' if v>0 else '−' for v in D['aspect_signs'][a]] for a in D['aspects']])+'\nСтолбцы функций: 0 сущ.; 1 верт.; 2 оценочные/ситуативные; 3 сильные/слабые; 4 ценностные/подавляемые; 5 инертные/контактные; 6 нальность; 7 тальность.\n\n'+table(['Функция']+list(range(8)),[[f]+['+' if v>0 else '−' for v in D['function_signs'][str(f)]] for f in range(1,9)]),
      'VERIFICATION_TABLE':table(['Проверка','Количество'],[[k,v] for k,v in {'Биективность моделей':16,'Произведения нормированных перестановок':256,'Тройки для ассоциативности и двух брейс-тождеств':4096,'Тройки фактора для 2-коцикла':512,'Пары для относительного оператора':256,'Значения действия на характерах':8192,'Точно заданные блоки каталога':290,'Позиционные замыкания блоков':290,'Элементы, сопряжённые с каталогом 8T9':16,'Значения исправленных TM-предикатов':128,'Явные общие автоморфизмы':32,'Направления для критериев подгруппы и идеалов':67}.items()]),
      'FULL_CATALOGUE':'\n'.join(blocks),
      'MISSING_PAIRS': '## Недостающие 22 пары P6\n\n'+table(['Октохотомия','Недостающая пара'],[[p['octa'],', '.join(p['pair'])] for p in C['missing_octa_pairs']]),
      'ERROR_TABLE':'## Контрпримеры к 63 вхождениям формул\n\nУказан один контрпример на строку. Для включений справа показан фактический образ аспектов у этого типа; он не входит в напечатанное ограничение. Полные формулы и все контрпримеры сохранены в source_errors.csv.\n\n'+table(['Файл:строка','Контрпример','Фактическое положение / нарушение'],errorrows),
      'ORBITS_TABLE':'## Орбиты на всех разбиениях\n\n'+table(['Группа','Семейство','Размер','Разбиения'],orbit_rows)
    }
    for marker,value in content.items():
        assert '<!-- '+marker+' -->' in s,marker
        s=s.replace('<!-- '+marker+' -->',value)
    assert '<!--' not in s
    fp.write_text(s)
print('Exported',len(list(OUT.glob('*.csv'))),'CSV files;',len(parts),'partitions;',sum(len(p['blocks_detail']) for p in parts),'blocks.')
