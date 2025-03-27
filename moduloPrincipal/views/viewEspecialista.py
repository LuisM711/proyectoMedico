from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from datetime import date, timezone, timedelta, datetime
from django.contrib.auth.models import User
from django.http.response import JsonResponse
import json
from moduloNutricion.urls import nutriologo
from django.forms.models import model_to_dict

from django.views.decorators.csrf import csrf_exempt
from moduloNutricion.models.modelMenuBien import Menu_Bien
from moduloPrincipal.models.__init__ import *
from moduloPrincipal.decorators import guest_or_login_required

# Clase para enviar al especialista a su ventana de inicio
class InicioEspecialista(View):
    @method_decorator(guest_or_login_required, name='dispatch')
    def get(self, request):        
        if request.session.get('guest'):
            return render(request, 'inicio.html',{"user_type": 'guest'})
        
        if (request.user.is_staff == 0):
            aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)

            if (aux_usuario.tipo == 'P'):
                return render(request, 'inicio.html',{"user_type": 'P'})

            return render(request, 'inicio.html',{"user_type": 'E'})

        else:
            return render(request, 'inicio.html',{"user_type": 'admin'})

# Clase para listar los pacientes de un especialista
class Pacientes(View):

    @method_decorator(login_required, name='dispatch')
    def get(self, request, id=0):
        # Validacion del tipo de usuario
        if (request.user.is_staff == 0):
            aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
            if (aux_usuario.tipo == 'P'):
                return render(request, 'inicio.html',{"user_type": 'P'})

            aux_especialista = Especialista.objects.get(id_usuario_id=aux_usuario.id)
            # Se obtienen las solicitudes del especialista
            solicitudes = Solicitudes.objects.filter(id_especialista=aux_especialista.id)

            # Se calcula la edad de los pacientes para poder mostrarla
            pacientes_con_edad = []
            for solicitud in solicitudes:
                fecha_act = date.today()
                fecha_na = solicitud.id_paciente.id_usuario.fecha_nacimiento
                edad = fecha_act.year - fecha_na.year - (
                            (fecha_act.month, fecha_act.day) < (fecha_na.month, fecha_na.day))
                pacientes_con_edad.append({'solicitud': solicitud, 'edad': edad})

            return render(request, 'ventanas_especialista/listar_pacientes.html', {'pacientes': pacientes_con_edad})

        else:
            return render(request, 'inicio.html',{"user_type": 'admin'})
        #Metodo put para actualizar el estado de una solicitud
    @method_decorator(login_required, name='dispatch')
    def put(self, request, id):
        jd = json.loads(request.body)
        try:
            solicitud = Solicitudes.objects.get(id=id)
            solicitud.estatus =jd['estatus']  
            solicitud.save()
            return JsonResponse({'success': True})
        except Solicitudes.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Solicitud no encontrada'})
# Clase para visualizar la ventana con los especialista que esta afuera de la pagina, antes de iniciar sesion

class Especialistas_Inicio(View):
    def get(self, request):
        # Se obtienen todos los especialistas y se hace la paginacion
        aux_especialistas = Especialista.objects.filter(estatus=1)
        page = request.GET.get('page', 1)
        try:
            paginator = Paginator(aux_especialistas, 3)
            especialistas = paginator.page(page)
        except:
            raise Http404

        return render(request, 'especialistas.html', {'entity': especialistas, 'paginator': paginator})

# CLase para validar el formulario de registro de especialista y registrarlo en la BD
class Registrarse_especialista(View):
    def post(self, request):
        username = request.POST.get('usuario_e')
        aux_usuarios = list(User.objects.filter(username=username).values())
        # Validacion para no registrar 2 o mas usuarios con el mismo nombre
        if len(aux_usuarios) > 0:
            aux_especialidades = list(Especialidades.objects.values())
            if len(aux_especialidades) > 0:
                datos = {"Especialidades": aux_especialidades,
                         'error': "Error, ya existe un registro con ese nombre de usuario"}
            else:
                datos = {'message': "No se encontraron especialidades",
                         'error': "Error, ya existe un registro con ese nombre de usuario"}
            return render(request, 'registro.html', {"datos": datos})

        correo = request.POST.get('correo_e')
        nombre = request.POST.get('nombre_e')
        apellido = request.POST.get('apellido_e')
        contra = request.POST.get('contra_e')
        fecha_nacim = request.POST.get('fecha_nacim_e')
        cedula = request.POST.get('cedula')
        info_adicional = request.POST.get('adicional')
        especialidad = request.POST.get('especialidad')

        # Se registra el usuario en la tabla auth_user de django que sirve para iniciar sesion
        user = User.objects.create_user(username, correo, contra)
        user.first_name = nombre
        user.last_name = apellido
        user.save()

        # Se realiza en registro en la tabla Usuario que almacenar datos generales independientemente si es Paciente o especialista
        usuario = Usuario.objects.create(id_usuario_id=user.id, fecha_nacimiento=fecha_nacim, foto='', tipo='E')
        usuario.save()
        # Se realiza el registro en la tabla de especialista
        # Se guarda un horario por defecto
        Especialista.objects.create(id_usuario_id=usuario.id, id_especialidad_id=especialidad, cedula=cedula,
                                    info_ad=info_adicional,
                                    horario='8:00-13:00, 14:00-17:00;8:00-13:00, 14:00-17:00;8:00-13:00, 14:00-17:00;8:00-13:00, 14:00-17:00;8:00-13:00, 14:00-17:00;8:00-13:00;',
                                    estatus="0")

        aux_especialidades = list(Especialidades.objects.values())
        datos = {"Especialidades": aux_especialidades}
        return render(request, 'registro.html', {"datos": datos})

# Clase para mostrar la interfaz de configuracion del especialista
class Configuracion_especialista(View):
    @method_decorator(login_required, name='dispatch')
    def get(self, request, message1="", message2=""):

        # Validacion de tipos de usuario
        if (request.user.is_staff == 0):
            aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
            if (aux_usuario.tipo == 'E'):
                aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
                aux_especialista = Especialista.objects.get(id_usuario_id=aux_usuario.id)
                # Se obtiene el horario y se divide en base al caracter ; para obtenener los datos de cada dia individualmente
                arreglo_horario = (aux_especialista.horario).split(";")
                json_horario = {"Lunes": arreglo_horario[0], "Martes": arreglo_horario[1],
                                "Miercoles": arreglo_horario[2], "Jueves": arreglo_horario[3],
                                "Viernes": arreglo_horario[4], "Sabado": arreglo_horario[5],
                                "Domingo": arreglo_horario[6]}
                # Se muestra un mensaje u otro dependiendo de si los cambios se realizaron correctamente
                if message1 == "error" and message2 == "exito":
                    datos = {'usuario': aux_usuario, 'nombre': request.user.username, 'correo': request.user.email,
                             'info_ad': aux_especialista.info_ad, 'cedula': aux_especialista.cedula,
                             'especialidad': aux_especialista.id_especialidad.nombre, "horario": json_horario,
                             'error': "Ese nombre de usuario ya esta ocupado",
                             'exito_info': "Informacion adicional actualizada"}
                elif message2 == "exito" and message2 == "exito":
                    datos = {'usuario': aux_usuario, 'nombre': request.user.username, 'correo': request.user.email,
                             'info_ad': aux_especialista.info_ad, 'cedula': aux_especialista.cedula,
                             'especialidad': aux_especialista.id_especialidad.nombre, "horario": json_horario,
                             'exito': "Nombre actualizado exitosamente",
                             'exito_info': "Informacion adicional actualizada"}
                else:
                    datos = {'usuario': aux_usuario, 'nombre': request.user.username, 'correo': request.user.email,
                             'info_ad': aux_especialista.info_ad, 'cedula': aux_especialista.cedula,
                             'especialidad': aux_especialista.id_especialidad.nombre, "horario": json_horario}

                return render(request, 'ventanas_especialista/configuracion_especialista.html', {"datos": datos})

            return redirect('inicio_paciente')

        else:
            return redirect('inicio_admin')

# Clase para actualizar el nombre de usuario del especialista
class CambiarUsernameEspecialista(View):
    @method_decorator(login_required, name='dispatch')
    def post(self, request):

        # Se obtiene el usuario de la tabla usuarios
        aux_user = Usuario.objects.get(id_usuario_id=request.user.id)
        # Se obtiene el especialista y se actualiza la info_ad sin requerir validaciones
        aux_especialista = Especialista.objects.get(id_usuario_id=aux_user.id)
        aux_especialista.info_ad = request.POST.get('info_ad')
        aux_especialista.save()

        # Se valida que no exista ningun usuario con el username que se quiere actualizar
        aux_usuario = list(User.objects.filter(username=request.POST.get('username')).values())

        if len(aux_usuario) > 0:

            return redirect('/configuracion/especialista/error/exito')
        else:
            user = User.objects.get(id=request.user.id)
            user.username = request.POST.get('username')
            user.save()

            return redirect('/configuracion/especialista/exito/exito')

# Clase para que el especialista pueda visualizar y registrar datos de una consulta medica
class ConsultaMedica(View):
    @method_decorator(login_required(login_url='login'), name='dispatch')
    def get(self, request, id):
        aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
        aux_especialista = Especialista.objects.get(id_usuario_id=aux_usuario.id)
        especialidad = Especialidades.objects.get(id=aux_especialista.id_especialidad.id)
        campos_excluir = ['_state','id', 'nombre', 'descripcion']
        especialidadJson = {key: value for key, value in vars(especialidad).items() if key not in campos_excluir and value == 'si'}
        #print(especialidadJson)
        cita = Cita.objects.get(id=id)
        pre_llenado = 'no'
        # Se valida que sea una cita confirmada
        if cita.estatus != 'C':
            return redirect('listarcitasespecialista')
        # Se valida que el la cita pertenezca al especialista
        aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
        aux_especialista = Especialista.objects.get(id_usuario_id=aux_usuario.id)
        #JEFE REVISE ESTE IF, NOSOTROS NO LE ENCONTRAMOS SENTIDO Y EN NUESTRAS PRUEBAS NI SIQUIERA ENTRA A ESTE BLOQUE DE CODIGO
        if aux_especialista.id != cita.id_especialista.id:
            # se valida que el especialista no sea enfermero, en ese caso si puede acceder, de lo contrario no
            if not (
                    aux_especialista.id_especialidad.exploracion_fisica == "si" and aux_especialista.id_especialidad.diagnostico_tratamiento == "no"):
                return redirect('listarcitasespecialista')
            else:
                pre_llenado = 'si'
        # Se obtienen los datos del usuario para mostrarlos en la interfaz
        #print("Es el mismo")
        paciente_obj = get_object_or_404(Paciente, id=cita.id_paciente.id)
        paciente_dict = model_to_dict(paciente_obj)
        paciente_json = json.dumps(paciente_dict)
        paciente = Paciente.objects.get(id=cita.id_paciente.id)
        fecha_act = date.today()
        fecha_na = paciente.id_usuario.fecha_nacimiento
        edad = fecha_act.year - fecha_na.year - ((fecha_act.month, fecha_act.day) < (fecha_na.month, fecha_na.day))
        peso = paciente.peso
        talla = paciente.talla
        if talla != 0:
            imc = peso / (talla ** 2)
            imc = round(imc, 2)
        else:
            imc = 0
        creatinina = paciente.creatinina
        if creatinina != 0:
            if paciente.genero == "M":
                fgm = (((140 - edad) * peso) / (72 * creatinina))
            else:
                fgm = (((140 - edad) * peso) / (72 * creatinina)) * 0.85
        else:
            fgm = 0
        AP_toxi = Toxicomania.objects.filter(id_paciente=paciente.id)
        AP_qui = Ant_quirurjicos.objects.filter(id_paciente=paciente.id)
        AP_tran = Ant_transfusionales.objects.filter(id_paciente=paciente.id)
        AP_al = Alergias.objects.filter(id_paciente=paciente.id)
        AP_vac = Vacunacion.objects.filter(id_paciente=paciente.id)
        AP = Ant_Patologicos.objects.filter(id_paciente=paciente.id)

        #JEFE TAMPOCO AQUI TIENE SENTIDO ESTO, NUNCA SE ENTRA AL IF, SIEMPRE ES AL ELSE, CREO QUE POR FUNCIONES QUE ELLOS PENSABAN IMPLEMENTAR
        #EN EL FUTURO
        # Se valida si la cita ya se prelleno
        aux_exp_fisica = Exploracion_fisica.objects.filter(id_cita_id=cita.id)

        if aux_exp_fisica.exists():
            print("hay")
         #   return render(request, 'layouts/consulta.html',
          #                {'paciente': paciente, 'edad': edad, 'imc': imc, 'fgm': fgm, 'AP_toxi': AP_toxi,
           #                'AP_qui': AP_qui, 'AP_tran': AP_tran, 'AP_vac': AP_vac, 'AP': AP, 'AP_al': AP_al,
            #               'ID_cita': id, "cita": cita, "pre_llenado": pre_llenado, "exp_fisica": aux_exp_fisica})
        #JEFE, ESTE ES EL CODIGO REALMENTE FUNCIONAL DE LA VISTA
        else:
            #print("no hay prelleno")
            return render(request, 'layouts/consulta.html',
                          {'paciente_json':paciente_json, 'paciente': paciente, 'edad': edad, 'imc': imc, 'fgm': fgm, 'AP_toxi': AP_toxi,
                           'AP_qui': AP_qui, 'AP_tran': AP_tran, 'AP_vac': AP_vac, 'AP': AP, 'AP_al': AP_al,
                           'ID_cita': id, "cita": cita, "pre_llenado": pre_llenado, 'especialidadJson': especialidadJson})

    # Funcion POST para realizar el registro de la consulta
    @method_decorator(login_required, name='dispatch')
    def post(self, request, id):
        cita = Cita.objects.get(id=id)

        # Se valida que si se haya registrado exploracion fisica
        if 'glucosa' in request.POST:
            # TABLA DE EXPLORACION FISICA
            paciente = Paciente.objects.get(id=cita.id_paciente.id)
            peso = paciente.peso
            talla = paciente.talla
            imc = request.POST.get('imc')
            creatinina = request.POST.get('creatinina')
            filtracion_glomerular = request.POST.get('filtracion_glomerular')
            glucosa = request.POST.get('glucosa')
            TA_sistolica = request.POST.get('tasis')
            TA_diastolica = request.POST.get('tadis')
            frecuencia_cardiaca = request.POST.get('frec')
            frecuencia_respiratoria = request.POST.get('frer')
            temperatura = request.POST.get('temp')
            descripcion_EXP = request.POST.get('desc')
            # GUARDAR TABLA
            exp_f = Exploracion_fisica.objects.create(id_cita=cita, peso=peso, talla=talla, glucosa=glucosa,
                                                      TA_sistolica=TA_sistolica, TA_diastolica=TA_diastolica,
                                                      frecuencia_cardiaca=frecuencia_cardiaca,
                                                      frecuencia_respiratoria=frecuencia_respiratoria,
                                                      temperatura=temperatura, descripcion=descripcion_EXP, imc=imc,
                                                      creatinina=creatinina,
                                                      filtracion_glomerular=filtracion_glomerular)
            exp_f.save()
            # SE ACTUALIZA EL VALOR DE CRATININA DEL PACIENTE
            paciente.creatinina = creatinina
            paciente.save()

        if 'diagnostico' in request.POST:
            # TABLA DIAGNOSTICO
            descripcion_DIA = request.POST.get('diagnostico')

            # TABLA TRATAMIENTO FARMACOLOGICO
            tipo_TRA1 = False
            descripcion_TRA1 = request.POST.get('tratamiento_far')

            # TABLA TRATAMIENTO NO FARMACOLOGICIO
            tipo_TRA2 = True
            descripcion_TRA2 = request.POST.get('tratamiento_nfar')

            diag = Diagnostico.objects.create(id_cita=cita, descripcion=descripcion_DIA, ruta_doc='')
            diag.save()
            tra1 = Tratamiento.objects.create(id_cita=cita, tipo=tipo_TRA1, descripcion=descripcion_TRA1)
            tra1.save()
            tra2 = Tratamiento.objects.create(id_cita=cita, tipo=tipo_TRA2, descripcion=descripcion_TRA2)
            tra2.save()

        if 'desaVerduras' in request.POST:

            #Inputs Desayuno
            desaVerduras = request.POST.get('desaVerduras')
            desaFrutas = request.POST.get('desaFrutas')
            desaCereales = request.POST.get('desaCereales')
            desaLeguminosas = request.POST.get('desaLeguminosas')
            desaOrigen = request.POST.get('desaOrigen')
            desaLeche = request.POST.get('desaLeche')
            desaGrasas = request.POST.get('desaGrasas')
            desaAzucares = request.POST.get('desaAzucares')

            #Inputs Comida
            comiVerduras = request.POST.get('comiVerduras')
            comiFrutas = request.POST.get('comiFrutas')
            comiCereales = request.POST.get('comiCereales')
            comiLeguminosas = request.POST.get('comiLeguminosas')
            comiOrigen = request.POST.get('comiOrigen')
            comiLeche = request.POST.get('comiLeche')
            comiGrasas = request.POST.get('comiGrasas')
            comiAzucares = request.POST.get('comiAzucares')

            #Inputs Cena
            cenaVerduras = request.POST.get('cenaVerduras')
            cenaFrutas = request.POST.get('cenaFrutas')
            cenaCereales = request.POST.get('cenaCereales')
            cenaLeguminosas = request.POST.get('cenaLeguminosas')
            cenaOrigen = request.POST.get('cenaOrigen')
            cenaLeche = request.POST.get('cenaLeche')
            cenaGrasas = request.POST.get('cenaGrasas')
            cenaAzucares = request.POST.get('cenaAzucares')

            #Inputs Colacion
            colaVerduras = request.POST.get('colaVerduras')
            colaFrutas = request.POST.get('colaFrutas')
            colaCereales = request.POST.get('colaCereales')
            colaLeguminosas = request.POST.get('colaLeguminosas')
            colaOrigen = request.POST.get('colaOrigen')
            colaLeche = request.POST.get('colaLeche')
            colaGrasas = request.POST.get('colaGrasas')
            colaAzucares = request.POST.get('colaAzucares')

            #Inputs Colacion 2
            colaVerduras2 = request.POST.get('colaVerduras2')
            colaFrutas2 = request.POST.get('colaFrutas2')
            colaCereales2 = request.POST.get('colaCereales2')
            colaLeguminosas2 = request.POST.get('colaLeguminosas2')
            colaOrigen2 = request.POST.get('colaOrigen2')
            colaLeche2 = request.POST.get('colaLeche2')
            colaGrasas2 = request.POST.get('colaGrasas2')
            colaAzucares2 = request.POST.get('colaAzucares2')

            #recomendacion
            recomendacion = request.POST.get('reco')

            menu = {

                'desayuno':{
                    'verduras': desaVerduras,
                    'frutas': desaFrutas,
                    'cereales': desaCereales,
                    'leguminosas': desaLeguminosas,
                    'origen': desaOrigen,
                    'leche': desaLeche,
                    'grasas': desaGrasas,
                    'azucares': desaAzucares

                },

                'comida':{
                    'verduras': comiVerduras,
                    'frutas': comiFrutas,
                    'cereales': comiCereales,
                    'leguminosas': comiLeguminosas,
                    'origen': comiOrigen,
                    'leche': comiLeche,
                    'grasas': comiGrasas,
                    'azucares': comiAzucares

                },

                'cena':{
                    'verduras': cenaVerduras,
                    'frutas': cenaFrutas,
                    'cereales': cenaCereales,
                    'leguminosas': cenaLeguminosas,
                    'origen': cenaOrigen,
                    'leche': cenaLeche,
                    'grasas': cenaGrasas,
                    'azucares': cenaAzucares

                },

                'colacion':{
                    'verduras': colaVerduras,
                    'frutas': colaFrutas,
                    'cereales': colaCereales,
                    'leguminosas': colaLeguminosas,
                    'origen': colaOrigen,
                    'leche': colaLeche,
                    'grasas': colaGrasas,
                    'azucares': colaAzucares

                },

                 'colacion2':{
                    'verduras': colaVerduras2,
                    'frutas': colaFrutas2,
                    'cereales': colaCereales2,
                    'leguminosas': colaLeguminosas2,
                    'origen': colaOrigen2,
                    'leche': colaLeche2,
                    'grasas': colaGrasas2,
                    'azucares': colaAzucares2
                },
                 'recomendacion': recomendacion
            }
            paciente = Paciente.objects.get(id=cita.id_paciente.id)
            aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
            aux_especialista = Especialista.objects.get(id_usuario_id=aux_usuario.id)
            menuString = json.dumps(menu)
            #print(menuString)
            auxMenuBien=Menu_Bien.objects.create(id_cita=cita,especialista=aux_especialista,paciente=paciente,menu=menuString)
            auxMenuBien.save()
        # solo se se cambia el estatus de la cita cuando no se esta pre llenando por una enfermera
        #if request.POST.get('pre_llenado') == "no":
        cita.estatus = 'A'
        cita.save()

        # REDIRIGE AL LISTADO DE CITAS
        return redirect('listarcitasespecialista')

# Clase para visualizar una consulta medica sin poder editarla
class VisualizarConsulta(View):
    @method_decorator(login_required, name='dispatch')
    def get(self, request, id):
        cita = Cita.objects.get(id=id)

        # Se valida que sea una cita ya atendida
        if cita.estatus != 'A':
            return redirect('listarcitasespecialista')
        # Se valida que el la cita pertenezca al especialista
        aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
        aux_especialista = Especialista.objects.get(id_usuario_id=aux_usuario.id)
        if aux_especialista.id != cita.id_especialista.id:
            return redirect('listarcitasespecialista')

        # Se obtienen los datos del paciente para mostrarlos en la ventana
        paciente = Paciente.objects.get(id=cita.id_paciente.id)
        fecha_act = date.today()
        fecha_na = paciente.id_usuario.fecha_nacimiento
        edad = fecha_act.year - fecha_na.year - ((fecha_act.month, fecha_act.day) < (fecha_na.month, fecha_na.day))
        
        #Obtenemos las especialidades en SI del especialista de dicha cita
        data={}
        if cita.diagnosticos.exists():
            aux_diagno=Diagnostico.objects.get(id_cita_id=cita.id)
            data.update({'diagnostico':aux_diagno})
        
        if cita.exploraciones.exists():
            aux_explo= Exploracion_fisica.objects.get(id_cita_id=cita.id)
            data.update({'exploracionfisica':aux_explo})

        if cita.menus.exists():
            auxMenu=Menu_Bien.objects.get(id_cita=cita.id)
            auxMenu2=auxMenu.menu
            auxMenu3 = json.loads(auxMenu2)
            data.update({'menu':auxMenu3})
        #("es la visualizacion")
        #print(auxMenu2)
        #data={'exploracionfisica': aux_explo, 'diagnostico': aux_diagno}

        datosPaciente={'paciente': paciente,
                       'edad': edad,
                       'diagnostico': Diagnostico.objects.get(id_cita_id=id),
                       'tratamiento_farmacologico': Tratamiento.objects.get(id_cita_id=id, tipo=0),
                       'tratamiento_no_farmacologico': Tratamiento.objects.get(id_cita_id=id, tipo=1),
                       'cita': cita,
                       'ID_cita': cita.id,
                       'AP_toxi': Toxicomania.objects.filter(id_paciente=paciente.id),
                       'AP_qui': Ant_quirurjicos.objects.filter(id_paciente=paciente.id),
                       'AP_tran': Ant_transfusionales.objects.filter(id_paciente=paciente.id),
                       'AP_al': Alergias.objects.filter(id_paciente=paciente.id),
                       'AP': Ant_Patologicos.objects.filter(id_paciente=paciente.id)}

        # SI el especialista no registra exploracion fisica, ese datos no se busca ni envia
        #if (aux_especialista.id_especialidad.exploracion_fisica == "no"):
        #print(data)
        return render(request, "ventanas_especialista/visualizar_consulta.html", {'datosPaciente': datosPaciente,
                                                                                        'data': data})
        #else:
            #try:
             #   exploracion_fisica = Exploracion_fisica.objects.get(id_cita_id=id)
            #except Exploracion_fisica.DoesNotExist:
                #print("No se encontro la exploracion fisica")
                #exploracion_fisica = None
            #return render(request, "ventanas_especialista/visualizar_consulta.html", {'paciente': paciente,
            #                                                                          'edad': edad,
             #                                                                         'AP_toxi': AP_toxi,
              #                                                                        'AP_qui': AP_qui,
               #                                                                       'AP_tran': AP_tran,
                #                                                                      'AP_vac': AP_vac,
                 #                                                                     'AP': AP, 'AP_al': AP_al,
                  #                                                                    'ID_cita': id,
                   #                                                                   "cita": cita,
                    #                                                                  "exploracion_fisica": exploracion_fisica,
                     #                                                                 "diagnostico": diagnostico,
                      #                                                                "tratamiento_farmacologico": tratamiento_farmacologico,
                       #                                                               "tratamiento_no_farmacologico": tratamiento_no_farmacologico}
# Clase para visualizar las citas agendadas del especialista
class ListarCitas_Especialista(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(login_required(login_url='login'), name='dispatch')
    def get(self, request, id=0):
        usuario_id = Usuario.objects.get(id_usuario=request.user)

        try:
            especialista = Especialista.objects.filter(id_usuario=usuario_id).first()
        except Especialista.DoesNotExist:
            especialista = None

        aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)
        aux_especialista = Especialista.objects.get(id_usuario=aux_usuario.id)
        especialidad = Especialidades.objects.get(id=aux_especialista.id_especialidad.id)

        # Caso de los especialistas que solo registran exploracion fisica
        if especialidad.exploracion_fisica == "si" and especialidad.diagnostico_tratamiento == "no":
            fecha_actual = date.today()
            citas = Cita.objects.filter(fecha__gt=fecha_actual, estatus='C')
            return render(request, "ventanas_especialista/lista_citas_especialista.html", {'citas': citas})
        else:
            citas = Cita.objects.filter(id_especialista=especialista.id)

        for cita in citas:
            cita.fecha = cita.fecha.strftime('%Y-%m-%d')
        """citas =  [{'paciente':'jose',
                    'hora': '14:00',
                    'servicio': 'primera visita',
                    'motivo': 'dolores de cabeza constante'},
                    {'especialista':'antonio',
                    'hora': '15:00',
                    'servicio': 'primera visita',
                    'motivo': 'dolores de cabeza constante'},]"""
        return render(request, "ventanas_especialista/lista_citas_especialista.html", {'citas': citas})

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

# Clase para que el especialista visualice la informacion de un paciente que le mando solicitud
class Informacion_paciente(View):
    @method_decorator(login_required, name="dispatch")
    def get(self, request, id_paciente=0):

        # Validacion de tipos de usaurio
        if (request.user.is_staff == 0):
            aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)

            if (aux_usuario.tipo == 'E'):
                # Se valida que el paciente tenga una solicitud enviada ya aceptada del especialista
                aux_especialista = Especialista.objects.get(id_usuario_id=aux_usuario.id)
                aux_solicitud = Solicitudes.objects.filter(id_paciente_id=id_paciente).filter(
                    id_especialista_id=aux_especialista.id)

                if not aux_solicitud:
                    return redirect('listarpacientes')

                # Se valida el estatus de la solicitud para redirigir a otra ventana en caso de no ser el correcto
                for elemento in aux_solicitud:
                    if elemento.estatus == 'R':
                        return redirect('listarpacientes')

                    if elemento.estatus == 'A':
                        return redirect('/informacion/paciente/full/' + str(id_paciente))

                paciente = Paciente.objects.get(id=id_paciente)
                fecha_act = date.today()
                fecha_na = paciente.id_usuario.fecha_nacimiento
                edad = fecha_act.year - fecha_na.year - (
                            (fecha_act.month, fecha_act.day) < (fecha_na.month, fecha_na.day))
                peso = paciente.peso
                talla = paciente.talla

                if peso != 0:
                    imc = peso / (talla ** 2)
                    imc = round(imc, 2)
                else:
                    imc = 0

                creatinina = paciente.creatinina
                if creatinina != 0:
                    if paciente.genero == "M":
                        fgm = round((((140 - edad) * peso) / (72 * creatinina)))

                    else:
                        fgm = round((((140 - edad) * peso) / (72 * creatinina)) * 0.85)
                else:
                    fgm = 0

                toxicomanias = Toxicomania.objects.filter(id_paciente=paciente.id)
                ant_patologicos = Ant_Patologicos.objects.filter(id_paciente=paciente.id)
                ant_quirurjicos = Ant_quirurjicos.objects.filter(id_paciente=paciente.id)
                ant_transfusionales = Ant_transfusionales.objects.filter(id_paciente=paciente.id)
                alergias = Alergias.objects.filter(id_paciente=paciente.id)
                vacunas = Vacunacion.objects.filter(id_paciente=paciente.id)
                return render(request, 'ventanas_especialista/info_paciente.html', {'paciente': paciente,
                                                                                    'edad': edad,
                                                                                    'imc': imc,
                                                                                    'fgm': fgm,
                                                                                    'toxicomanias': toxicomanias,
                                                                                    'ant_patologicos': ant_patologicos,
                                                                                    'ant_quirurjicos': ant_quirurjicos,
                                                                                    'ant_transfusionales': ant_transfusionales,
                                                                                    'alergias': alergias,
                                                                                    'vacunas': vacunas})
            else:
                return redirect('inicio_paciente')
        else:
            return redirect('inicio_admin')

# Clase para que el especialista visualice la informacion de un paciente al que ya le acepto una solicitd, se diferencia en que en este caso puede editar su perfil clinico y visualizar sus citas
class Informacion_Paciente_full(View):
    @method_decorator(login_required, name="dispatch")
    def get(self, request, id):

        # Validacion de tipos de usaurio
        if (request.user.is_staff == 0):
            aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)

            if (aux_usuario.tipo == 'E'):

                especialista = Especialista.objects.get(id_usuario=aux_usuario.id)
                # Se valida que el paciente tenga una solicitud enviada ya aceptada del especialista
                aux_solicitud = Solicitudes.objects.filter(id_paciente_id=id).filter(id_especialista_id=especialista.id)

                if not aux_solicitud:
                    return redirect('listarpacientes')

                # Se valida el estatus de la solicitud para redirigir a otra ventana en caso de no ser el correcto
                for elemento in aux_solicitud:
                    if elemento.estatus == 'R':
                        return redirect('listarpacientes')

                    if elemento.estatus == 'P':
                        return redirect('/informacion/paciente/' + str(id))

                paciente = Paciente.objects.get(id=id)
                fecha_act = date.today()
                fecha_na = paciente.id_usuario.fecha_nacimiento
                edad = fecha_act.year - fecha_na.year - (
                            (fecha_act.month, fecha_act.day) < (fecha_na.month, fecha_na.day))
                peso = paciente.peso
                talla = paciente.talla

                if peso != 0:
                    imc = peso / (talla ** 2)
                    imc = round(imc, 2)
                else:
                    imc = 0

                creatinina = paciente.creatinina
                if creatinina != 0:
                    if paciente.genero == "M":
                        fgm = round(((140 - edad) * peso) / (72 * creatinina))

                    else:
                        fgm = round((((140 - edad) * peso) / (72 * creatinina)) * 0.85)
                else:
                    fgm = 0

                toxicomanias = Toxicomania.objects.filter(id_paciente=paciente.id)
                ant_patologicos = Ant_Patologicos.objects.filter(id_paciente=paciente.id)
                ant_quirurjicos = Ant_quirurjicos.objects.filter(id_paciente=paciente.id)
                ant_transfusionales = Ant_transfusionales.objects.filter(id_paciente=paciente.id)
                alergias = Alergias.objects.filter(id_paciente=paciente.id)
                vacunas = Vacunacion.objects.filter(id_paciente=paciente.id)

                citas = Cita.objects.filter(id_paciente=id).filter(id_especialista=especialista.id).exclude(
                    estatus="B").exclude(estatus="P").order_by('-fecha')
                return render(request, 'ventanas_especialista/info_paciente_full.html', {'paciente': paciente,
                                                                                         'edad': edad,
                                                                                         'imc': imc,
                                                                                         'fgm': fgm,
                                                                                         'toxicomanias': toxicomanias,
                                                                                         'ant_patologicos': ant_patologicos,
                                                                                         'ant_quirurjicos': ant_quirurjicos,
                                                                                         'ant_transfusionales': ant_transfusionales,
                                                                                         'alergias': alergias,
                                                                                         'vacunas': vacunas,
                                                                                         'citas': citas})
            else:
                return redirect('inicio_paciente')
        else:
            return redirect('inicio_admin')