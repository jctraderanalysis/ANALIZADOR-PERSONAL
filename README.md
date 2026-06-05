# 📊 Analizador Técnico Multi-Temporal — Python / Streamlit

Mismo analizador técnico pero en Python puro con Streamlit.
Sin API Key. Datos reales de Yahoo Finance. Corre en tu navegador.

---

## ✨ Funcionalidades

- **Tabla 52 semanas** — precio, máx/mín, caída % y $, posición en rango
- **Gráfico interactivo** con Plotly — precio + RSI + MACD histograma
- **Medias móviles** MA30 / MA50 / MA100 / MA200 (activables)
- **Marcos temporales** D1 (diario) · H1 (horario) · M5 (5 minutos)
- **Reporte técnico completo** D1/H1/M5 calculado desde datos reales
- **Exportar CSV** con OHLC + todas las medias + RSI + MACD
- **Tema oscuro / claro** para el gráfico
- **Watchlist** multi-ticker en sidebar

---

## 🚀 Instalación y uso

### Paso 1 — Instalar dependencias

Abre la terminal en la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

### Paso 2 — Correr la app

```bash
streamlit run app.py
```

Se abrirá automáticamente en tu navegador en:
```
http://localhost:8501
```

### En Windows — comandos completos

```cmd
cd C:\Users\PAPOT\OneDrive\Desktop\trading-streamlit
pip install -r requirements.txt
streamlit run app.py
```

---

## 📁 Estructura

```
trading-streamlit/
├── app.py            ← App principal (toda la lógica)
├── requirements.txt  ← Dependencias Python
└── README.md
```

---

## 🧠 Indicadores calculados

| Indicador | Parámetros | Uso |
|-----------|-----------|-----|
| MA | 30, 50, 100, 200 períodos | Tendencia y soporte/resistencia |
| RSI | 14 períodos | Fuerza del movimiento |
| MACD | 12, 26, 9 | Momentum y cruces |
| ATR | 14 períodos | Cálculo de SL/TP |

---

## ⚠ Aviso

Datos vía Yahoo Finance — pueden tener delay ~15 min.
No constituye asesoramiento financiero. Opera siempre con gestión de riesgo.
