# Multi-agent: backend de chat con IA y asistente de correo

API en **Python (FastAPI)** que conecta un modelo de lenguaje con una base de datos **PostgreSQL** y con herramientas reales (leer y enviar correos de Gmail). Está contenerizada con **Docker Compose** y desplegada en **Railway**.

El proyecto nació como ejercicio de aprendizaje sobre cómo construir aplicaciones con LLMs más allá de un simple "llamar a la API": persistencia, herramientas, agentes y despliegue.

## Qué hace

- **Chat con IA:** recibe un mensaje, lo guarda en la base de datos y responde con un correo generado por el modelo, ya estructurado en `subject` y `contents`.
- **Historial:** expone los mensajes recientes guardados.
- **Asistente de correo:** el modelo puede decidir leer la bandeja de entrada (IMAP) o enviar un correo (SMTP) a través de *tools*.
- **Modelo intercambiable:** el mismo código funciona con un modelo local gratuito (Docker Model Runner) o con proveedores en la nube (Gemini, Groq, OpenRouter, OpenAI), cambiando solo variables de entorno.

## Arquitectura

```
Cliente ──HTTP──▶ FastAPI ──▶ PostgreSQL        (historial de mensajes)
                     │
                     ├──▶ LLM (local o nube)    (API compatible con OpenAI)
                     │
                     └──▶ Tools de correo ──▶ Gmail (IMAP / SMTP)
```

| Capa | Tecnología |
|---|---|
| API | FastAPI, Uvicorn |
| Datos | PostgreSQL, SQLModel, psycopg 3 |
| IA | LangChain (`langchain-openai`), LangGraph |
| Infraestructura | Docker, Docker Compose, Railway |

```
backend/src/
├── main.py              # app FastAPI, arranque y creación de tablas
└── api/
    ├── db.py            # conexión a la base de datos
    ├── chat/            # rutas y modelos del chat
    ├── ai/              # LLM, esquemas, servicios, tools y agentes
    └── myemailer/       # envío y lectura de correo
```

## Decisiones técnicas

- **Una sola interfaz para todos los modelos.** Todo pasa por un cliente compatible con OpenAI, así que pasar de un modelo local a Gemini en producción es un cambio de configuración, no de código.
- **Configuración por entorno.** Credenciales y URLs viven en variables de entorno, con valores distintos en local y en Railway. Nada sensible está en el código.
- **Dos formas de usar herramientas.** Los modelos con *tool calling* nativo se usan con un agente de LangGraph. Para modelos pequeños que no lo soportan (como SmolLM2), implementé un modo alternativo donde las herramientas se describen en el prompt y la llamada se extrae del texto, con validación y deduplicación para tolerar respuestas rotas o repetidas.
- **Salida estructurada.** Las respuestas se validan contra un esquema Pydantic. Con modelos pequeños, separar la redacción del formateo en dos pasos dio resultados más estables que pedir todo en una sola llamada.
- **Datos persistentes en contenedores.** La base de datos usa un volumen de Docker, y las tablas se crean al arrancar la aplicación.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Estado de la aplicación |
| `POST` | `/api/chats/` | Guarda el mensaje y devuelve el correo generado por la IA |
| `GET` | `/api/chats/recent/` | Últimos mensajes guardados |

Documentación interactiva en `/docs` (Swagger, generada por FastAPI).

## Ejecutarlo en local

Requisitos: Docker Desktop y, para la IA, un modelo local o una API key de algún proveedor.

1. Crea un archivo `.env` a partir de `.env.sample`:

   ```env
   API_KEY=cambia-esto
   DATABASE_URL=postgresql+psycopg://dbuser:db-password@db_service:5432/mydb

   OPENAI_BASE_URL=http://host.docker.internal:12434/engines/v1   # modelo local
   OPENAI_API_KEY=not-needed
   OPENAI_MODEL_NAME=ai/smollm2
   ```

2. Levanta los servicios:

   ```bash
   docker compose up --build
   ```

3. Prueba la API en `http://localhost:8080/docs`, o con:

   ```bash
   curl -X POST http://localhost:8080/api/chats/ \
     -H "Content-Type: application/json" \
     -d '{"message": "Write an email about the benefits of coffee"}'
   ```

Para usar un modelo en la nube, cambia solo las tres variables `OPENAI_*` (por ejemplo, la URL compatible con OpenAI de Gemini o Groq).

## Despliegue

Desplegado en Railway con un servicio para el backend (a partir del `Dockerfile`) y otro de PostgreSQL. La conexión a la base de datos y las credenciales del modelo se definen como variables del servicio. En producción se usa un proveedor de IA en la nube, porque el modelo local solo existe en la máquina de desarrollo.

## Limitaciones conocidas

- Los modelos locales muy pequeños pueden ignorar las herramientas o devolver respuestas poco fiables. Para el agente completo conviene un modelo con soporte nativo de herramientas.
- El proyecto es un ejercicio de aprendizaje: no incluye autenticación de usuarios, tests automatizados ni migraciones de base de datos (las tablas se crean al iniciar).

## Posibles mejoras

- Tests automatizados y CI.
- Migraciones con Alembic en lugar de crear tablas al arrancar.
- Autenticación por usuario y límite de peticiones.
- Guardar también la respuesta de la IA junto a cada mensaje.
