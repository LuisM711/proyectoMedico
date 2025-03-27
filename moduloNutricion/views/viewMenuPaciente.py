from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from moduloNutricion.models.modelMenuBien import Menu_Bien
from moduloPrincipal.models.modelUsuario import Usuario
from moduloPrincipal.models.modelPaciente import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
class Menu_paciente(View):
    @method_decorator(login_required(login_url='login'), name='dispatch')
    def get(self, request):
        auxUsuario = Usuario.objects.get(id_usuario=request.user)
        pacienteBien = Paciente.objects.get(id_usuario=auxUsuario)
        auxMenu = Menu_Bien.objects.filter(paciente=pacienteBien).order_by('-fecha').first()
        #Si encuentra un registro de asignacion de menu asignado a ese paciente
        if auxMenu:
            #Se jala unicamente el menu, que ha sido guardado como un json
            auxMenu2 = auxMenu.menu
            #print(auxMenu2)
            menuPaciente = json.loads(auxMenu2)
            data={
                'paciente': pacienteBien,
                'menu': menuPaciente
            }
        else:
            data={
                'paciente': pacienteBien,
                'menu':None
            }
        return render(request,'menuPaciente.html', data)