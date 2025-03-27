# Proyecto Médico

Este es un proyecto basado en Django para la gestión médica. Permite administrar información relacionada con pacientes, doctores y citas médicas.

## 📌 Requisitos
Asegúrate de tener instalados los siguientes requisitos antes de comenzar:
- Python 3.x
- pip
- virtualenv (opcional pero recomendado)
- PostgreSQL o SQLite (según la configuración del proyecto)

## 🚀 Instalación

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/LuisM711/proyectoMedico.git
cd proyectoMedico
```

### 2️⃣ Crear y activar un entorno virtual (opcional pero recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar la base de datos
Si usas SQLite, no necesitas configuración adicional. Para PostgreSQL, actualiza `settings.py` con tus credenciales.
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tu_basedatos',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5️⃣ Ejecutar migraciones
```bash
python manage.py migrate
```

### 6️⃣ Crear un superusuario (opcional, para acceder al panel de administración)
```bash
python manage.py createsuperuser
```
Sigue las instrucciones para crear el usuario administrador.

### 7️⃣ Iniciar el servidor
```bash
python manage.py runserver
```
El proyecto estará disponible en `http://127.0.0.1:8000/`.

## 📂 Estructura del Proyecto
```
proyectoMedico/
│-- manage.py
│-- requirements.txt
│-- README.md
│-- app_medica/  # Aplicación principal
│   │-- models.py
│   │-- views.py
│   │-- urls.py
│   │-- templates/
│-- static/  # Archivos estáticos
│-- db.sqlite3  # Base de datos (si usas SQLite)
```

## 🛠 Tecnologías utilizadas
- **Django**: Framework web en Python
- **Bootstrap**: Para mejorar la interfaz de usuario
- **PostgreSQL** (opcional): Base de datos

## 📄 Licencia
Este proyecto está bajo la licencia MIT.

## 🤝 Contribuciones
Si deseas contribuir, haz un fork del repositorio y envía un pull request.

¡Gracias por tu interés en este proyecto! 🚀

