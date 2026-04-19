

#!/usr/bin/python3
import subprocess
import sys
import os

TEAM_ID = "3" 
COMPOSE_FILE = "docker-compose.micro.yml"

def check_repo():
    if not os.path.exists('practica_creativa2'):
        subprocess.call(['git', 'clone', 'https://github.com/CDPS-ETSIT/practica_creativa2.git'])



def compilar_reviews():
    reviews_path = os.path.abspath("practica_creativa2/bookinfo/src/reviews")
    
    # Comando específico para compilar con Gradle 4.8.1
    cmd = [
        'docker', 'run', '--rm', '-u', 'root',
        '-v', f"{reviews_path}:/home/gradle/project",
        '-w', '/home/gradle/project', 
        'gradle:4.8.1', 'gradle', 'clean', 'build'
    ]
    subprocess.call(cmd)

def construir_todo():

    dockerfile_reviews = "practica_creativa2/bookinfo/src/reviews/reviews-wlpcfg"
    subprocess.call([
        'docker', 'build', 
        '-t', f'cdps-reviews:g{TEAM_ID}', 
        dockerfile_reviews
    ])
    

    subprocess.call(['docker', 'compose', '-f', COMPOSE_FILE, 'build'])

def iniciar(version):
    
    env = os.environ.copy()
    env["SERVICE_VERSION"] = version
    
    # Configuración de colores para las estrellas según la versión
    if version == "v1":
        # v1 no suele mostrar ratings, pero si se fuerza, que sea black
        env["ENABLE_RATINGS"] = "false"
        env["STAR_COLOR"] = "black" 
    elif version == "v2":
        env["ENABLE_RATINGS"] = "true"
        env["STAR_COLOR"] = "black"
    elif version == "v3":
        env["ENABLE_RATINGS"] = "true"
        env["STAR_COLOR"] = "red"
        
    subprocess.call(['docker', 'compose', '-f', COMPOSE_FILE, 'up', '-d'], env=env)
    print(f"Accede a http://localhost:9080/productpage ")

def borrar():
    
    subprocess.call(['docker', 'compose', '-f', COMPOSE_FILE, 'down'])

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 punto3.py [iniciar <v1|v2|v3> | borrar]")
        sys.exit(1)
        
    accion = sys.argv[1]
    
    check_repo()

    if accion == "iniciar":
        if len(sys.argv) != 3:
            print("Error: Debes especificar la versión (v1, v2 o v3).")
            sys.exit(1)
        
        version = sys.argv[2]
        
      
        compilar_reviews()
        construir_todo()
        iniciar(version)
        
    elif accion == "borrar":
        borrar()
    else:
        print("Opción desconocida.")

if __name__ == '__main__':
    main()
