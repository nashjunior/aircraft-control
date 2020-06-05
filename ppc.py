import threading
import time
import datetime
import argparse
import random
import sys
from queue import Queue

num_aviao_decolar = 0
num_aviao_aterrisar = 0
total_aviao = 1
tempo_decolar = None
tempo_aterrisar = None
tempo_max_ar = None
fila_decolar = []
fila_aterrisar = []
lock=threading.Lock()
prioridade_aviao_aterrisar = "baixa"
arquivo_aviao = open("avioes.txt","w")
#------------------------------------------------
class Aircraft():
	def __init__(self,numero_aviao,hora_criada):
		self.numero_aviao = numero_aviao
		self.hora_criada = hora_criada
		self.hora_inicio = None
		self.hora_fim = None			

class Aircraft_Airspace(Aircraft):
	def __init__(self,numero_aviao,hora_criada):
		super().__init__(numero_aviao, hora_criada)
		self.hora_criada = hora_criada
		self.aterrisou = False
		print ("Aviao ",self.numero_aviao,"criado pelo espaco aereo as",self.hora_criada)

	def verificar_pista(self):
		global lock,tempo_max_ar,tempo_aterrisar
		threading.Timer(tempo_max_ar-tempo_decolar,self.verificar_situacao_aviao).start()
		while True:
			if lock.locked():
				continue
			if verificar_prioridade()==True:
				Pista().utilizar_pista(True)
				break
	def verificar_situacao_aviao(self):
		global prioridade_aviao_aterrisar
		if not self.aterrisou:
			threading.Timer(tempo_decolar+1,self.verificar_aviao_caiu).start()
			print ("*****Aviao ",self.numero_aviao,"ira adquirir prioridade na pista quando ficar livre para nao cair")
			prioridade_aviao_aterrisar = "alta"

	def verificar_aviao_caiu(self):
		global fila_aterrisar,prioridade_aviao_aterrisar,tempo_aterrisar
		if not self.aterrisou:
			global arquivo_aviao
			self.hora_fim = datetime.datetime.now().strftime("%H:%M:%S")
			time.sleep(tempo_aterrisar-1)
			print ("**OBS: aviao ",self.numero_aviao,"caiu as ",self.hora_fim)
			prioridade_aviao_aterrisar = "baixa"
			del fila_aterrisar[0]
			string_aviao = "Aviao ",str(self.numero_aviao),": foi criado as ",str(self.hora_criada)," e caiu as ",str(self.hora_fim),"\n"
			arquivo_aviao.writelines(str(string_aviao))

class Aircraft_airport(Aircraft):
	def __init__(self,numero_aviao,hora_criada):
		super().__init__(numero_aviao,hora_criada)
		print ("Aviao ",self.numero_aviao,"criado pelo aeroporto as",self.hora_criada)

	def verificar_pista(self):
		global lock
		while True:
			if lock.locked():
				continue
			if verificar_prioridade()==False:
				Pista().utilizar_pista(False)
				break
#--------------------------------------------------
class Pista():
	def utilizar_pista(self,aterrisar):
		global lock,fila_decolar,fila_aterrisar,tempo_aterrisar,tempo_decolar,prioridade_aviao_aterrisar,arquivo_aviao
		with lock:
			print ("________________________________________________________")
			if not aterrisar:
				if threading.active_count()>2:
					time.sleep(tempo_decolar)
				hora_ir_decolar = datetime.datetime.now().strftime("%H:%M:%S")
				print ("*Um aviao esta indo decolar as ",hora_ir_decolar)
				aviao = fila_decolar[0]
				time.sleep(tempo_decolar)
				del fila_decolar[0]
				aviao.hora_fim = datetime.datetime.now().strftime("%H:%M:%S")
				print ("O aviao ",aviao.numero_aviao, "concluiu a sua decolagem as ",aviao.hora_fim)
				aviao.hora_inicio = hora_ir_decolar
				string_aviao="Aviao ",str(aviao.numero_aviao),": criado as ",str(aviao.hora_criada),", iniciou a decolagem as",str(aviao.hora_inicio),"e terminou a decolagem as ",str(aviao.hora_fim),"\n"
				arquivo_aviao.writelines(string_aviao)

			else:
				hora_ir_aterrisar = datetime.datetime.now().strftime("%H:%M:%S")
				print ("*Um aviao esta indo aterrisar as ",hora_ir_aterrisar)
				aviao = fila_aterrisar[0]
				aviao.aterrisou=True
				prioridade_aviao_aterrisar="baixa"
				time.sleep(tempo_aterrisar)
				del fila_aterrisar[0]
				aviao.hora_fim = datetime.datetime.now().strftime("%H:%M:%S")
				aviao.aterrisou = True
				print ("O aviao ",aviao.numero_aviao, "concluiu a sua aterrisagem as ",aviao.hora_fim)
				aviao.hora_inicio = hora_ir_aterrisar
				string_aviao="Aviao ",str(aviao.numero_aviao),": criado as ",str(aviao.hora_criada),", iniciou a aterrisagem as",str(aviao.hora_inicio),"e terminou a aterrisagem as ",str(aviao.hora_fim),"\n"
				arquivo_aviao.writelines(string_aviao)
			print ("________________________________________________________")
			print ("Existem ",len(fila_decolar),"para decolar e ",len(fila_aterrisar)," para aterrisar\n________________________________________________________\n")
			if len(fila_decolar)==0 and len(fila_aterrisar)==0:
				sys.exit()
#--------------------------------------------------------------------------
def verificar_prioridade():
	global fila_decolar,fila_aterrisar,prioridade_aviao_aterrisar
	if prioridade_aviao_aterrisar=="baixa":
		if len(fila_decolar)>0 or len(fila_aterrisar)>0:
			if len(fila_decolar)>0:
				if len(fila_aterrisar)==0:
					return False
				elif len(fila_aterrisar)>0:
					if len(fila_decolar)%3==0:
						return False
					else:
						return True
			if len(fila_aterrisar)>0:
				return True
	else:
		return True

def arguments():
	global tempo_decolar,tempo_aterrisar,tempo_max_ar
	parser = argparse.ArgumentParser(prog="Controle de Trafego Aereo",usage='%(prog)s [options]')
	parser.add_argument('--timecriar','-tc',type=int,required=True,help='Tempo para cada aviao ser criado')
	parser.add_argument('--numdecol','-nd',type=int,required=True,help='Quantidade de avioes decolando')
	parser.add_argument('--timedecol','-td',type=int,required=True,help='Tempo de decolagem do aviao')
	parser.add_argument('--numaterr','-na',type=int,required=True,help='Quantidade de avioes aterrisando')
	parser.add_argument('--timeaterr','-ta',type=int,required=True,help='Tempo de aterrisagem do aviao')
	parser.add_argument('--timemax','-tm',type=int,required=True,help='Tempo maximo do aviao no espaco aereo')
	args = parser.parse_args()
	tempo_decolar = args.timedecol
	tempo_aterrisar = args.timeaterr
	tempo_max_ar = args.timemax
	criar_aviao(args.numdecol,args.numaterr,args.timecriar)

def aviao_espaco_aereo():
	global total_aviao,fila_aterrisar
	aviao=Aircraft_Airspace(total_aviao,datetime.datetime.now().strftime("%H:%M:%S"))
	fila_aterrisar.append(aviao)
	total_aviao+=1
	aviao.verificar_pista()

def aviao_aeroporto():
	global fila_decolar,total_aviao
	aviao=Aircraft_airport(total_aviao,datetime.datetime.now().strftime("%H:%M:%S"))
	fila_decolar.append(aviao)
	total_aviao+=1
	aviao.verificar_pista()

def criar_aviao(qtd_decolar,qtd_aterrisar,time_create):
	global num_aviao_decolar,num_aviao_aterrisar,total_aviao,fila_decolar,fila_aterrisar

	tempo_criar = threading.Timer(time_create,criar_aviao,[qtd_decolar,qtd_aterrisar,time_create])
	if num_aviao_decolar < qtd_decolar and num_aviao_aterrisar < qtd_aterrisar:
		tempo_criar.start()
		if random.choice([True,False]):
			if len(fila_aterrisar)%4==3:
				print ("Aviao nao pode ser criado no espaco aereo... Fila cheia\n")
			else:
				num_aviao_aterrisar+=1
				aviao_espaco_aereo()
		else:
			if len(fila_decolar)%4==3:
				print ("Aviao nao pode ser criado no aeroporto... Fila cheia\n")
			else:
				num_aviao_decolar +=1
				aviao_aeroporto()
	elif num_aviao_decolar == qtd_decolar and num_aviao_aterrisar < qtd_aterrisar:
		if num_aviao_aterrisar+1>=qtd_aterrisar:
			if len(fila_aterrisar)%4==3:
				print ("Aviao nao pode ser criado no espaco aereo... Fila cheia\n")
				tempo_criar.start()
			else:
				tempo_criar.cancel()
				num_aviao_aterrisar+=1
				aviao_espaco_aereo()
		else:
			tempo_criar.start()
			if len(fila_aterrisar)%4==3:
				print ("Aviao nao pode ser criado no espaco aereo... Fila cheia\n")
			else:
				num_aviao_aterrisar +=1
				aviao_espaco_aereo()

	elif num_aviao_aterrisar == qtd_aterrisar and num_aviao_decolar < qtd_decolar:
		if num_aviao_decolar+1>=qtd_decolar:
			if len(fila_decolar)%4==3:
				print ("Aviao nao pode ser criado no aeroporto... Fila cheia\n")
				tempo_criar.start()
			else:
				tempo_criar.cancel()
				num_aviao_decolar+=1
				aviao_aeroporto()
		else:
			tempo_criar.start()
			if len(fila_decolar)%4==3:
				print ("Aviao nao pode ser criado... Fila cheia\n")
			else:
				num_aviao_decolar +=1
				aviao_aeroporto()
	elif num_aviao_decolar == qtd_decolar and num_aviao_aterrisar == qtd_aterrisar:
		while len(fila_decolar)>0 and len (fila_aterrisar)>0:
			continue
		else:
			sys.exit()
arguments()

