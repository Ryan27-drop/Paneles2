Optimización de Paneles Solares Ryan C, Jorge F, Matías H

Este proyecto tiene como objetivo minimizar el costo de instalación de paneles solares en tres casas, utilizando un modelo de Programación Lineal Entera.

---

Función objetivo del Modelo

Minimizar el costo total de inversión en paneles solares, garantizando que cada casa cubra su demanda energética y respete las limitaciones de espacio disponible en el techo.

---

Variables de Decisión

Para cada casa (i = 1, 2, 3):

- Ai: cantidad de paneles tipo A
- Bi: cantidad de paneles tipo B
- Ci: cantidad de paneles tipo C

Todas las variables son enteras y no negativas.

---

Función Objetivo (Matemáticamente)

Minimizar el costo total:

Min Z = 190(A1+A2+A3) + 205(B1+B2+B3) + 255(C1+C2+C3)

Donde:
- Panel A cuesta $190
- Panel B cuesta $205
- Panel C cuesta $255

---

Restricciones

### 1. Restricciones de Energía

Cada casa debe generar al menos la energía que consume diariamente:

(400Ai + 450Bi + 550Ci) * horas_sol / 1000 ≥ demanda_diaria_i

Donde:
- 400W, 450W y 550W son las potencias de los paneles
- horas_sol es el promedio de horas solares diarias
- demanda diaria se calcula como consumo mensual / 30

---

2. Restricciones de Área

El área total ocupada por los paneles no debe exceder el área del techo:

1.9Ai + 2.1Bi + 2.5Ci ≤ área_techo_i

---

### 3. Restricciones de Entereza

Ai, Bi, Ci ∈ ℤ⁺ (valores enteros no negativos)

---

Tipo de Modelo

- Programación Lineal Entera (PLE)
- Problema de minimización
- Variables discretas (número de paneles)

---

Implementación

El modelo fue implementado en Python utilizando:

- PuLP → para modelado matemático
- Streamlit → para interfaz interactiva
- GitHub → control de versiones

---

Funcionalidades

El modelo creado permite modificar ciertos parametros entre los cuales están:

  - Consumo mensual
  - Área del techo
  - Horas de sol
- Calcula automáticamente:
  - Cantidad óptima de paneles por tipo
  - Costo mínimo total

---

Conclusión

El modelo permite tomar decisiones óptimas sobre la instalación de paneles solares, minimizando costos y asegurando el cumplimiento de la demanda energética bajo restricciones reales.
