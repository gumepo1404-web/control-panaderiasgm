from flask import Flask, render_template, request
import csv
import os
from datetime import datetime

app = Flask(__name__)

# Configuración del inventario y precios
inventario_panes = {
    "PAN $8.00": ["Bisquet", "Magdalena", "Capacillo", "Dona azucar", "Concha", "Lima", "Piojosa", "Chicharrón", "Rebanada", "Novia", "Cuerno", "Corbata", "Oreja", "Banderilla", "Broca", "Polvoron", "Galleta", "Budin", "Hojaldra", "Bollo", "Gusano", "Piedra"],
    "PAN $10.00": ["Dona choco", "Dona fresa", "Dona blanca", "Dona maple", "Dona moka", "Ojo de buey", "Rollo", "Beso", "Chino", "Abanico", "Sacramento", "Trenza", "Peineta", "Taco piña", "Capa choco", "Pierna", "Cacahuate"],
    "PAN $12.00": ["Multi", "Bola Berlin", "Cono", "Cubilete", "Reb. choco", "Rol"],
    "PAN $14.00": ["Rollo Zarza", "Muffin", "Rosca", "Pingüino", "Bombin", "Astorga"],
    "OTROS": {"Bolillo": 3.0, "Barra": 4.0, "Español": 7.0}
}

archivo_csv = "registro_panaderia.csv"

def calcular_cantidad_bolsas(ini, fin):
    if ini == 0 and fin == 0: return 0
    return (fin - ini) if fin >= ini else (200 - ini) + fin

@app.route('/', methods=['GET', 'POST'])
def index():
    # Crear una lista plana de todos los panes para el buscador de pan frío
    lista_plana_panes = []
    for cat, panes in inventario_panes.items():
        if isinstance(panes, list):
            lista_plana_panes.extend(panes)
        else:
            lista_plana_panes.extend(panes.keys())
    lista_plana_panes.sort()

    resultado = None
    if request.method == 'POST':
        try:
            # 1. Datos Generales
            turno = request.form.get('turno')
            dia = request.form.get('dia')
            fecha_form = request.form.get('fecha')
            empleado = request.form.get('empleado')
            
            # 2. Venta de Pan (Cálculo principal)
            total_venta_pan = 0
            for cat, lista in inventario_panes.items():
                precio_base = float(cat.split('$')[1].split()[0]) if '$' in cat else 0
                for pan in (lista if isinstance(lista, list) else lista.keys()):
                    precio = inventario_panes["OTROS"][pan] if cat == "OTROS" else precio_base
                    ini = float(request.form.get(f'{pan}_ini', 0) or 0)
                    ent = float(request.form.get(f'{pan}_ent', 0) or 0)
                    fin = float(request.form.get(f'{pan}_fin', 0) or 0)
                    vendidas = (ini + ent) - fin
                    total_venta_pan += (max(0, vendidas) * precio)

            # 3. Bolsas (Lógica circular 200)
            v_bolsa = 0
            for i in range(1, 4):
                b_ini = float(request.form.get(f'b{i}_ini', 0) or 0)
                b_fin = float(request.form.get(f'b{i}_fin', 0) or 0)
                v_bolsa += calcular_cantidad_bolsas(b_ini, b_fin)

            # 4. Totales Finales
            p_frio_dinero = float(request.form.get('p_frio_dinero_hidden', 0) or 0)
            gastos = float(request.form.get('gastos', 0) or 0)
            efectivo = float(request.form.get('efectivo', 0) or 0)
            
            venta_neta = (total_venta_pan + v_bolsa) - p_frio_dinero - gastos
            diferencia = efectivo - venta_neta

            # 5. Guardar CSV
            with open(archivo_csv, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([fecha_form, dia, turno, empleado, total_venta_pan, v_bolsa, p_frio_dinero, gastos, venta_neta, efectivo, diferencia])

            resultado = {"neta": venta_neta, "dif": diferencia}
        except Exception as e:
            resultado = {"error": str(e)}

    return render_template('index.html', inventario=inventario_panes, lista_panes=lista_plana_panes, resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)