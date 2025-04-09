from django.urls import path, re_path

from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from moduloPrincipal import *
from moduloPrincipal.views.viewGeneral import *
from moduloPrincipal.views.viewAdmin import *
from moduloPrincipal.views.viewAlergia import *
from moduloPrincipal.views.viewAnt_Quirurjico import *
from moduloPrincipal.views.viewAnt_Transfusional import *
from moduloPrincipal.views.viewEspecialista import *
from moduloPrincipal.views.viewGraficar import *
from moduloPrincipal.views.viewHorario import *
from moduloPrincipal.views.viewPacientes import *
from moduloPrincipal.views.viewPatologia import *
from moduloPrincipal.views.viewPerfilClinico import *
from moduloPrincipal.views.viewToxicomania import *
from moduloPrincipal.views.viewVacuna import *
from moduloPrincipal.views.viewAsistenteVirtual import *
from moduloPrincipal.views.viewGemini import *
from moduloNutricion.views.viewAlimentos import *
from moduloNutricion.views.viewMenuPaciente import *
from moduloNutricion.views.viewListaAlimentos import *
from moduloNutricion.views.viewMapa import *
from moduloNutricion.views.viewMapa import *
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView

urlpatterns = [

    # Urls Generales
    path('', Redirigir.as_view(), name='index'),
    path('login', Login.as_view(), name='login'),
    #loginInvitado
     path('loginInvitado', LoginInvitado.as_view(), name='loginInvitado'),
    path('logout', CerrarSesion.as_view(), name='logout'),
    path('cambiar/contra/', Cambiar_Contra.as_view(), name='cambiar_contra'),
    path('acerca/', Acerca.as_view(), name='acerca'),
    path('especialistas/', Especialistas_Inicio.as_view(), name='especialistas'),
    path('registrarse/', Registrarse.as_view(), name='registrarse'),
    path('subir/imagen/perfil', SubirImagenPerfil.as_view(), name='subir_imagen_perfil'),
#     path('user_type', UserType.as_view(), name='user_type'),
    # Cambio de contraseña
    path('reset/password_reset', PasswordResetView.as_view(template_name='recuperar_contra/recuperar_contra.html',
                                                           email_template_name="recuperar_contra/plantilla_email.html"),
         name='password_reset'),
    path('reset/password_reset_done',
         PasswordResetDoneView.as_view(template_name='recuperar_contra/recuperar_contra_done.html'),
         name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-za-z_\-]+)/(?P<token>.+)/$',
            PasswordResetConfirmView.as_view(template_name='recuperar_contra/recuperar_contra_confirm.html'),
            name='password_reset_confirm'),
    path('reset/done',
         PasswordResetCompleteView.as_view(template_name='recuperar_contra/recuperar_contra_complete.html'),
         name='password_reset_complete'),
    path('configuracion/', Configuracion.as_view(), name='configuracion'),
    # Urls de Paciente
    path('inicio', InicioEspecialista.as_view(), name='inicio_especialista'),
    path('inicio', InicioEspecialista.as_view(), name='inicio_paciente'),
    path('registrarse/paciente', Registrarse_paciente.as_view(), name='registrarse_paciente'),
    path('listarcitas/paciente/', ListarCitas_Paciente.as_view(), name='listarcitaspaciente'),
    path('listarcitas/paciente/<int:id>', ListarCitas_Paciente.as_view(), name='listarcitaspaciente'),
    path('configuracion/paciente/<str:message1>', Configuracion_paciente.as_view(), name='configuracion_paciente'),
    path('cambiar/username/paciente', CambiarUsernamePaciente.as_view(), name='cambiar_username_paciente'),
    path('agendarcita/<int:id>', Agendar.as_view(), name='agendarcita'),
    path('agendarcita/', Agendar.as_view(), name='agendarcita'),
    path('listarespecialistas/<int:id>', Especialistas.as_view(), name='listarespecialistas'),
    path('listarespecialistas/', Especialistas.as_view(), name='listarespecialistas'),
    path('informacion/especialista/<int:id_especialista>/<int:id_usuario>/<int:id_user>',
         Informacion_especialista.as_view(), name='info_especialista'),
    path('enviar_solicitud/<int:id_especialista>', Enviar_solicitud.as_view(), name='enviar_solicitud'),
    path('perfil_clinico', Perfil_Clinico.as_view(), name="perfil_clinico"),
    path('menu_paciente', Menu_paciente.as_view(), name='menu_paciente'),
    path('registrar_toxicomanias', Registrar_Toxicomania.as_view(), name='registrar_toxicomania'),
    path('registrar_patologia', Registrar_Patologia.as_view(), name='registrar_patologia'),
    path('registrar_ant_quirurjico', Registrar_Ant_Quirurjico.as_view(), name='registrar_ant_quirurjico'),
    path('registrar_ant_transfusional', Registrar_Ant_Transfusional.as_view(), name='registrar_ant_transfusional'),
    path('registrar_alergia', Registrar_Alergia.as_view(), name='registrar_alergia'),
    path('registrar_vacuna', Registrar_Vacuna.as_view(), name='registrar_vacuna'),
    path('guardar_ficha', Guardar_Ficha.as_view(), name="guardar_ficha"),

    # Urls de Especialista
    path('registrarse/especialista', Registrarse_especialista.as_view(), name='registrarse_especialista'),
    path('configuracion/especialista/<str:message1>/<str:message2>', Configuracion_especialista.as_view(),
         name='configuracion_especialista'),
    path('cambiar/username/especialista', CambiarUsernameEspecialista.as_view(), name='cambiar_username_especialista'),
    path('listarcitas/especialista/', ListarCitas_Especialista.as_view(), name='listarcitasespecialista'),
    path('listarcitas/especialista/<int:id>', ListarCitas_Especialista.as_view(), name='listarcitasespecialista'),
    path('listarpacientes/<int:id>', Pacientes.as_view(), name='listarpacientes'),
    path('listarpacientes/', Pacientes.as_view(), name='listarpacientes'),
    path('consulta_medica/<int:id>', ConsultaMedica.as_view(), name='ConsultaMedica'),
    path('visualizar_consulta/<int:id>', VisualizarConsulta.as_view(), name='VisualizarConsulta'),
    path('informacion/paciente/full/<int:id>', Informacion_Paciente_full.as_view(), name='info_paciente_full'),
    path('informacion/paciente/<int:id_paciente>', Informacion_paciente.as_view(), name='info_paciente'),
    path('especialista/horario', Horario.as_view(), name='horario_especialista'),
    path('grafica/<int:id>/<int:tipo>', grafica, name='grafica'),
    path('graficas/', Graficas.as_view(), name='graficas'),
    path('grafica2/<int:id>/<int:tipo>', grafica_EXP, name='grafica_exp'),
    path('listaAlimentos/', Lista_Alimentos.as_view(), name='listaAlimentos'),
    #path('mapa/',Mapa.as_view(),name='Mapa'),
    path('api/foods/', fetch_category_data, name='fetch_category_data'),
    path('api/types/', fetch_tipo_data, name='fetch_tipo_data'),
    path('api/units/', fetch_unidades_data, name='fetch_unidades_data'),
    path('mapa/', visualizarMapa, name='mapa'),
     
     path('reglasDifusas/', reglasDifusas, name='reglasDifusas'),
     path('gemini/<str:prompt>', gemini, name='gemini'),
     path('unidades', unidades , name='unidades'),


    # Urls del administrador
    path('inicio/admin/', InicioAdmin.as_view(), name='inicio_admin'),
    path('listarpacientes/admin', Pacientes_Admin.as_view(), name='listarpacientes_admin'),
    path('listarpacientes/admin/<int:id>', Pacientes_Admin.as_view(), name='listarpacientes_admin'),
    path('informacion/paciente/admin/<int:id>', Informacion_paciente_admin.as_view(), name="infopaciente_admin"),
    path('listarespecialistas/admin/<int:id>', Especialistas_Admin.as_view(), name='listarespecialistas_admin'),
    path('listarespecialistas/admin/', Especialistas_Admin.as_view(), name='listarespecialistas_admin'),
    path('informacion/especialista/admin/<int:id_especialista>/<int:id_usuario>/<int:id_user>',
         Informacion_especialista_admin.as_view(), name='info_especialista_admin'),
    path('listarespecialidades/admin', Listar_especialidades_admin.as_view(), name='especialidades_admin'),
]
