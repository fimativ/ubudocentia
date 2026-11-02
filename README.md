# UBU-Docentia (herramienta no oficial, v2.1)

Calculadora orientativa de la puntuación del modelo UBU-Docentia (manual v4.07), pensada para el profesorado de la Universidad de Burgos. Usar bajo propia responsabilidad. No se almacena ninguna información personal en el servidor.

- App: https://ubudocentia.streamlit.app
- Copia local sin conexión: `docentia_ubu.html` (un solo archivo, se abre en cualquier navegador).

## Ejecutar en local
```
pip install -r requirements.txt
streamlit run app.py
```

## Desplegar en Streamlit Community Cloud
1. Suba esta carpeta a un repositorio público de GitHub.
2. En https://share.streamlit.io, elija el repositorio, la rama y `app.py`.
3. En «Advanced settings», escriba `ubudocentia` como subdominio.

## Archivos
- `app.py`: interfaz y cálculo.
- `encuestas.py`: lectura de los informes de encuesta en PDF de la Unidad Técnica de Calidad.
- `textos.py`: elementos del informe de reflexión y prompt de revisión.
- `docentia_ubu.html`: copia local autocontenida.

Licencia MIT. Autor: Sinuhé Perea Puente.
