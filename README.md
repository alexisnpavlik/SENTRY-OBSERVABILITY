# SENTRY-OBSERVABILITY

Biblioteca ligera en Python para centralizar la configuración de Sentry y reutilizarla en múltiples proyectos.

## Instalación

```bash
pip install git+https://github.com/Nubiral-EMU/NU00021-SENTRY-OBSERVABILITY.git

```
# Varibles de entorno
Configura las siguientes variables de entorno en tu entorno de ejecución:
- `SERVICE_NAME`: El nombre del servicio que se está instrumentando.
- `SENTRY_DSN`: La URL DSN de tu proyecto en Sentry.
- `SENTRY_DEBUG`: Habilita el modo de depuración (por ejemplo, "true" para habilitar).
- `ENVIRONMENT`: El entorno en el que se está ejecutando la aplicación (por ejemplo, "development", "production").

## Uso

```python
from sentry_observability import azure.handle_exceptions_azure_functions

@azure.handle_exceptions_azure_functions # Decora tu función Azure Function
def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello, World!")
```

## Licencia

[MIT](LICENSE)

