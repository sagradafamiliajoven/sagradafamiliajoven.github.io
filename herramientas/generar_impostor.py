"""Genera las partidas de «El impostor» a partir de banco_conexiones.py → datos/impostor.json.

Uso:  python herramientas/generar_impostor.py                    (genera 200, REEMPLAZA las actuales)
      python herramientas/generar_impostor.py --rehacer-desde 13 (deja igual los días 1 a 13 y rehace los siguientes)

Cada partida: una categoría y 10 fichas. Entre 6 y 9 son de la categoría (de su lista «usar») y el resto
(1 a 4) son impostores (el juego no dice cuántos): palabras de otra categoría DEL MISMO TIPO (ver TIPOS), que NO encajan en esta
(se controla contra «usar» y «tambien», así no hay impostores discutibles).
"""
import json
import os
import random
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from banco_conexiones import C  # noqa: E402

SALIDA = os.path.join(AQUI, 'datos', 'impostor.json')
ESPERA = 20  # días mínimos antes de que una categoría vuelva a salir
# juegos de palabras o listas donde «pertenecer» es discutible: no sirven para este juego
EXCLUIR = {'___ Santo / ___ Santa', 'Sagrada ___', 'Palabras hebreas o arameas que usamos', 'Grupos de Sagrada Familia'}


def norm(s):
    s = unicodedata.normalize('NFD', s.upper()).encode('ascii', 'ignore').decode()
    return ' '.join(s.split())


def miembros(c):
    return {norm(w) for w in c['usar'] + c['tambien']}


CATS = [c for c in C if len(c['usar']) >= 6 and c['nombre'] not in EXCLUIR]

# Los impostores salen de categorías del MISMO TIPO, así engañan de verdad
# (un apóstol entre los hijos de Jacob, una carta de Pablo entre los pueblos vecinos, etc.).
TIPOS = {
    'personas de la Biblia': ['Apóstoles', 'Hijos de Jacob', 'Reyes de Israel y Judá', 'Mujeres del Antiguo Testamento', 'Jueces de Israel',
                              'Personajes del Génesis', 'Personajes del Éxodo', 'Personajes de la Pasión', 'Mujeres del Nuevo Testamento',
                              'Profetas menores', 'Profetas mayores'],
    'personas de la Iglesia': ['Santos jóvenes', 'Mártires de los primeros siglos', 'Nombres de papas', 'Apellidos de papas', 'Escritores católicos',
                               'Santos y beatos argentinos', 'Doctoras de la Iglesia'],
    'lugares': ['Lugares de la vida de Jesús', 'Montes de la Biblia', 'Advocaciones de la Virgen', 'Ciudades argentinas con nombre de santo',
                'Lugares de peregrinación', 'Ríos y mares de la Biblia'],
    'grupos en plural': ['Pueblos vecinos de Israel', 'Órdenes religiosas', 'Coros de ángeles'],
    'libros de la Biblia': ['Cartas de san Pablo', 'Libros sapienciales', 'Libros del Pentateuco'],
    'cosas': ['Cosas que se usan en misa', 'Cosas que hay en una iglesia', 'Instrumentos de la Pasión', 'Cosas de Navidad', 'Cosas de un campamento',
              'Instrumentos de la Biblia', 'Plantas de la Biblia', 'Comidas de la Biblia', 'Plagas de Egipto', 'Vestiduras litúrgicas',
              'Símbolos de Pascua', 'Materia de los sacramentos', 'Animales de la Biblia'],
    'liturgia': ['Partes de la misa', 'Oraciones', 'Liturgia de las Horas', 'Fiestas del año litúrgico', 'Fiestas de la Virgen', 'Gestos en misa',
                 'Sacramentos', 'Tiempos litúrgicos', 'Días de Semana Santa'],
    'virtudes y conceptos': ['Pecados capitales', 'Dones del Espíritu Santo', 'Frutos del Espíritu Santo', '«Felices los…» (Bienaventuranzas)',
                             'Nombres de Jesús', 'Títulos de María en las letanías', 'Virtudes cardinales', 'Oficios y cargos en el Evangelio'],
    'acciones y relatos': ['Obras de misericordia corporales', 'Obras de misericordia espirituales', 'Parábolas de Jesús', 'Milagros de Jesús',
                           'Canciones de misa en Sagrada'],
}
TIPO_DE = {n: t for t, ns in TIPOS.items() for n in ns}
sin_tipo = [c['nombre'] for c in CATS if c['nombre'] not in TIPO_DE]
assert not sin_tipo, f'Categorías sin tipo en generar_impostor.py: {sin_tipo}'



def armar(rnd, cat, uso_ficha):
    propios = miembros(cat)
    k = min(9, len(cat['usar']))
    ok = sorted(cat['usar'], key=lambda w: uso_ficha.get(norm(w), 0) + rnd.random() * 1.5)[:k]
    # impostores: primero de categorías «parecidas» (comparten alguna palabra), si no, de cualquiera
    otras = [c for c in C if c is not cat]
    parecidas = [c for c in otras if TIPO_DE.get(c['nombre']) == TIPO_DE[cat['nombre']]]
    imp = []
    for grupo in (parecidas, otras):
        pool = [w for c in grupo for w in c['usar'] if norm(w) not in propios and norm(w) not in {norm(x) for x in imp}]
        rnd.shuffle(pool)
        while pool and len(imp) < 10 - k:
            imp.append(pool.pop())
        if len(imp) == 10 - k:
            break
    fichas = [{'w': w, 'ok': 1} for w in ok] + [{'w': w, 'ok': 0} for w in imp]
    assert len(fichas) == 10 and len({norm(f['w']) for f in fichas}) == 10
    return {'c': cat['nombre'], 'f': fichas}


def generar(n, previas, semilla):
    rnd = random.Random(semilla)
    uso_cat, uso_ficha, todas = {}, {}, list(previas)
    for p in todas:
        uso_cat[p['c']] = uso_cat.get(p['c'], 0) + 1
    while len(todas) < len(previas) + n:
        recientes = {p['c'] for p in todas[-ESPERA:]}
        pool = [c for c in CATS if c['nombre'] not in recientes] or CATS
        pesos = [1 / (1 + uso_cat.get(c['nombre'], 0)) ** 2 for c in pool]
        cat = rnd.choices(pool, weights=pesos)[0]
        p = armar(rnd, cat, uso_ficha)
        todas.append(p)
        uso_cat[cat['nombre']] = uso_cat.get(cat['nombre'], 0) + 1
        for f in p['f']:
            uso_ficha[norm(f['w'])] = uso_ficha.get(norm(f['w']), 0) + 1
    return todas


def main():
    if '--rehacer-desde' in sys.argv:
        desde = int(sys.argv[sys.argv.index('--rehacer-desde') + 1])
        ruta_orden = os.path.join(AQUI, 'datos', 'orden.json')
        orden = json.load(open(ruta_orden, encoding='utf-8'))
        previas = json.load(open(SALIDA, encoding='utf-8'))
        salieron = [previas[int(i)] for i in orden.get('impostor', [])[:desde]]
        todas = generar(200 - len(salieron), salieron, f'impostor:{desde}')
        orden['impostor'] = [str(i) for i in range(len(todas))]
        json.dump(orden, open(ruta_orden, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    else:
        todas = generar(200, [], 'impostor')
    json.dump(todas, open(SALIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    imp = [sum(1 for f in p['f'] if not f['ok']) for p in todas]
    print(f'Impostor: {len(todas)} partidas · {len(CATS)} categorías · impostores por partida: '
          f'{min(imp)} a {max(imp)} ' + str({n: imp.count(n) for n in sorted(set(imp))}))


if __name__ == '__main__':
    main()
