from django import forms

class HumedadForm(forms.Form):
    modelo = forms.ChoiceField(
        label="Modelo de predicción",
        choices=[
            ('modelo_regresion_lineal.pkl', 'Regresión Lineal'),
            ('modelo_knn.pkl', 'KNN'),
            ('modelo_polinomial.pkl', 'Regresión Polinómica')
        ],
        initial='modelo_regresion_lineal.pkl'
    )
    outdoor_temp = forms.FloatField(label="Temperatura Exterior (°C)")
    indoor_temp = forms.FloatField(label="Temperatura Interior (°C)")