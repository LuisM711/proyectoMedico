from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from datetime import date, timezone, timedelta, datetime
from moduloPrincipal.models.__init__ import *
# Clase para visualizar la interfaz de perfil clinicio por parte del paciente
class Perfil_Clinico(View):
    @method_decorator(login_required(login_url='login'), name='dispatch')
    def get(self, request):
        # Validacion de tipos de usaurio
        if (request.user.is_staff == 0):
            aux_usuario = Usuario.objects.get(id_usuario_id=request.user.id)

            if (aux_usuario.tipo == 'P'):
                # Se obtiene la informaicon que se muestra en la interfaz
                aux_usuario = Usuario.objects.get(id_usuario=request.user.id)
                paciente = Paciente.objects.get(id_usuario=aux_usuario.id)
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
                return render(request, 'ventanas_paciente/perfil_clinico.html', {'paciente': paciente,
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
                return redirect('inicio_especialista')
        else:
            return redirect('inicio_admin')