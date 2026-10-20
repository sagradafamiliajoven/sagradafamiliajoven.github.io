"""Rehace los crucigramas desde mañana con las pistas nuevas y arma js/juegos-datos.js.

Uso:  doble clic en «Actualizar crucigrama.bat» (en la carpeta de la web)
      o  python herramientas/actualizar_crucigrama.py

Toma el banco (banco_crucigrama.py) más las pistas que cargan ustedes en
herramientas/datos/pistas_propias.xlsx. Los crucigramas que ya salieron (hasta hoy incluido) no se tocan.
"""
import datetime
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import armar_juegos  # noqa: E402
import generar_crucigramas  # noqa: E402


def main():
    inicio = datetime.date.fromisoformat(armar_juegos.INICIO)
    hoy = datetime.date.today()
    jugados = (hoy - inicio).days + 1  # días que ya salieron, hoy incluido
    generar_crucigramas.rehacer(jugados, max(120, jugados + 100))
    armar_juegos.main()
    print(f'\nListo: los crucigramas cambian desde mañana ({(hoy + datetime.timedelta(days=1)).strftime("%d/%m")}).')


if __name__ == '__main__':
    main()
