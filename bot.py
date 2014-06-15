# -*- coding: utf-8 -*-
import socket
import sys
import re
import time
import threading
import urllib2
import simplejson
from random import randint
from pt import *
reload(sys)
sys.setdefaultencoding('utf-8')

## CONFIGURACIONES ##
conf = {
'servidor' : configuracion('servidor'),
'puerto' : configuracion('puerto'),
'canal' : configuracion('canal'),
'nick' : configuracion('nick')
}

#servidor = configuracion('servidor')
#canal = configuracion('canal')
#nick = configuracion('nick')

## CONEXION ##
def conexion():
   irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #configuracion del socket
   irc.connect((conf['servidor'], int(conf['puerto'])))                                                     #conecta al servidor
   irc.send("USER "+ conf['nick'] +" "+ conf['nick'] +" "+ conf['nick'] +" :El bot de RadioGNU\n") #elige el usuario
   irc.send("NICK "+ conf['nick'] +"\n")                            #selecciona el nick
   irc.send("PRIVMSG nickserv :iNOOPE\r\n")    #autenticacion
   irc.send("JOIN "+ conf['canal'] +"\n")        #entrada al canal
   return irc

## LECTURA DE DATOS ##
def lectura():
   global irc
   text=irc.recv(2040)  #recibe el texto
   print text   #muestra el texto en la consola
   nick_msg = re.findall(':(.*?)!',text)
   buscar_msg = re.search('PRIVMSG\s#\w+\s:(.*?)$', text)
   if nick_msg:
      #print format(nick_msg.group(0))
      nick = nick_msg[0]

   if text.find('PING') != -1:                          #revisa si es un 'PING'
      irc.send('PONG ' + text.split() [1] + '\r\n') #le envia un 'PONG' al servidor (para evitar ping timeout)

   if buscar_msg:
      msg = str(buscar_msg.group(1))
      if text.find(':!sonando') !=-1:
         peticion = urllib2.urlopen('http://radiognu.org/api/?no_cover')
         html = peticion.read()
         peticion.close()
         datos = simplejson.loads(html)
         if datos[u'isLive']:
            irc.send('PRIVMSG '+conf['canal']+' :EN VIVO: «'+datos[u'show']+'» de '+datos[u'broadcaster']+' transmite'+datos[u'title']+'” de ‘'+datos[u'title']+'’ \r\n')
         else:
            irc.send('PRIVMSG '+conf['canal']+' :SONANDO EN DIFERIDO: “'+datos[u'title']+'” de ‘'+datos[u'artist']+'’ del álbum «'+datos[u'album']+'» ('+datos[u'country']+', '+datos[u'year']+', '+datos[u'license'][u'shortname']+') \r\n')
         #SONANDO EN DIFERIDO: “Taifenü (Original Mix)” de ‘Paweldun’ del álbum «Vertiente EP» (Chile, 2013, CC BY-NC-ND 3.0)

      if text.find(':!cuantos') !=-1:
         peticion = urllib2.urlopen('http://radiognu.org/api/?no_cover')
         html = peticion.read()
         peticion.close()
         datos = simplejson.loads(html)
         archivo = open('cuantos.txt').readlines()
         palabra = randint(0, len(archivo)-1)
         r1 = re.sub('_X_', str(datos[u'listeners']), archivo[palabra])
         r2 = re.sub('____NICK____', nick, r1)
         irc.send('PRIVMSG '+conf['canal']+' :'+r2+'\r\n')

      if text.find(':!hablaclaro ') !=-1:
         t = text.split(':!hablaclaro')
         to = t[1].strip()
         archivo = open('hablaclaro.txt').readlines()
         palabra = randint(0, len(archivo)-1)
         poema = str(archivo[palabra])
         irc.send('PRIVMSG '+conf['canal']+' :\x02\x038'+str(to)+': HABLA CLARO '+archivo[palabra])

      if text.find(':!salir') !=-1:
         irc.send('QUIT :init 0 \n')
         sys.exit()

try:
   print "Conectando a: " + conf['servidor']
   irc = conexion()
except:
   print 'Error al conectar con el servidor: "' + conf['servidor'] + '"'

while 1:
   lectura()
