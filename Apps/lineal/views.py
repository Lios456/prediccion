import base64
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
from io import BytesIO
from django.shortcuts import render
from .forms import HumedadForm
import pandas as pd
import joblib
import numpy as np
from pathlib import Path
from sklearn.preprocessing import PolynomialFeatures

# We'll load models dynamically based on user selection
models = {}
# Add polynomial transformer
poly_transformer = None

def predecir_humedad(request):
    grafico = None
    prediccion = None
    form = HumedadForm()
    
    if request.method == 'POST':
        form = HumedadForm(request.POST)
        if form.is_valid():
            # Get the selected model
            modelo_seleccionado = form.cleaned_data['modelo']
            
            # Load the model if not already loaded
            if modelo_seleccionado not in models:
                model_path = Path(__file__).resolve().parent / modelo_seleccionado
                models[modelo_seleccionado] = joblib.load(model_path)
            
            # Use the selected model
            model = models[modelo_seleccionado]
            
            # Obtener temperaturas del formulario
            outdoor_temp = form.cleaned_data['outdoor_temp']
            indoor_temp = form.cleaned_data['indoor_temp']
            
            # Crear arrays para horas y minutos
            hours = np.arange(0, 24)
            minutes = np.arange(0, 60, 15)  # Cada 15 minutos para reducir el número de predicciones
            
            # Crear todas las combinaciones de horas y minutos
            all_hours = []
            all_minutes = []
            all_outdoor = []
            all_indoor = []
            
            for hour in hours:
                for minute in minutes:
                    all_hours.append(hour)
                    all_minutes.append(minute)
                    all_outdoor.append(outdoor_temp)
                    all_indoor.append(indoor_temp)
            
            # Crear DataFrame con todas las combinaciones
            datos = pd.DataFrame({
                'OUTDOOR TEMP': all_outdoor,
                'INDOOR TEMP': all_indoor,
                'hour': all_hours,
                'minute': all_minutes
            })
            
            # Apply polynomial transformation if using polynomial regression model
            if modelo_seleccionado == 'modelo_polinomial.pkl':  # This is the correct filename
                global poly_transformer
                if poly_transformer is None:
                    poly_transformer = PolynomialFeatures(degree=2, include_bias=False)
                    # Fit the transformer with a sample of the data
                    poly_transformer.fit(datos.iloc[:1])
                
                datos_transformados = poly_transformer.transform(datos)
                predicciones = model.predict(datos_transformados)
            else:
                predicciones = model.predict(datos)
            
            # Remove the duplicate prediction line
            # predicciones = model.predict(datos)  # This line should be removed
            
            # Calcular el promedio para mostrar como resultado principal
            prediccion = np.mean(predicciones)
            
            # Generar gráfico de línea para mostrar variación por hora
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Reorganizar datos para graficar por hora
            pred_by_hour = {}
            for i, pred in enumerate(predicciones):
                hour = all_hours[i]
                if hour not in pred_by_hour:
                    pred_by_hour[hour] = []
                pred_by_hour[hour].append(pred)
            
            # Calcular promedio por hora
            hours_list = sorted(pred_by_hour.keys())
            avg_preds = [np.mean(pred_by_hour[h]) for h in hours_list]
            
            # Graficar
            ax.plot(hours_list, avg_preds, marker='o', linestyle='-', color='skyblue')
            ax.set_xlabel('Hora del día')
            ax.set_ylabel('Humedad (%)')
            modelo_nombre = dict(form.fields['modelo'].choices)[modelo_seleccionado]
            ax.set_title(f'Predicción de Humedad Relativa ({modelo_nombre})\nTemp. Ext: {outdoor_temp}°C, Temp. Int: {indoor_temp}°C')
            ax.set_xticks(range(0, 24, 2))
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Convertir gráfico a imagen HTML
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            grafico = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return render(request, 'prediccion.html', {
        'form': form,
        'grafico': grafico,
        'prediccion': prediccion
    })