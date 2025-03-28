# Proyecto médico

Este es un proyecto basado en Django para la gestión médica. Permite administrar información relacionada con pacientes, doctores y citas médicas.

## 📌 Requisitos
Asegúrate de tener instalados los siguientes requisitos antes de comenzar:
- Python 3.x
- pip

## 🚀 Instalación

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/LuisM711/proyectoMedico.git
cd proyectoMedico
```

### 2️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3️⃣ Crear un superusuario (opcional)
```bash
python manage.py createsuperuser
```
Sigue las instrucciones para crear el usuario administrador.

### 4️⃣ Iniciar el servidor
```bash
python manage.py runserver
```
El proyecto estará disponible en `http://127.0.0.1:8000/`.

## 📚 Credenciales de prueba
<!-- Credenciales usadas por nosotros -->
```
admin:administrator  <-- Administrador
andrik:password      <-- Especialista (Nutrición)
gaby:password        <-- Paciente
```

## 💂️🏼 Estructura del Proyecto
```
proyectoMedico/
│-- .idea/
│-- .vscode/
│-- moduloNutricion/
│   │-- __pycache__/
│   │-- models/
│   │-- static/
│   │-- templates/
│   │-- views/
│   │   │-- __init__.py
│   │   │-- admin.py
│   │   │-- apps.py
│   │   │-- models.py
│   │   │-- tests.py
│   │   │-- urls.py
│   │   │-- views.py
│-- moduloPrincipal/
│   │-- __pycache__/
│   │-- migrations/
│   │-- models/
│   │-- static/
│   │-- templates/
│   │-- views/
│   │   │-- __init__.py
│   │   │-- admin.py
│   │   │-- apps.py
│   │   │-- models.py
│   │   │-- tests.py
│   │   │-- urls.py
│   │   │-- views.py
│-- proyectoMedico/
│-- db.sqlite3
│-- favicon.ico
│-- manage.py
│-- README.md
│-- requirements.txt

```

## 🛠 Tecnologías utilizadas
- **Django**: Framework web en Python
- **Bootstrap**: Para mejorar la interfaz de usuario
- **SQLite**: Base de datos

## 📝 Licencia
Este proyecto está bajo la licencia MIT.

## 🤝 Contribuciones
Si deseas contribuir, haz un fork del repositorio y envía un pull request.

🚀¡Gracias por tu interés en este proyecto! 🚀

