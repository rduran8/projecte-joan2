#!/usr/bin/env python3
# python3
# -*- coding: utf-8 -*-
import csv 
import os 
import mysql.connector 
import getpass 
import socket 
import crypt
#Connexió a la base de dades.
try:
    mydb = mysql.connector.connect(host="172.24.10.1", #3306
        user="grup2",
        passwd="patata",
        database='dualRogerJordiDavid')
except mysql.connector.Error:
    print("Error de la base de dades")
    input("Enter per continuar...")
    
def connectarBD():
    global mydb
    mydb.close()
    try:
        mydb = mysql.connector.connect(host="172.24.10.1", #3306
        user="grup2",
        passwd="patata",
        database='dualRogerJordiDavid')
    except mysql.connector.Error:
        print("Error de la base de dades")
        input("Enter per continuar...")

user = ""
#Mostra el ranking de puntuacions dels grups.
def ranking():
    connectarBD()
    os.system('clear')
    retorn = ""
    sql_select_Query = "select usuaris.usuaris,puntuacions.puntuacions from puntuacions,usuaris where puntuacions.idusuaris = usuaris.idusuaris"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query, ())
    llista = cursor.fetchall()
    print("Grup\tPuntuació")
    for x in range(0,len(llista)):
         text = llista[x]
         print(str(text[0]) + "\t" + str(text[1]).rjust(9))
    input("Enter per continuar...")
#Comprova si la prova s'ha respost.
def comprovarProva(grup):
    sql_select_Query = "select * from completat where grup = %s and prova = %s"
    cursor = mydb.cursor()
    val = (user,grup,)
    cursor.execute(sql_select_Query, val)
    llista = cursor.fetchall()
    retorn = len(llista)+1
    return retorn;
#Mostra la puntuació del grup.
def mostrarPuntuacio():
    retorn = ""
    sql_select_Query = "select puntuacions from puntuacions where idusuari = %s"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query, (user,))
    z = cursor.fetchall()
    retorn = str(z[0])
    retorn = retorn[1:len(retorn) - 2]
    return retorn
#Actualitzar notificacions def socketResposta():
#    HOST = '127.0.0.1' # The server's hostname or IP address PORT = 
#    65432 # The port used by the server try:
#        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#            s.connect((HOST, PORT)) s.sendall(b'Hello, world') data = 
#    s.recv(1024) s.close() except:
#        print("No s'ha trobat cap programa de notificaccions en 
#execució.") Actualitza la puntuació d'un grup cada vegada que respon 
#correctament a una prova.
def actualitzarPuntuacio(grup,prova):
    sql_select_Query = "select puntuacions.puntuacions,puntuacions.idusuaris from puntuacions,usuaris where puntuacions.idusuaris = usuaris.idusuaris and usuaris.usuaris = %s"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query, (user,))
    z = cursor.fetchall()
    cursorcomp = mydb.cursor()
    sql = "INSERT INTO completat (grup, prova,repte) VALUES (%s, %s, %s)"
    val = (user,grup,prova,)
    cursorcomp.execute(sql, val)
    mydb.commit()
    if len(z) <= 0:
        sql_select_Query = "select idusuaris from usuaris where usuaris = %s"
        cursor = mydb.cursor()
        cursor.execute(sql_select_Query, (user,))
        y = cursor.fetchall()
        p = y[0]
        id = int(p[0])
        sql_select_Query = "select puntuacio from reptes where grup = %s and numprova = %s"
        cursor = mydb.cursor()
        cursor.execute(sql_select_Query, (grup,prova,))
        y = cursor.fetchall()
        punts = str(y[0])
        punts = str(punts[1:len(punts) - 2])
        punts = int(punts)
        mycursor = mydb.cursor()
        sql = "INSERT INTO puntuacions (idusuaris, puntuacions) VALUES (%s, %s)"
        val = (id,punts,)
        mycursor.execute(sql, val)
        mydb.commit()
    else:
        p = z[0]
        id = int(p[1])
        puntuacio = z[0]
        p1 = str(puntuacio[0])
        puntu = int(p1)
        #puntu = str(puntuacio[0])
        sql_select_Query = "select puntuacio from reptes where grup = %s and numprova = %s"
        cursor = mydb.cursor()
        cursor.execute(sql_select_Query, (grup,prova,))
        y = cursor.fetchall()
        punts = str(y[0])
        punts = str(punts[1:len(punts) - 2])
        punts = int(punts)
        npuntuacio = puntu + punts
        updatec = mydb.cursor()
        print("")
        print("Has aconseguit "+str(punts)+" punts.")
        print("Tens "+str(npuntuacio)+" punts.")
        sqlu = "UPDATE puntuacions SET puntuacions = %s WHERE idusuaris = %s"
        val = (npuntuacio,id)
        updatec.execute(sqlu,val)
        mydb.commit()
    #socketResposta()
#Mostra la següent pregunta del repte a no ser que ja s'hagin mostrat 
#totes.
def seguentPregunta(grup, prova):
    maxproves = contarProves(grup)
    if(prova == maxproves):
        print()
    else:
        prova += 1
        mostrarPreguntaPantalla(grup, prova) 
def comprovarProvaResposta(grup, prova):
    connectarBD()
    sql_select_Query = "select * from completat where grup = %s and prova = %s and repte = %s"
    scursor = mydb.cursor()
    val = (user,grup,prova,)
    scursor.execute(sql_select_Query, val)
    z = scursor.fetchall()
    if len(z) == 1:
        retorn = "true"
    else:
        retorn = "false"
    return retorn
        
#Comprova si el codi entrat es correcte.
def resposta(grup, prova):
    sortir = "true"
    while sortir == "true":
        codi = str(input("Entra el codi (R per sortir): "))
        if codi == "r" or codi == "R":
            sortir = "false"
        else:
            if comprovarProvaResposta(grup,prova) == "false":
                if codi.upper() == llegirCodi(grup, prova).upper():
                    print("Correcte")
                    actualitzarPuntuacio(grup,prova)
                    input("Prem enter per continuar: ")
                    seguentPregunta(grup, prova)
                    sortir = "false"
                else:
                    print("Incorrecte")
                    input("Prem enter per continuar: ")
            else:
                print("La prova ja s'ha respost")
                input("Prem enter per continuar: ")
                sortir = "false"
#Retorna la pregunta d'una prova.
def llegirPregunta(grup,prova):
    try:
        retorn = ""
        sql_select_Query = "select prova from reptes where grup = %s and numprova = %s"
        cursor = mydb.cursor()
        cursor.execute(sql_select_Query, (grup,prova))
        z = cursor.fetchall()
        retorn = str(z[0])
        retorn = retorn[2:len(retorn) - 3]
        return retorn
    except:
        return ""
     
#Retorna la resposta d'una prova. def llegirResposta(grup,prova):
#    retorn = "" sql_select_Query = "select resposta from reptes where 
#grup = %s and numprova = %s" cursor = mydb.cursor() 
#cursor.execute(sql_select_Query, (grup,prova)) z = cursor.fetchall() 
#retorn = str(z[0]) retorn = retorn[2:len(retorn) - 3] return retorn 
#Retorna el codi d'una prova.
def llegirCodi(grup,prova):
    retorn = ""
    sql_select_Query = "select codi from reptes where grup = %s and numprova = %s"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query, (grup,prova))
    z = cursor.fetchall()
    retorn = str(z[0])
    retorn = retorn[2:len(retorn) - 3]
    return retorn
#Menú principal d'usuari.

#Retorna la puntuació d'una prova.
def llegirPunt(grup,prova):
    retorn = ""
    sql_select_Query = "select codi from reptes where grup = %s and numprova = %s"
    sql_select_Query = "select puntuacio from reptes where grup = %s and numprova = %s"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query, (grup,prova))
    z = cursor.fetchall()
    retorn = str(z[0])
    retorn = retorn[1:len(retorn) - 2]
    return retorn

#Retorna la descripció d'una prova.
def llegirDesc(grup):
    retorn = ""
    sql_select_Query = "select descripcio from reptes where grup = %s and numprova = 1"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query, (grup,))
    z = cursor.fetchall()
    retorn = str(z[0])
    retorn = retorn[2:len(retorn) - 3]
    return retorn

def menuPrincipal():
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        print("Menu")
        print("========================")
        print("1. Respondre")
        print("2. Veure ranking")
        print("3. Administrar usuari")
        print("10. SORTIR")
        opcio = int(input())
        if opcio > 0 and opcio < 11:
            if opcio == 1:
                mostrarMenuGrups()
            elif opcio == 2:
                ranking()
            elif opcio == 3:
                borrat = menuAdministrarUsuari()
                if borrat == True:
                    sortir="false"
            elif opcio == 10:
                print("Sortint")
                sortir = "false"
         
#Mostra una prova per pantalla.
def mostrarPreguntaPantalla(grup, pregunta):
    os.system('clear')
    print("Repte: " + str(grup) + " Prova: " + str(pregunta))
    print("**********************************")
    print(llegirPregunta(grup, pregunta))
    resposta(grup, pregunta)
#Menú que llista totes les proves d'un grup i demana triar-ne una.
def menuProva(grup):
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        nproves = int(contarProves(grup))
        sql_select_Query = "select descripcio from reptes where grup = %s"
        cursor = mydb.cursor()
        cursor.execute(sql_select_Query, (grup,))
        z = cursor.fetchall()
        descripcions = str(z[0])
        descripcions = descripcions[2:len(descripcions) - 3]
        print("REPTE: " + str(grup)+" Descripcio: "+descripcions)
        print("*********************************")
        nproves = int(nproves)
        anterior = "true"
        for prova in range(1,nproves + 1):
            if comprovarProvaResposta(grup, prova) == "true":
                print(str(prova) + ". Prova " + str(prova)+" (Ja s'ha respost)")
            elif anterior == "true":
                print(str(prova) + ". Prova " + str(prova)+" (Es pot respondre)")
                anterior = "false"
            else:
                print(str(prova) + ". Prova " + str(prova)+" (Encara no es pot respondre)")
        prova = input("Escull la prova que vols seleccionar (R per sortir): ")
        if prova == "r" or prova == "R":
            sortir = "false"
        else:
            prova = int(prova)
            if prova == comprovarProva(grup):
                mostrarPreguntaPantalla(grup,prova)
            else:
                print("Ja has respost/encara no pots respondre aquesta prova.")
                input("Enter per continuar...")
          
#Compte el número de proves que hi han.
def contarProves(grup):
    proves = ""
    sql_select_Query = "select COUNT(numprova) from reptes where grup = %s"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query, (grup,))
    z = cursor.fetchall()
    proves = str(z[0])
    retorn = int(proves[1:len(proves) - 2])
    return retorn
#Compte el número de reptes (grups) que hi han.
def contarGrups():
    grups = ""
    sql_select_Query = "select MAX(grup) from reptes"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query, ())
    z = cursor.fetchall()
    grups = str(z[0])
    retorn = int(grups[1:len(grups) - 2])
    return retorn
#Menú de reptes.
def mostrarMenuGrups():
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        i = int(contarGrups())
        print("REPTES:")
        print("******************************")
        for x in range(1,i + 1):
            print(str(x) + ". Repte " + str(x))
        grup = input("Escull el repte que vols seleccionar (R per sortir): ")
        if grup == "r" or grup == "R":
            sortir = "false"
        else:
            grup = int(grup)
            if grup > 0 and grup < x + 1:
                menuProva(grup)
            else:
                os.system('clear')
                print()
                print("Repte seleccionat incorrecte torna a intentar-ho")
                input("Enter per continuar...")
#Permet importar reptes a partir d'un csv (llegeix la ruta de l'arxiu).
def ImportarReptes():
    sortir = "true"
    while sortir == "true":
        try:
            ruta = str(input("Entra la ruta del csv (R per tornar): "))
            #D:\\PRACTIQUES\\DUAL\\reptes.csv
            #D:\PRACTIQUES\DUAL\reptes_import.csv
            if ruta.upper() == "R":
                sortir="false"
            else:
                with open(ruta, newline='') as File:
                    llegir = csv.reader(File)
                    sql_select_Query = "select max(grup) from reptes"
                    cursor = mydb.cursor()
                    cursor.execute(sql_select_Query, ())
                    z = cursor.fetchall()
                    if len(z) == 0:
                        ngrup=0
                    else:
                        grups = str(z[0])
                        ngrup = int(grups[1:len(grups) - 2])
                    for row in llegir:
                        print(row)
                        g = int(row[0]) + ngrup
                        r = row[1]
                        p = row[2]
                        res = row[3]
                        punt = row[4]
                        desc = row[5]
                        mycursor = mydb.cursor()
                        sql = "INSERT INTO reptes (grup, numprova,prova,codi,puntuacio,descripcio) VALUES (%s, %s,%s,%s,%s,%s)"
                        val = (g,r,p,res,punt,desc)
                        mycursor.execute(sql, val)
                    mydb.commit()
                    input("Enter per continuar...")
                    sortir = "false"
        except:
            print("Ruta no vàlida")

#Permet crear reptes.
def CrearReptes():
    sortir2 = "true"
    while sortir2 == "true":
        resposta = str(input("Vols crear un repte? (S o R per sortir) "))
        if resposta == "s" or resposta == "S":
            sql_select_Query = "select max(grup) from reptes"
            cursor = mydb.cursor()
            cursor.execute(sql_select_Query, ())
            z = cursor.fetchall()
            grups = str(z[0])
            ngrup = int(grups[1:len(grups) - 2])
            r = 0
            sortir = "true"
            ngrup = ngrup+1
            while sortir == "true":
                g = ngrup
                r = r+1
                p = input("Entra la pregunta: ")
                c = str(input("Entra el codi: "))
                punt = int(input("Entra la puntuació: "))
                desc = str(input("Entra la descripció: "))
                mycursor = mydb.cursor()
                sql = "INSERT INTO reptes (grup, numprova,prova,codi,puntuacio,descripcio) VALUES (%s, %s,%s,%s,%s,%s)"
                val = (g,r,p,c,punt,desc)
                mycursor.execute(sql, val)
                mydb.commit()
                input("Prova creada, enter per continuar")
                s = str(input("Vols crear una altre prova? (S o N)"))
                if s == "s" or s == "S":
                    sortir = "true"
                else:
                    sortir = "false"
        elif resposta == "r" or resposta == "R":
            sortir2 = "false"
            
#Modificar la pregunta d'una pregunta.
def modificarPregunta(grup,prova):
    sortir = "true"
    while sortir == "true":
        try:
            mod = input("Entra la nova pregunta: ")
            updatec = mydb.cursor()
            sqlu = "UPDATE reptes SET prova = %s WHERE grup = %s and numprova = %s"
            val = (mod,grup,prova)
            updatec.execute(sqlu,val)
            mydb.commit()
            modificarRepte(grup,prova)
            sortir = "false"
        except ValueError:
            os.system('clear')
            print("Valor no vàlid, torna a intentar-ho.")
            input("Enter per continuar...")
#Modificar la resposta d'una pregunta. def 
#modificarResposta(grup,prova):
#    sortir = "true" while sortir == "true":
#        try:
#            mod = input("Entra la nova resposta: ") updatec = 
#        mydb.cursor() sqlu = "UPDATE reptes SET resposta = %s WHERE 
#        grup = %s and numprova = %s" val = (mod,grup,prova) 
#        updatec.execute(sqlu,val) mydb.commit() sortir = "true" except 
#        ValueError:
#            os.system('clear') print("Valor no vàlid, torna a 
#intentar-ho.") input("Enter per continuar...") Modificar el codi d'una 
#pregunta.
def modificarCodi(grup,prova):
    sortir = "true"
    while sortir == "true":
        try:
            mod = input(str("Entra el nou codi: "))
            updatec = mydb.cursor()
            sqlu = "UPDATE reptes SET codi = %s WHERE grup = %s and numprova = %s"
            val = (mod,grup,prova)
            updatec.execute(sqlu,val)
            mydb.commit()
            sortir = "false"
        except ValueError:
            os.system('clear')
            print("Valor no vàlid, torna a intentar-ho.")
            input("Enter per continuar...") 
            
#Modificar la descripció d'una pregunta.
def modificarDesc(grup):
    sortir = "true"
    while sortir == "true":
        try:
            mod = input(str("Entra la nova descripció: "))
            updatec = mydb.cursor()
            sqlu = "UPDATE reptes SET descripcio = %s WHERE grup = %s and numprova = 1"
            val = (mod,grup)
            updatec.execute(sqlu,val)
            mydb.commit()
            sortir = "false"
        except ValueError:
            os.system('clear')
            print("Valor no vàlid, torna a intentar-ho.")
            input("Enter per continuar...")


#Modificar la puntuació d'una pregunta.
def modificarPunt(grup,prova):
    sortir = "true"
    while sortir == "true":
        try:
            mod = input(str("Entra la nova puntuació: "))
            updatec = mydb.cursor()
            sqlu = "UPDATE reptes SET puntuacio = %s WHERE grup = %s and numprova = %s"
            val = (mod,grup,prova)
            updatec.execute(sqlu,val)
            mydb.commit()
            sortir = "false"
        except ValueError:
            os.system('clear')
            print("Valor no vàlid, torna a intentar-ho.")
            input("Enter per continuar...")

def mostrarRepteAdmin(grup,prova):
    pregunta = llegirPregunta(grup,prova)
    return pregunta
#def mostrarRespostaAdmin(grup,prova):
#    resposta = llegirResposta(grup,prova) return resposta
def mostrarCodiAdmin(grup,prova):
    codi = llegirCodi(grup,prova)
    return codi

def mostrarPuntAdmin(grup,prova):
    punt = llegirPunt(grup,prova)
    return punt

def mostrarDescAdmin(grup,prova):
    desc = llegirDesc(grup)
    return desc

#Menú CRUD d'una prova.
def modificarRepte(grup,prova):
    sortir = "true"
    sql_select_Query = "select descripcio from reptes where grup = %s"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query, (grup,))
    z = cursor.fetchall()
    descripcions = str(z[0])
    descripcions = descripcions[2:len(descripcions) - 3]
    os.system('clear')
    print("REPTE: " + str(grup)+ " Descripcio: "+descripcions+" Prova: "+prova)
    while sortir == "true":
        os.system('clear')
        print("REPTE: " + str(grup)+ " Descripcio: "+descripcions+" Prova: "+prova)
        print("******************************")
        print("1.Anunciat: " + str(mostrarRepteAdmin(grup,prova)))
        print("2.Resposta: " + str(mostrarCodiAdmin(grup,prova)))
        print("3.Puntuació: " + str(mostrarPuntAdmin(grup,prova)))
        print("4.Descripció: " + str(mostrarDescAdmin(grup,prova)))
        seleccio = input("Selecciona el que vols modificar (R per sortir): ")
        if seleccio == "r" or seleccio == "R":
            sortir = "false"
        else:
            print("")
            seleccio = int(seleccio)
            if seleccio == 1:
                modificarPregunta(grup,prova)
            elif seleccio == 2:
                modificarCodi(grup,prova)
            elif seleccio == 3:
                modificarPunt(grup, prova)
            elif seleccio == 4:
                modificarDesc(grup)
            else:
                sortir = "false"

#Retorna la pregunta d'una prova.
def mostrarRepteAdmin(grup,prova):
    pregunta = llegirPregunta(grup,prova)
    return pregunta
#Retorna la resposta d'una prova. def mostrarRespostaAdmin(grup,prova):
#    resposta = llegirResposta(grup,prova) return resposta Retorna el 
#codi d'una prova.
def mostrarCodiAdmin(grup,prova):
    codi = llegirCodi(grup,prova)
    return codi
#Demana si vols borrar la prova del repte seleccionat o si vols tirar 
#enrere.
def borrarRepte(grup,prova):
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        print("Anunciat: " + str(mostrarRepteAdmin(grup,prova)))
        print("Resposta: " + str(mostrarCodiAdmin(grup,prova)))
        seleccio = input("Vols borrar aquesta pregunta? (S o R per sortir) ")
        if seleccio == "r" or seleccio == "R":
            sortir = "false"
        elif seleccio == "s" or seleccio == "S":
            updatec = mydb.cursor()
            sqlu = "DELETE FROM reptes WHERE grup = %s and numprova = %s"
            val = (grup,prova)
            updatec.execute(sqlu,val)
            mydb.commit()
            sortir = "false"
        else:
            sortir = "false"
#Mostra una llista de les proves i demana triar-ne una per borrar-la.
def borSeleccionarRepte(grup):
    sortir = "true"
    while sortir == "true":
        nproves = int(contarProves(grup))
        os.system('clear')
        print("REPTE: " + str(grup))
        print("******************************")
        nproves = int(nproves)
        for prova in range(1,nproves + 1):
            print(str(prova) + ". Prova " + str(prova))
        prova = input("Escull la prova que vols seleccionar (R per sortir): ")
        if prova == "r" or prova == "R":
            sortir = "false"
        else:
            if nproves >= int(prova):
                borrarRepte(grup,prova)
            else:
                print()
                print("Repte seleccionat incorrecte torna a intentar-ho")
                input("Enter per continuar...")
#Demana si vols borrar el repte del grup seleccionat o si vols tirar 
#enrere.
def borrarGrup(grup):
        seleccio = input("Vols esborrar el repte " + str(grup) + " o una pregunta? (S, P o R per sortir) ")
        if seleccio == "r" or seleccio == "R":
            print()
        elif seleccio == "s" or seleccio == "S":
            updatec = mydb.cursor()
            sqlu = "DELETE FROM reptes WHERE grup = %s"
            updatec.execute(sqlu,(grup,))
            mydb.commit()
        elif seleccio == "p" or seleccio == "P":
            x = int(contarGrups())
            sortir2 = "true"
            while sortir2 == "true":
                if int(grup) > 0 and int(grup) < x + 1:
                     seleccio = input("Una pregunta o sortir? (P o S)")
                     if seleccio == "p" or seleccio == "P":
                        borSeleccionarRepte(grup)
                     elif seleccio == "s" or seleccio == "S":
                         sortir2 = "false"
                     else:
                        os.system('clear')
                        print()
                        print("Repte seleccionat incorrecte torna a intentar-ho")
                        input("Enter per continuar...")
#Mostra una llista dels reptes i demana triar-ne un per borrar-lo.
def borSeleccionarGrup():
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        i = int(contarGrups())
        print("REPTES:")
        print("******************************")
        for x in range(1,i + 1):
            print(str(x) + ". Repte " + str(x))
        try:
            grup = input("Escull el repte que vols seleccionar (R per sortir): ")
            if grup == "r" or grup == "R":
               sortir = "false"
            elif int(grup) > 0 and int(grup) < x + 1:
                borrarGrup(grup)
                #borSeleccionarRepte(grup)
            else:
                os.system('clear')
                print()
                print("Repte seleccionat incorrecte torna a intentar-ho")
                input("Enter per continuar...")
        except ValueError:
            os.system('clear')
            print("Valor no vàlid, torna a intentar-ho.")
            input("Enter per continuar...")
#Afageix una prova.
def afegirProva(grup):
    os.system('clear')
    pregunta = input("Entra la pregunta: ")
    codi = input("Entra la resposta: ")
    puntuacio = input("Entra la puntuacio: ")
    sql_select_Query = "select max(numprova) from reptes where grup = %s"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query, (grup,))
    z = cursor.fetchall()
    prova = str(z[0])
    nprova = int(prova[1:len(prova) - 2])
    mycursor = mydb.cursor()
    sql = "INSERT INTO reptes (grup, numprova,prova,codi,puntuacio) VALUES (%s, %s,%s,%s,%s)"
    val = (grup,nprova+1,pregunta,codi,puntuacio)
    mycursor.execute(sql, val)
    mydb.commit()
#Mostra una llista de les proves i demana triar-ne una.
def modSeleccionarRepte(grup):
    sortir = "true"
    while sortir == "true":
        nproves = int(contarProves(grup))
        sql_select_Query = "select descripcio from reptes where grup = %s"
        cursor = mydb.cursor()
        cursor.execute(sql_select_Query, (grup,))
        z = cursor.fetchall()
        descripcions = str(z[0])
        descripcions = descripcions[2:len(descripcions) - 3]
        os.system('clear')
        print("REPTE: " + str(grup)+ " Descripcio: "+descripcions)
        print("******************************")
        nproves = int(nproves)
        for prova in range(1,nproves + 1):
            preg = mostrarRepteAdmin(grup,prova)
            if preg=="":
                preg = mostrarRepteAdmin(grup,prova+1)
                print(str(prova) + ". Prova " + str(prova)+ " Pregunta: "+ preg)
            else:
                print(str(prova) + ". Prova " + str(prova)+ " Pregunta: "+ preg)
        try:
            prova = input("Escull la prova que vols seleccionar o C per crear una pregunta nova.(R per sortir): ")
            if prova == "r" or prova == "R":
                sortir = "false"
            elif prova == "c" or prova == "C":
                afegirProva(grup)
            elif nproves >= int(prova):
                modificarRepte(grup,prova)
        except ValueError:
            os.system('clear')
            print("Valor no vàlid, torna a intentar-ho.")
            input("Enter per continuar...")
#Mostra una llista dels Reptes i demana triar-ne un.
def modSeleccionarGrup():
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        i = int(contarGrups())
        print("REPTES:")
        print("******************************")
        for x in range(1,i + 1):
            sql_select_Query = "select descripcio from reptes where grup = %s"
            cursor = mydb.cursor()
            cursor.execute(sql_select_Query, (x,))
            z = cursor.fetchall()
            descripcions = str(z[0])
            descripcions = descripcions[2:len(descripcions) - 3]
            print(str(x) + ". Repte " + str(x)+" Descripcio: "+descripcions)
        grup = int(input("Escull el repte que vols seleccionar (R per sortir): "))
        if grup == "r" or grup == "R":
            sortir = "false"
        else:
            if grup > 0 and grup < x + 1:
                modSeleccionarRepte(grup)
            else:
                os.system('clear')
                print()
                print("Repte seleccionat incorrecte torna a intentar-ho")
                input("Enter per continuar...")
            
#Crea un usuari nou.
def crearUsuari():
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        llistarUsuaris()
        preg = input("Vols crear un usuari o tornar?(C o T)")
        if preg == "c" or preg =="C":
            sql_select_Query = "select max(idusuaris) from usuaris"
            cursor = mydb.cursor()
            cursor.execute(sql_select_Query, ())
            y = cursor.fetchall()
            idusuari1 = y[0]
            idusuari = idusuari1[0] + 1
            usuari = input("Entra el nom de l'usuari: ")
            contrasenya = crypt.crypt(getpass.getpass("Entra la contrasenya: "),'patata')
            mycursor = mydb.cursor()
            sql = "INSERT INTO usuaris (idusuaris,usuaris,contrasenya) VALUES (%s,%s, %s)"
            val = (idusuari,usuari,contrasenya)
            mycursor.execute(sql, val)
            mydb.commit()
        elif preg == "t" or preg == "T":
            sortir = "false"
        else:
            print("Resposta incorrecte.")
            input("Enter per continuar...")
#Borra un usuari.
def borrarUsuari():
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        llistarUsuaris()
        preg = input("Vols borrar un usuari o tornar?(B o T)")
        if preg == "b" or preg == "B":
            usuari = str(input("Entra el nom de l'usuari: "))
            mycursor = mydb.cursor()
            sql = "DELETE FROM puntuacions WHERE idusuaris = (select idusuaris from usuaris where usuaris = %s)"
            val = (usuari)
            mycursor.execute(sql, (val,))
            mydb.commit()
            mycursor = mydb.cursor()
            sql = "DELETE FROM usuaris WHERE usuaris = %s"
            val = (usuari)
            mycursor.execute(sql, (val,))
            mydb.commit()
        elif preg == "t" or preg == "T":
            sortir = "false"
        else:
            print("Resposta incorrecte.")
            input("Enter per continuar...")
            
#L'usuari s'esborra a ell mateix.
def borrarPropiUsuari():
    sortir="false"
    while sortir=="false":
        os.system('clear')
        passw = crypt.crypt(getpass.getpass("Entra la contrasenya: "),'patata')
        sql_select_Query = "SELECT contrasenya from usuaris WHERE usuaris = %s and contrasenya = %s"
        cursor = mydb.cursor()
        cursor.execute(sql_select_Query, (user,passw))
        z = cursor.fetchall()
        if len(z) <= 0:
            print("Contrasenya incorrecte.")
            input("Enter per continuar...")
        else:
            print("Contrasenya correcta")
            preg = input("Estas segur de que vols esborrar l'usuari?(S o N)")
            if preg == "s" or preg == "S":
                mycursor = mydb.cursor()
                sql = "DELETE FROM puntuacions WHERE idusuaris = (select idusuaris from usuaris where usuaris = %s)"
                val = (user)
                mycursor.execute(sql, (val,))
                mydb.commit()
                mycursor = mydb.cursor()
                sql = "DELETE FROM usuaris WHERE usuaris = %s"
                val = (user)
                mycursor.execute(sql, (val,))
                mydb.commit()
                input ("Has esborrat l'usuari")
                return True
            
#Permet canviar la contrasenya de l'usuari
def canviContrasenya():
        os.system('clear')
        sortir2="false"
        while sortir2 == "false":
            seleccio = input("Vols canviar la contrasenya? (S o qualsevol altre tecla per sortir): ")
            if seleccio == "s" or seleccio == "S":
                sortir2 = "false"
                seleccio = crypt.crypt(getpass.getpass("Entra la contrasenya actual: "),'patata')
                sql_select_Query = "SELECT contrasenya from usuaris WHERE usuaris = %s and contrasenya = %s"
                cursor = mydb.cursor()
                cursor.execute(sql_select_Query, (user,seleccio))
                z = cursor.fetchall()
                if len(z) <= 0:
                    print("Contrasenya incorrecte.")
                    input("Enter per continuar...")
                else:
                    print("Contrasenya correcta.")
                    sortir2 = "true"
                    sortir = "false"
                    while sortir == "false":
                        seleccio = crypt.crypt(getpass.getpass("Entra la nova contrasenya: "),'patata')
                        seleccio2 = crypt.crypt(getpass.getpass("Entra la nova contrasenya un altre cop: "),'patata')
                        if seleccio == seleccio2:
                            mycursor = mydb.cursor()
                            sql = "UPDATE usuaris SET contrasenya = %s WHERE usuaris = %s"
                            mycursor.execute(sql,(seleccio,user))
                            mydb.commit()
                            print("Contrasenya canviada")
                            input("Enter per continuar...")
                            sortir = "true"
                        else:
                            print("Les contrasenyes no coincideixen.")
                            input("Enter per continuar...")
            else:
                sortir2="true"
         
#Menu administracio usuari
def menuAdministrarUsuari():
    sortir = "false"
    while sortir == "false":
        os.system('clear')
        print("1. Esborrar Usuari")
        print("2. Canviar Contrasenya")
        seleccio=input("Selecciona la opció que vulguis. (R per sortir): ")
        if seleccio == "R" or seleccio == "r":
            sortir = "true"
        elif seleccio == "1":
            borrat = borrarPropiUsuari()
            if borrat == True:
                return True
        elif seleccio == "2":
            canviContrasenya()
        else:
            os.system('clear')
            print("Opció no vàlida, torna a intentar-ho.")
            input("Enter per continuar...")
#Comprova si l'usuari existeix.
def comprovarUser(usuari):
    retorn = "false"
    sql_select_Query = "select usuaris from usuaris where usuaris = %s"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query, (usuari,))
    z = cursor.fetchall()
    if len(z) <= 0:
        retorn = "true"
    return retorn
#Menú que permet modificar l'usuari i la contrasenya d'un usuari.
def menModUsuari(usuari):
    os.system('clear')
    sql_select_Query = "select * from usuaris where usuaris = %s"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query, (usuari,))
    z = cursor.fetchall()
    y = z[0]
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        print("1. Nom: "+y[1])
        print("2. Contrasenya: "+y[2])
        print("10. Sortir")
        opcio = input("Selecciona una opció: ")
        try:
            idusuari = y[0]
            opcio = int(opcio)
            if opcio > 0 and opcio < 10:
                if opcio == 1:
                    mod = input("Entra el nou nom: ")
                    updatec = mydb.cursor()
                    sqlu = "UPDATE usuaris SET usuaris = %s WHERE idusuaris = %s"
                    val = (mod,idusuari)
                    updatec.execute(sqlu,val)
                    mydb.commit()
                elif opcio == 2:
                    mod = crypt.crypt(getpass.getpass("Entra la contrasenya: "),'patata')
                    updatec = mydb.cursor()
                    sqlu = "UPDATE usuaris SET contrasenya = %s WHERE idusuaris = %s"
                    val = (mod,idusuari)
                    updatec.execute(sqlu,val)
                    mydb.commit()
            elif opcio == 10:
                os.system('clear')
                print("Sortint")
                sortir = "false"
            else:
                print("Valor no vàlid, torna a intentar-ho.")
                input("Enter per continuar...")
        except ValueError:
            os.system('clear')
            print("Valor no vàlid, torna a intentar-ho.")
            input("Enter per continuar...")
#Modificar usuari.
def modificarUsuari():
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        llistarUsuaris()
        preg = input("Vols modificar un usuari o tornar? (M o T)")
        if preg == "M" or preg == "m":
            seleccio = input("Entra l'usuari que vols modificar: ")
            if comprovarUser(seleccio):
                menModUsuari(seleccio)
            else:
                print("Usuari incorrecte.")
                input("Enter per continuar...")
        else:
            sortir = "false"
#Menú CRUD usuaris.
def usuaris():
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        print("Usuaris")
        print("====================")
        print("1.  Crear usuaris")
        print("2.  Borrar usuaris")
        print("3.  Modificar usuaris")
        print("10. SORTIR")
        opcio = input("Selecciona una opció: ")
        try:
            opcio = int(opcio)
            if opcio > 0 and opcio < 10:
                if opcio == 1:
                    crearUsuari()
                elif opcio == 2:
                    borrarUsuari()
                elif opcio == 3:
                    modificarUsuari()
            elif opcio == 10:
                os.system('clear')
                print("Sortint")
                sortir = "false"
            else:
                print("Valor no vàlid, torna a intentar-ho.")
                input("Enter per continuar...")
        except ValueError:
            os.system('clear')
            print("Valor no vàlid, torna a intentar-ho.")
            input("Enter per continuar...")
#Llista tots els usuaris registrats a la base de dades.
def llistarUsuaris():
    mycursor = mydb.cursor()
    sql = "SELECT usuaris,contrasenya FROM usuaris"
    mycursor.execute(sql, ())
    z = mycursor.fetchall()
    print("Usuaris\tContrasenya\n*******************")
    for row in z:
        print(row[0]+"\t"+row[1].rjust(11))
#Menú admin
def menuAdmin():
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        print("Menu")
        print("========================")
        print("1. Importar reptes")
        print("2. Crear reptes")
        print("3. Modificar reptes")
        print("4. Eliminar reptes")
        print("5. Veure ranking")
        print("6. Administrar usuaris")
        print("10. SORTIR")
        opcio = input()
        try:
            opcio = int(opcio)
            if opcio > 0 and opcio < 10:
                if opcio == 1:
                     os.system('clear')
                     ImportarReptes()
                elif opcio == 2:
                     os.system('clear')
                     CrearReptes()
                elif opcio == 3:
                     print("Modificar reptes")
                     modSeleccionarGrup()
                elif opcio == 4:
                    print("Eliminar reptes")
                    borSeleccionarGrup()
                elif opcio == 5:
                    ranking()
                elif opcio == 6:
                    usuaris()
            elif opcio == 10:
                os.system('clear')
                print("Sortint")
                sortir ="false"
            else:
                print("Valor no vàlid, torna a intentar-ho.")
                input("Enter per continuar...")
        except ValueError:
            os.system('clear')
            #print("Valor no vàlid, torna a intentar-ho.") input("Enter per contunuar...")
#Comprova si l'usuari es admin o no, i redirecciona al seu respectiu 
#menú.
def adminUser(nom,contrasenya):
    if nom == "admin":
        if contrasenya == crypt.crypt("JPUDQHHFTB",'patata'):
                global user
                user = nom
                menuAdmin()
        else:
            print("Contrasenya incorrecta")
            input("Enter per continuar...")
            os.system('clear')
    else:
        comp = compUser(nom,contrasenya)
        if comp == "true":
            menuPrincipal()
        else:
            print("Usuari o contrasenya incorrecte")
            input("Enter per continuar...")
            os.system('clear')
        
#Comprova a la base de dades si l'usuari existeix (excepte admin).
def compUser(nom,contrasenya):
    comp = "false"
    sql_select_Query = "select usuaris,contrasenya from usuaris where usuaris = %s and contrasenya = %s;"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query, (nom,contrasenya))
    z = cursor.fetchall()
    if len(z) <= 0:
        comp = "false"
    else:
        global user
        user = nom
        comp = "true"
    return comp
#Loggin
def loging():
    os.system('clear')
    nom = str(input("Entra l'usuari : "))
    #No és mostra la contrasenya si obres el programa amb python.
    contrasenya = crypt.crypt(getpass.getpass("Entra la contrasenya: "),'patata')
    os.system('clear')
    adminUser(nom,contrasenya)
#Crear usuari
def crearUser():
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        preg = input("Introdueix el nom de l'usuari que vols crear (R per sortir): ")
        if preg == "r" or preg =="R":
            sortir = "false"
        else:
            sql_select_Query = "select max(idusuaris) from usuaris"
            cursor = mydb.cursor()
            cursor.execute(sql_select_Query, ())
            y = cursor.fetchall()
            idusuari1 = y[0]
            idusuari = idusuari1[0] + 1
            usuari = preg
            sql_select_Query = "select usuaris from usuaris where usuaris = %s"
            cursor = mydb.cursor()
            cursor.execute(sql_select_Query, (usuari,))
            z = cursor.fetchall()
            if len(z) <= 0:
                contrasenya = crypt.crypt(getpass.getpass("Entra la contrasenya: "),'patata')
                contrasenya2 = crypt.crypt(getpass.getpass("Entra la contrasenya un altre cop: "),'patata')
                if contrasenya == contrasenya2:
                    mycursor = mydb.cursor()
                    sql = "INSERT INTO usuaris (idusuaris,usuaris,contrasenya) VALUES (%s,%s, %s)"
                    val = (idusuari,usuari,contrasenya)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    print("Usuari creat")
                    input("Enter per continuar...")
                    sortir = "false"
                else:
                    print("Les contrasenyes no coincideixen.")
                    input("Enter per continuar...")
            else:
                print("L'usuari ja existeix.")
                input("Enter per continuar...")
#Menú inici
def inici():
    sortir = "true"
    while sortir == "true":
        os.system('clear')
        print("1. Crear usuari")
        print("2. Loggin")
        print("3. Sortir")
        opcio = input("Selecciona una opció: ")
        try:
            opcio = int(opcio)
            if opcio == 1:
                crearUser()
            elif opcio == 2:
                loging()
            elif opcio ==3:
                sortir="false"
            else:
                os.system('clear')
                print("Valor no vàlid, torna a intentar-ho.")
                input("Enter per continuar...")
        except ValueError:
            os.system('clear')
            print("Valor no vàlid, torna a intentar-ho.")
            input("Enter per continuar...")
    
inici()
