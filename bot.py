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
'reconexion' : configuracion('reconexion'),
'canal' : configuracion('canal'),
'nick' : configuracion('nick')
}

#servidor = configuracion('servidor')
#canal = configuracion('canal')
#nick = configuracion('nick')

## CONEXION ##
def conexion(SERVIDOR, PUERTO, CANAL, NICK):
   irc.connect((SERVIDOR, int(PUERTO)))                                     #conecta al servidor
   irc.send("USER  %s %s %s :El bot de RadioGNU r\n" % (NICK,NICK,NICK) ) #elige el usuario
   irc.send("NICK %s \r\n" % (NICK))            #selecciona el nick
   irc.send("PONG %s \r\n" % (SERVIDOR))           #entrada al canal
   irc.send("PRIVMSG nickserv :iNOOPE\r\n")     #autenticacion
   irc.send("JOIN %s \r\n" % (CANAL))           #entrada al canal
   global conectado
   conectado = True


## LECTURA DE DATOS ##
def lectura():
   ultimo_ping = time.time()
   limite = 5 * 60 # cinco minutos, pon esto como tu quieras
   while conectado:
      bufer = irc.recv ( 4096 )
      nick_msg = re.findall(':(.*?)!',bufer)
      buscar_msg = re.search('PRIVMSG\s#\w+\s:(.*?)$', bufer)

      kick = re.search('^:(.+?)\sKICK\s(#.*?)\s(.*?)\s(.*)$', bufer)
      #if bufer.split()[1] == '376':
      #   irc.send("JOIN %s \r\n" % (CANAL))
      #irc.send('PRIVMSG '+conf['canal']+' :'+msg+'\r\n')
      
      #if kick:
      #   print str(kick.group(1)).strip()
         
      
      #### SI EL MENSAJE HA SIDO DENTRO DEL CANAL ####
      if buscar_msg:
         msg = str(buscar_msg.group(1)).strip()
         #print 'EL MSG SI FUNCIONAAAAAAAAa' ## SI IMPRIME ESTO EStá bien
         
         #### SI SABEMOS EL NICK DE LA PERSONA QUE HA ESCRITO EL MENSAJE ####
         if nick_msg:
            nick = str(nick_msg[0]).strip()
            
            ####     LISTA DE FUNCIONES (EL CEREBRO DEL BOT)       ####
            if msg == '!sonando':
               peticion = urllib2.urlopen('http://radiognu.org/api/?no_cover')
               html = peticion.read()
               peticion.close()
               datos = simplejson.loads(html)
               if datos[u'isLive']:
                  irc.send('PRIVMSG '+conf['canal']+' :EN VIVO: «'+datos[u'show']+'» de '+datos[u'broadcaster']+' transmite'+datos[u'title']+'” de ‘'+datos[u'title']+'’ \r\n')
               else:
                  irc.send('PRIVMSG '+conf['canal']+' :SONANDO EN DIFERIDO: “'+datos[u'title']+'” de ‘'+datos[u'artist']+'’ del álbum «'+datos[u'album']+'» ('+datos[u'country']+', '+datos[u'year']+', '+datos[u'license'][u'shortname']+') \r\n')
               #SONANDO EN DIFERIDO: “Taifenü (Original Mix)” de ‘Paweldun’ del álbum «Vertiente EP» (Chile, 2013, CC BY-NC-ND 3.0)
            
            if msg == '!cuantos':
               peticion = urllib2.urlopen('http://radiognu.org/api/?no_cover')
               html = peticion.read()
               peticion.close()
               datos = simplejson.loads(html)
               archivo = open('cuantos.txt').readlines()
               palabra = randint(0, len(archivo)-1)
               r1 = re.sub('_X_', str(datos[u'listeners']), archivo[palabra])
               r2 = re.sub('____NICK____', nick, r1)
               irc.send('PRIVMSG '+conf['canal']+' :'+r2+'\r\n')
               
            if re.search('^!hablaclaro', msg):
               t = bufer.split(':!hablaclaro')
               to = t[1].strip()
               archivo = open('hablaclaro.txt').readlines()
               palabra = randint(0, len(archivo)-1)
               poema = str(archivo[palabra])
               irc.send('PRIVMSG '+conf['canal']+' :\x02\x038'+str(to)+': HABLA CLARO '+archivo[palabra])
            
            if msg == '!salir':
               irc.send('QUIT :init 0 \n')
               sys.exit()
               
      # Si la conexion se pierde
      if len(bufer) == 0:
         break
      print bufer
      # Si el nick esta en uso
      if bufer.find ( "Nickname is already in use" ) != -1:
         print '[[NICK "' + conf['nick'] + '" EN USO]]'
         exit()
      if bufer.find ('adios') != -1:
         irc.send('PRIVMSG #radiognu :Chao, nos vemos \r\n')

      # Ping Pong, asi que no nos desconectamos
      if bufer[0:4] == "PING":
         irc.send ( "PONG " + bufer.split() [ 1 ] + "\r\n" )
         ultimo_ping = time.time()
      if (time.time() - ultimo_ping) > limite:
         break


## EJECUCION ##
while 1:
   try:
      irc = None
      irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #configuracion del socket
      irc.settimeout(300)
      conectado = False
      conexion(conf['servidor'], conf['puerto'], conf['canal'], conf['nick'])
      lectura()
      print '[[CONEXIÓN CAIDA]]'
      if conf['reconexion'] == '1':
         print '[[RE-CONECTADO EN ' + conf['reconexion'] + ' SEGUNDO]]\n'
      else:
         print '[[RE-CONECTADO EN ' + conf['reconexion'] + ' SEGUNDOS]]\n'
      time.sleep(float(conf['reconexion']))
   except socket.error:
      print 'Error al conectar con el servidor: "' + conf['servidor'] + '"'
      if conf['reconexion'] == '1':
         print '[[RE-CONECTADO EN ' + conf['reconexion'] + ' SEGUNDO]]\n'
      else:
         print '[[RE-CONECTADO EN ' + conf['reconexion'] + ' SEGUNDOS]]\n'
      time.sleep(float(conf['reconexion']))
   except KeyboardInterrupt:
      exit()
   #except:
   #   print '[[CONEXIÓN CAIDA]]'
   #   print 'Re conectando en ' + conf['reconexion'] + ' segundos'
   #   time.sleep(float(conf['reconexion']))






"""

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
"""
