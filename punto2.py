#!/usr/bin/python3
import subprocess
import sys


TEAM_ID = "3" 

IMAGE_TAG = f"cdps-productpage:g{TEAM_ID}"

CONTAINER_NAME = f"productpage_cdps_{TEAM_ID}"

PORT_HOST = "9095"
PORT_CONTAINER = "8080" 

APP_OWNER = "Cuadra-et-al"

def crear():
    subprocess.call(['docker', 'build', '-t', IMAGE_TAG, '.'])

def iniciar():
    subprocess.call([
        'docker', 'run', 
        '--name', CONTAINER_NAME, 
        '-p', f'{PORT_HOST}:{PORT_CONTAINER}', 
        '-e', f'TEAM_ID={TEAM_ID}', 
        '-e', f'APP_OWNER={APP_OWNER}', 
        '-d', IMAGE_TAG
    ])

#ip es la inet de enp1s0 --> http://IP:9095

def borrar():
    subprocess.call(['docker', 'rm', '-f', CONTAINER_NAME])

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 punto2.py [crear | iniciar | borrar]")
        sys.exit(1)

    accion = sys.argv[1]
    if accion == "crear":
        crear()
    elif accion == "iniciar":
        iniciar()
    elif accion == "borrar":
        borrar()
    else:
        print("Opción no válida.")

if __name__ == '__main__':
    main()

