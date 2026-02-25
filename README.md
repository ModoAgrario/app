# Harina de Trigo App (MVP inicial mejorado)

Ahora el proyecto quedó con arquitectura más sólida para avanzar hacia app iOS/Android:

## Lo nuevo
- Backend FastAPI con arquitectura por proveedores para **sumar APIs externas**.
- Integración preparada para **scraping de ModoAgrario.com/market**.
- Frontend web minimalista y moderno, con estética limpia tipo ChatGPT:
  - pantalla blanca,
  - tipografía Inter,
  - botones negros,
  - bloque reservado para banner publicitario futuro.

## Endpoints y UI
- `GET /` interfaz visual MVP.
- `GET /health`
- `GET /sources` (muestra fuentes activas)
- `GET /quotes/latest`
- `GET /quotes/history`

## Roadmap recomendado (siguiente paso)
1. React Native/Expo conectado a estos endpoints.
2. Persistencia en PostgreSQL + tabla de trazabilidad por fuente.
3. Scheduler para scraping periódico + validación de calidad de datos.
4. Alertas push por variación de precio.
5. Módulo admin para alta/corrección de cotizaciones.
