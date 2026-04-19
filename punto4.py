#!/usr/bin/python3
import subprocess
import sys
import os
import time


TEAM_ID = "3"
NAMESPACE = f"cdps-{TEAM_ID}"
KUBE_DIR = "."

def check_repo():

    if not os.path.exists('practica_creativa2'):
        subprocess.call(['git', 'clone', 'https://github.com/CDPS-ETSIT/practica_creativa2.git'])

def check_minikube():
    # Verificamos que minikube esté corriendo
    try:
        subprocess.check_call(['minikube', 'status'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        sys.exit(1)

def build_images_in_minikube():
    print(f"Construyendo imágenes Docker en Minikube") 
    env = os.environ.copy()
    try:
        minikube_env = subprocess.check_output(['minikube', 'docker-env']).decode('utf-8')
        for line in minikube_env.splitlines():
            if line.startswith('export '):
                key, value = line.replace('export ', '').split('=', 1)
                env[key] = value.strip('"')
    except Exception as e:
        sys.exit(1)

    print(" > Compilando Reviews con Gradle...")
    reviews_path = os.path.abspath("practica_creativa2/bookinfo/src/reviews")
    subprocess.call([
        'docker', 'run', '--rm', '-u', 'root',
        '-v', f"{reviews_path}:/home/gradle/project",
        '-w', '/home/gradle/project', 
        'gradle:4.8.1', 'gradle', 'clean', 'build'
    ], env=env) 

    # Construir imágenes
    imagenes = [
        (f"cdps-productpage:g{TEAM_ID}", "dockerfile_productpage", "."),
        (f"cdps-details:g{TEAM_ID}", "dockerfile_details", "."),
        (f"cdps-ratings:g{TEAM_ID}", "dockerfile_ratings", "."),
        (f"cdps-reviews:g{TEAM_ID}", "practica_creativa2/bookinfo/src/reviews/reviews-wlpcfg", "practica_creativa2/bookinfo/src/reviews/reviews-wlpcfg")
    ]

    for tag, dockerfile, context in imagenes:
        print(f" > Construyendo {tag}...")
        # Nota: docker build necesita el contexto correcto
        if "reviews" in tag:
             subprocess.call(['docker', 'build', '-t', tag, context], env=env)
        else:
             subprocess.call(['docker', 'build', '-f', dockerfile, '-t', tag, context], env=env)

def deploy_base():
  
    subprocess.call(['kubectl', 'apply', '-f', f'{KUBE_DIR}/namespace.yaml'])
    subprocess.call(['kubectl', 'apply', '-f', f'{KUBE_DIR}/services.yaml'])
    
    
    subprocess.call(['kubectl', 'apply', '-f', f'{KUBE_DIR}/details.yaml'])
    subprocess.call(['kubectl', 'apply', '-f', f'{KUBE_DIR}/ratings.yaml'])
    subprocess.call(['kubectl', 'apply', '-f', f'{KUBE_DIR}/productpage.yaml'])

def deploy_reviews(version):
    
    # Primero borramos cualquier versión anterior de reviews para evitar conflictos 
    subprocess.call(['kubectl', 'delete', 'deployment', 'reviews-v1', '-n', NAMESPACE], stderr=subprocess.DEVNULL)
    subprocess.call(['kubectl', 'delete', 'deployment', 'reviews-v2', '-n', NAMESPACE], stderr=subprocess.DEVNULL)
    subprocess.call(['kubectl', 'delete', 'deployment', 'reviews-v3', '-n', NAMESPACE], stderr=subprocess.DEVNULL)
    
    # ueva versión!!!
    file = f"{KUBE_DIR}/reviews-{version}.yaml"
    subprocess.call(['kubectl', 'apply', '-f', file])
    
    time.sleep(2)
    subprocess.call(['kubectl', 'get', 'pods', '-n', NAMESPACE])

def get_url():
   # URL del servicio minikube
        subprocess.call(['minikube', 'service', 'productpage', '-n', NAMESPACE, '--url'])
    
def borrar():
    subprocess.call(['kubectl', 'delete', 'namespace', NAMESPACE])

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 punto4.py [construir | iniciar <v1|v2|v3> | borrar]")
        sys.exit(1)

    accion = sys.argv[1]

    check_repo()

    if accion == "construir":
        subprocess.call(['minikube', 'start', '--driver=docker'])
        check_minikube()
        build_images_in_minikube()
    
    elif accion == "iniciar":
        if len(sys.argv) != 3:
            print("Debes especificar la versión: v1, v2 o v3")
            sys.exit(1)
        check_minikube()
        deploy_base()
        deploy_reviews(sys.argv[2])
        get_url()

    elif accion == "borrar":
        borrar()
    
    else:
        print("Opción desconocida")

if __name__ == '__main__':
    main()

# minikube ssh -- docker system prune -a -f
# cd practica_creativa2/bookinfo/src/reviews
# docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build
# kubectl get pods -n cdps-3