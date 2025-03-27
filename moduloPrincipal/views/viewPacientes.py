from datetime import date, timezone, timedelta, datetime
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
import json
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from moduloPrincipal.models.__init__ import *

# CLase para validar el formulario de registro de paciente y registrarlo en la BD
class Registrarse_paciente(View):
    def post(self, request):
        # Se valida que no exista un regsitro con el mismo nombre de usuario
        username = request.POST.get('usuario_p')
        aux_usuarios = list(User.objects.filter(username=username).values())
        if len(aux_usuarios) > 0:
            datos = {'error': "Error, ya existe un registro con ese nombre de usuario"}
            return render(request, 'registro.html', {"datos": datos})

        correo = request.POST.get('correo_p')
        nombre = request.POST.get('nombre_p')
        apellido = request.POST.get('apellido_p')
        contra = request.POST.get('contra_p')
        fecha_nacim = request.POST.get('fecha_nacim_p')

        # Se crea el usuario en la tabla auth_user
        user = User.objects.create_user(username, correo, contra)
        user.first_name = nombre
        user.last_name = apellido
        user.save()
        # Se crea el usuario en la tabla de usuarios
        usuario = Usuario.objects.create(id_usuario_id=user.id, fecha_nacimiento=fecha_nacim, foto='', tipo='P')
        usuario.save()
        # Se crea el paciente con esattus 1 porque no requiere una validacion por parte del administrador
        Paciente.objects.create(id_usuario_id=usuario.id, peso=0, talla=0, estado_civil='', estilo_vida='', estatus='1')
        datos = {'exito': "Registro exitoso"}
        return render(request, 'registro.html', {"datos": datos})

# # CLase para validar el formulario de registro de paciente y registrarlo en la BD
# class Registrarse_paciente(View):
#     def post(self, request):
#         # Se valida que no exista un regsitro con el mismo nombre de usuario
#         username = request.POST.get('usuario_p')
#         aux_usuarios = list(User.objects.filter(username=username).values())
#         if len(aux_usuarios) > 0:
#             datos = {'error': "Error, ya existe un registro con ese nombre de usuario"}
#             return render(request, 'registro.html', {"datos": datos})
#
#         correo = request.POST.get('correo_p')
#         nombre = request.POST.get('nombre_p')
#         apellido = request.POST.get('apellido_p')
#         contra = request.POST.get('contra_p')
#         fecha_nacim = request.POST.get('fecha_nacim_p')
#
#         # Se crea el usuario en la tabla auth_user
#         user = User.objects.create_user(username, correo, contra)
#         user.first_name = nombre
#         user.last_name = apellido
#         user.save()
#         # Se crea el usuario en la tabla de usuarios
#         usuario = Usuario.objects.create(id_usuario_id=user.id, fecha_nacimiento=fecha_nacim, foto='', tipo='P')
#         usuario.save()
#         # Se crea el paciente con esattus 1 porque no requiere una validacion por parte del administrador
#         Paciente.objects.create(id_usuario_id=usuario.id, peso=0, talla=0, estado_civil='', estilo_vida='', estatus='1')
#         datos = {'exito': "Registro exitoso"}
#         return render(request, 'registro.html', {"datos": datos})

# Clase para enviar al paciente a su ventana de inicio


# class InicioPaciente(View):
#     # @method_decorator(guest_or_login_required, name='dispatch')
#     def get(self, request):
#         print("dfsdfiujbsdiubnsdfiujbnsdfiu")
#         print(request.session.get('guest'))
#         if request.session.get('guest'):
#             return render(request, 'ventanas_paciente/inicio_paciente.html', {"Nombre": "Invitado"})

#         if request.user.is_staff == 0:
#             aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
#             if aux_usuario.tipo == 'P':
#                 return render(request, 'ventanas_paciente/inicio_paciente.html', {"Nombre": request.user.first_name})
#             return redirect('inicio_especialista')
#         else:
#             return redirect('inicio_admin')

class CambiarUsernamePaciente(View):
    @method_decorator(login_required, name='dispatch')
    def post(self, request):
        # Se valida que no exista ningun usuario con el username que se quiere actualizar
        aux_usuario = list(User.objects.filter(username=request.POST.get('username')).values())
        if len(aux_usuario) > 0:
            return redirect('/configuracion/paciente/error')
        else:
            user = User.objects.get(id=request.user.id)
            user.username = request.POST.get('username')
            user.save()

            return redirect('/configuracion/paciente/exito')

# # Clase para actualizar el nombre de usuario del paciente
# class CambiarUsernamePaciente(View):
#     @method_decorator(login_required, name='dispatch')
#     def post(self, request):
#         # Se valida que no exista ningun usuario con el username que se quiere actualizar
#         aux_usuario = list(User.objects.filter(username=request.POST.get('username')).values())
#         if len(aux_usuario) > 0:
#             return redirect('/configuracion/paciente/error')
#         else:
#             user = User.objects.get(id=request.user.id)
#             user.username = request.POST.get('username')
#             user.save()
#
#             return redirect('/configuracion/paciente/exito')

# Clase para mostrar la interfaz de configuracion del paciente
class Configuracion_paciente(View):
    @method_decorator(login_required, name='dispatch')
    def get(self, request, message1=""):
        # Validacion de tipos de usaurio
        if (request.user.is_staff == 0):
            aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
            if (aux_usuario.tipo == 'P'):
                aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
                # Muestra un mensaje u otro dependiendo de si se hicieron los cambio correctamente
                if message1 == "exito":
                    datos = {'usuario': aux_usuario, 'nombre': request.user.username, 'correo': request.user.email,
                             'exito': "Nombre actualizado exitosamente"}
                elif message1 == "error":
                    datos = {'usuario': aux_usuario, 'nombre': request.user.username, 'correo': request.user.email,
                             'error': "Ese nombre de usuario ya esta ocupado"}
                else:
                    datos = {'usuario': aux_usuario, 'nombre': request.user.username, 'correo': request.user.email}
                return render(request, 'ventanas_paciente/configuracion_paciente.html', {"datos": datos})
            return redirect('inicio_especialista')
        else:
            return redirect('inicio_admin')

# # Clase para mostrar la interfaz de configuracion del paciente
# class Configuracion_paciente(View):
#     @method_decorator(login_required, name='dispatch')
#     def get(self, request, message1=""):
#         # Validacion de tipos de usaurio
#         if (request.user.is_staff == 0):
#             aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
#             if (aux_usuario.tipo == 'P'):
#                 aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
#                 # Muestra un mensaje u otro dependiendo de si se hicieron los cambio correctamente
#                 if message1 == "exito":
#                     datos = {'usuario': aux_usuario, 'nombre': request.user.username, 'correo': request.user.email,
#                              'exito': "Nombre actualizado exitosamente"}
#                 elif message1 == "error":
#                     datos = {'usuario': aux_usuario, 'nombre': request.user.username, 'correo': request.user.email,
#                              'error': "Ese nombre de usuario ya esta ocupado"}
#                 else:
#                     datos = {'usuario': aux_usuario, 'nombre': request.user.username, 'correo': request.user.email}
#                 return render(request, 'ventanas_paciente/configuracion_paciente.html', {"datos": datos})
#             return redirect('inicio_especialista')
#         else:
#             return redirect('inicio_admin')

# Clase para listar los especialistas en la ventana de paciente
class Especialistas(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(login_required(login_url='login'), name='dispatch')
    def get(self, request):
        # Validacion del tipo de usuario
        if (request.user.is_staff == 0):
            aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
            if (aux_usuario.tipo == 'E'):
                return redirect("inicio_especialista")
            aux_paciente = Paciente.objects.get(id_usuario_id=aux_usuario.id)

            # Se obtienen todos los especialistas
            especialistas = Especialista.objects.all()
            # Se obtienen las solicitudes del paciene
            solicitudes = Solicitudes.objects.filter(id_paciente=aux_paciente.id)

            # Se hace una lista de los especialistas a los que ya se les envio una solicitud para filtrarlos en la interfaz
            lista_solicitados = []
            for solicitud in solicitudes:
                for especialista in especialistas:
                    if solicitud.id_especialista_id == especialista.id:
                        lista_solicitados.append(especialista.id)

            return render(request, 'ventanas_paciente/listar_especialistas.html',
                          {'especialistas': especialistas, 'lista_solicitados': lista_solicitados,
                           'solicitudes': solicitudes})

        else:
            return redirect('inicio_admin')

    @method_decorator(login_required, name='dispatch')
    def post(self, request, id):
        jd = json.loads(request.body)

        try:
            solicitud = Solicitudes.objects.get(id=id)
            solicitud.estatus = jd['estatus']
            solicitud.save()
            return JsonResponse({'success': True})
        except Solicitudes.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Solicitud no encontrada'})

# Clase para visualizar la informacion de especialista por parte del paciente
class Informacion_especialista(View):
    @method_decorator(login_required, name='dispatch')
    def get(self, request, id_user, id_usuario, id_especialista):

        # Validacion de tipos de usaurio
        if (request.user.is_staff == 0):
            aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)

            if (aux_usuario.tipo == 'P'):
                # Se obtiene la informacion del especialista
                aux_user = User.objects.get(id=id_user)
                aux_usuario = Usuario.objects.get(id=id_usuario)
                aux_especialista = Especialista.objects.get(id=id_especialista)

                # Se divide el horario por dias
                arreglo_horario = (aux_especialista.horario).split(";")
                json_horario = {"Lunes": arreglo_horario[0], "Martes": arreglo_horario[1],
                                "Miercoles": arreglo_horario[2], "Jueves": arreglo_horario[3],
                                "Viernes": arreglo_horario[4], "Sabado": arreglo_horario[5],
                                "Domingo": arreglo_horario[6]}

                datos = {'usuario': aux_usuario, 'nombre': aux_user.first_name + " " + aux_user.last_name,
                         'correo': aux_user.email, 'info_ad': aux_especialista.info_ad,
                         'cedula': aux_especialista.cedula, 'especialidad': aux_especialista.id_especialidad.nombre,
                         'horario': json_horario}

                return render(request, 'ventanas_paciente/info_especialista.html', {"datos": datos})

            return redirect('inicio_especialista')

        else:
            return redirect('inicio_admin')

# Clase para enviar al paciente a su ventana de inicio

# class InicioPaciente(View):
#     @method_decorator(guest_or_login_required(), name='dispatch')
#     def get(self, request):
#         # Validacion de tipos de usaurio
#         if (request.user.is_staff == 0):
#             aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)

#             if (aux_usuario.tipo == 'P'):
#                 return render(request, 'ventanas_paciente/inicio_paciente.html', {"Nombre": request.user.first_name})

#             return redirect('inicio_especialista')

#         else:
#             return redirect('inicio_admin')

# Clase para agendar cita
class Agendar(View):
    @method_decorator(login_required, name='dispatch')
    def get(self, request, id):
        # Validacion de tipos de usuario
        if (request.user.is_staff == 0):
            aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
            if (aux_usuario.tipo == 'E'):
                return redirect('inicio_especialista')
            else:
                # se obtiene informacion del paciente
                aux_paciente = Paciente.objects.get(id_usuario_id=aux_usuario.id)
                # se valida que el paciente actual tenga una solicitud aceptada por parte del especialista
                aux_solicitudes = Solicitudes.objects.filter(id_paciente_id=aux_paciente.id).filter(
                    id_especialista_id=id).values()

                # se valida la solicitud del usuario, si es estatus es 'A' (aceptado), se despliega la interfaz de agendar cita, de lo contrario se imprime un mensaje de error
                aceptado = 0
                for solicitud in aux_solicitudes:
                    if solicitud['estatus'] == 'A':
                        aceptado = 1

                        # si la variable no cambia a 1, entonces no se encontro una solicitud aceptada
                if aceptado == 0:
                    return render(request, 'ventanas_paciente/agendar_cita.html',
                                  {'Error': 'Este especialista no ha aceptado una solicitud tuya'})

                # Se obtiene la informacion del especialista
                aux_especialista = Especialista.objects.get(id=id)

                # Validacion de que el especialista haya registrado un horario
                if aux_especialista.horario == ';;;;;;;':
                    return render(request, 'ventanas_paciente/agendar_cita.html',
                                  {'Error': 'El especialista no ha registrado un horario de atencion'})

                arreglo_horario = (aux_especialista.horario).split(";")
                json_horario = {"Lunes": arreglo_horario[0], "Martes": arreglo_horario[1],
                                "Miercoles": arreglo_horario[2], "Jueves": arreglo_horario[3],
                                "Viernes": arreglo_horario[4], "Sabado": arreglo_horario[5],
                                "Domingo": arreglo_horario[6]}

                # Se obtienen las horas intermedias para sacar cita a intervalos de 30 minutos
                intervalo = 30

                # Horas del lunes
                if ", " in arreglo_horario[0]:
                    aux_horas = (arreglo_horario[0].split(', '))
                    turno1 = aux_horas[0]
                    turno2 = aux_horas[1]
                    # Se obtienen las horas de inicio y final del primer turno
                    aux_horas = turno1.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    # Arreglo que contendra las horas de cita del dia lunes
                    horas_lunes = []
                    # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                    horas_lunes = self.obtener_horas_intermedias(horas_lunes, inicio, fin, intervalo)
                    # Se obtienen las horas de inicio y final del segundo turno
                    aux_horas = turno2.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    horas_lunes = self.obtener_horas_intermedias(horas_lunes, inicio, fin, intervalo)
                else:
                    turno1 = arreglo_horario[0]
                    # Se obtienen las horas de inicio y final del primer turno
                    if "-" in turno1:
                        aux_horas = turno1.split('-')
                        inicio = aux_horas[0]
                        fin = aux_horas[1]
                        # Arreglo que contendra las horas de cita del dia lunes
                        horas_lunes = []
                        # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                        horas_lunes = self.obtener_horas_intermedias(horas_lunes, inicio, fin, intervalo)
                    else:
                        horas_lunes = []

                        # Horas del martes
                if ", " in arreglo_horario[1]:
                    aux_horas = (arreglo_horario[1].split(', '))
                    turno1 = aux_horas[0]
                    turno2 = aux_horas[1]
                    # Se obtienen las horas de inicio y final del primer turno
                    aux_horas = turno1.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    # Arreglo que contendra las horas de cita del dia lunes
                    horas_martes = []
                    # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                    horas_martes = self.obtener_horas_intermedias(horas_martes, inicio, fin, intervalo)
                    # Se obtienen las horas de inicio y final del segundo turno
                    aux_horas = turno2.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    horas_martes = self.obtener_horas_intermedias(horas_martes, inicio, fin, intervalo)
                else:
                    turno1 = arreglo_horario[1]
                    # Se obtienen las horas de inicio y final del primer turno
                    if "-" in turno1:
                        aux_horas = turno1.split('-')
                        inicio = aux_horas[0]
                        fin = aux_horas[1]
                        # Arreglo que contendra las horas de cita del dia lunes
                        horas_martes = []
                        # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                        horas_martes = self.obtener_horas_intermedias(horas_martes, inicio, fin, intervalo)
                    else:
                        horas_martes = []

                # Horas del miercoles
                if ", " in arreglo_horario[2]:
                    aux_horas = (arreglo_horario[2].split(', '))
                    turno1 = aux_horas[0]
                    turno2 = aux_horas[1]
                    # Se obtienen las horas de inicio y final del primer turno
                    aux_horas = turno1.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    # Arreglo que contendra las horas de cita del dia lunes
                    horas_miercoles = []
                    # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                    horas_miercoles = self.obtener_horas_intermedias(horas_miercoles, inicio, fin, intervalo)
                    # Se obtienen las horas de inicio y final del segundo turno
                    aux_horas = turno2.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    horas_miercoles = self.obtener_horas_intermedias(horas_miercoles, inicio, fin, intervalo)
                else:
                    turno1 = arreglo_horario[2]
                    # Se obtienen las horas de inicio y final del primer turno
                    if "-" in turno1:
                        aux_horas = turno1.split('-')
                        inicio = aux_horas[0]
                        fin = aux_horas[1]
                        # Arreglo que contendra las horas de cita del dia lunes
                        horas_miercoles = []
                        # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                        horas_miercoles = self.obtener_horas_intermedias(horas_miercoles, inicio, fin, intervalo)
                    else:
                        horas_miercoles = []

                # Horas del jueves
                if ", " in arreglo_horario[3]:
                    aux_horas = (arreglo_horario[3].split(', '))
                    turno1 = aux_horas[0]
                    turno2 = aux_horas[1]
                    # Se obtienen las horas de inicio y final del primer turno
                    aux_horas = turno1.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    # Arreglo que contendra las horas de cita del dia lunes
                    horas_jueves = []
                    # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                    horas_jueves = self.obtener_horas_intermedias(horas_jueves, inicio, fin, intervalo)
                    # Se obtienen las horas de inicio y final del segundo turno
                    aux_horas = turno2.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    horas_jueves = self.obtener_horas_intermedias(horas_jueves, inicio, fin, intervalo)
                else:
                    turno1 = arreglo_horario[3]
                    # Se obtienen las horas de inicio y final del primer turno
                    if "-" in turno1:
                        aux_horas = turno1.split('-')
                        inicio = aux_horas[0]
                        fin = aux_horas[1]
                        # Arreglo que contendra las horas de cita del dia lunes
                        horas_jueves = []
                        # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                        horas_jueves = self.obtener_horas_intermedias(horas_jueves, inicio, fin, intervalo)
                    else:
                        horas_jueves = []

                # Horas del viernes
                if ", " in arreglo_horario[4]:
                    aux_horas = (arreglo_horario[4].split(', '))
                    turno1 = aux_horas[0]
                    turno2 = aux_horas[1]
                    # Se obtienen las horas de inicio y final del primer turno
                    aux_horas = turno1.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    # Arreglo que contendra las horas de cita del dia lunes
                    horas_viernes = []
                    # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                    horas_viernes = self.obtener_horas_intermedias(horas_viernes, inicio, fin, intervalo)
                    # Se obtienen las horas de inicio y final del segundo turno
                    aux_horas = turno2.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    horas_viernes = self.obtener_horas_intermedias(horas_viernes, inicio, fin, intervalo)
                else:
                    turno1 = arreglo_horario[4]
                    # Se obtienen las horas de inicio y final del primer turno
                    if "-" in turno1:
                        aux_horas = turno1.split('-')
                        inicio = aux_horas[0]
                        fin = aux_horas[1]
                        # Arreglo que contendra las horas de cita del dia lunes
                        horas_viernes = []
                        # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                        horas_viernes = self.obtener_horas_intermedias(horas_viernes, inicio, fin, intervalo)
                    else:
                        horas_viernes = []

                # Horas del sabado
                if ", " in arreglo_horario[5]:
                    aux_horas = (arreglo_horario[5].split(', '))
                    turno1 = aux_horas[0]
                    turno2 = aux_horas[1]
                    # Se obtienen las horas de inicio y final del primer turno
                    aux_horas = turno1.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    # Arreglo que contendra las horas de cita del dia lunes
                    horas_sabado = []
                    # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                    horas_sabado = self.obtener_horas_intermedias(horas_sabado, inicio, fin, intervalo)
                    # Se obtienen las horas de inicio y final del segundo turno
                    aux_horas = turno2.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    horas_sabado = self.obtener_horas_intermedias(horas_sabado, inicio, fin, intervalo)

                else:
                    turno1 = arreglo_horario[5]
                    # Se obtienen las horas de inicio y final del primer turno
                    if "-" in turno1:
                        aux_horas = turno1.split('-')
                        inicio = aux_horas[0]
                        fin = aux_horas[1]
                        # Arreglo que contendra las horas de cita del dia lunes
                        horas_sabado = []
                        # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                        horas_sabado = self.obtener_horas_intermedias(horas_sabado, inicio, fin, intervalo)
                    else:
                        horas_sabado = []

                # Horas del domingo
                if ", " in arreglo_horario[6]:
                    aux_horas = (arreglo_horario[6].split(', '))
                    turno1 = aux_horas[0]
                    turno2 = aux_horas[1]
                    # Se obtienen las horas de inicio y final del primer turno
                    aux_horas = turno1.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    # Arreglo que contendra las horas de cita del dia lunes
                    horas_domingo = []
                    # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                    horas_domingo = self.obtener_horas_intermedias(horas_domingo, inicio, fin, intervalo)
                    # Se obtienen las horas de inicio y final del segundo turno
                    aux_horas = turno2.split('-')
                    inicio = aux_horas[0]
                    fin = aux_horas[1]
                    horas_domingo = self.obtener_horas_intermedias(horas_domingo, inicio, fin, intervalo)
                else:
                    turno1 = arreglo_horario[6]
                    # Se obtienen las horas de inicio y final del primer turno
                    if "-" in turno1:
                        aux_horas = turno1.split('-')
                        inicio = aux_horas[0]
                        fin = aux_horas[1]
                        # Arreglo que contendra las horas de cita del dia lunes
                        horas_domingo = []
                        # Se llama a la funcion que devolvera las horas intermedias entre la hora inicial y final
                        horas_domingo = self.obtener_horas_intermedias(horas_domingo, inicio, fin, intervalo)
                    else:
                        horas_domingo = []

                # Se obtiene la fecha actual y se muestra la interfaz de agendar cita
                fecha_actual = timezone.now()
                fecha_actual = fecha_actual + timedelta(days=1)
                # fecha_max = fecha_actual + timedelta(days=30)

                # se calcula la fecha maxima sumando un año a la fecha actual
                fecha_max = fecha_actual.replace(year=fecha_actual.year + 1)
                fecha_actual_str = fecha_actual.strftime('%Y-%m-%d')
                fecha_max_str = fecha_max.strftime('%Y-%m-%d')
                return render(request, 'ventanas_paciente/agendar_cita.html', {'fecha_act': fecha_actual_str,
                                                                               'fecha_max': fecha_max_str,
                                                                               "horario": json_horario,
                                                                               "horas_lunes": horas_lunes,
                                                                               "horas_martes": horas_martes,
                                                                               "horas_miercoles": horas_miercoles,
                                                                               "horas_jueves": horas_jueves,
                                                                               "horas_viernes": horas_viernes,
                                                                               "horas_sabado": horas_sabado,
                                                                               "horas_domingo": horas_domingo,
                                                                               "id_especialista": id,
                                                                               "id_paciente": aux_paciente.id})
        else:
            return redirect('inicio_admin')

    @method_decorator(login_required, name='dispatch')
    def post(self, request):
        jd = json.loads(request.body)
        # Se valida que la hora no este ocupada
        aux_citas = Cita.objects.filter(fecha=jd['fecha']).filter(id_especialista_id=jd['id_especialista']).filter(
            hora__contains=jd['hora']).exclude(estatus="B").values()
        if aux_citas:
            return JsonResponse({'Error': True, 'Descripcion': "Ese dia y hora no estan disponibles para cita"})
        else:
            # Se valida que el paciente no tenga 2 citas registradas el mismo dia a la misma hora
            aux_citas = Cita.objects.filter(fecha=jd['fecha']).filter(hora__contains=jd['hora']).filter(
                id_paciente_id=jd['id_paciente'])
            if aux_citas:
                return JsonResponse(
                    {'Error': True, 'Descripcion': "No puedes agendar 2 o mas citas para el mismo dia a la misma hora"})
            # Se valida que el paciente no tenga 2 citas registradas el mismo dia con el mismo espeicailsta
            aux_citas = Cita.objects.filter(fecha=jd['fecha']).filter(id_paciente_id=jd['id_paciente']).filter(
                id_especialista_id=jd['id_especialista'])
            if aux_citas:
                return JsonResponse({'Error': True,
                                     'Descripcion': "No puedes agendar 2 o mas citas para el mismo dia con el mismo especialista"})
            cita = Cita.objects.create(fecha=jd['fecha'], hora=jd['hora'], estatus='P', motivo=jd['motivo'],
                                       id_especialista_id=jd['id_especialista'], id_paciente_id=jd['id_paciente'])
            cita.save()
            return JsonResponse({'Success': True})

    def obtener_horas_intermedias(request, horas_intermedias, inicio, fin, intervalo):
        # Se convierten los string a objetos datetime
        hora_inicio = datetime.strptime(inicio, "%H:%M")
        hora_final = datetime.strptime(fin, "%H:%M")
        # Calcular las horas intermedias en intervalos de 30 minutos
        intervalo = timedelta(minutes=intervalo)
        hora_actual = hora_inicio
        # Se agregan las horas intermedias mientras la hora actual sea menor a la hora final
        while hora_actual < hora_final:
            horas_intermedias.append(hora_actual.strftime("%H:%M"))
            hora_actual += intervalo
        return horas_intermedias

# Clase para visualizar las citas agendadas del paciente
class ListarCitas_Paciente(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(login_required(login_url='login'), name='dispatch')
    def get(self, request):
        usuario_id = Usuario.objects.get(id_usuario=request.user)
        try:
            paciente = Paciente.objects.filter(id_usuario=usuario_id).first()
        except Especialista.DoesNotExist:
            paciente = None
        citas = Cita.objects.filter(id_paciente=paciente.id)
        for cita in citas:
            cita.fecha = cita.fecha.strftime('%Y-%m-%d')
        """citas =  [{'especialista':'jose',
                    'hora': '14:00',
                    'servicio': 'primera visita',
                    'motivo': 'dolores de cabeza constante'},
                    {'especialista':'antonio',
                    'hora': '15:00',
                    'servicio': 'primera visita',
                    'motivo': 'dolores de cabeza constante'},]"""
        return render(request, "ventanas_paciente/lista_citas_paciente.html", {'citas': citas})

    @method_decorator(login_required, name='dispatch')
    def put(self, request, id):
        jd = json.loads(request.body)

        try:
            citas = Cita.objects.get(id=id)

            citas.estatus = jd['estatus']
            citas.save()
            return JsonResponse({'success': True})
        except Cita.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Cita no encontrada'})

# CLase para que el paciente envie una solicitud a un especialista
class Enviar_solicitud(View):
    @method_decorator(login_required, name='dispatch')
    def post(self, request, id_especialista):
        aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
        aux_paciente = Paciente.objects.get(id_usuario_id=aux_usuario.id)

        solicitud = Solicitudes.objects.create(id_especialista_id=id_especialista, id_paciente_id=aux_paciente.id,
                                               estatus='P')
        solicitud.save()

        return redirect('listarespecialistas')

# Clase para que el paciente guarde los datos de su ficha medica desde la ventana de perfil clinico
class Guardar_Ficha(View):
    @method_decorator(login_required, name="dispatch")
    def post(self, request):
        sexo = request.POST.get('sexo')
        estado_civil = request.POST.get('estado_civil')
        estilo_vida = request.POST.get('estilo_vida')
        peso = request.POST.get('peso')
        talla = request.POST.get('talla')

        aux_usuario = Usuario.objects.get(id_usuario=request.user.id)
        aux_paciente = Paciente.objects.get(id_usuario=aux_usuario.id)

        aux_paciente.genero = sexo
        aux_paciente.estado_civil = estado_civil
        aux_paciente.peso = peso
        aux_paciente.estilo_vida = estilo_vida
        aux_paciente.talla = talla

        aux_paciente.save()

        return redirect('perfil_clinico')