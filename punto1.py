import os, sys, subprocess
TEAM_ID = '3' 
PORT = '9095' 

def iniciar(port=PORT):
    # si ya existe el directorio, lo borramos
    if os.path.exists('practica_creativa2'):
        subprocess.call(['rm', '-rf', 'practica_creativa2'])

    # nstalacion dependencias
    subprocess.check_call(['sudo', 'apt-get', 'update'])
    subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'python3.9', 'python3-pip', 'git'])

    #Clonar repositorio
    subprocess.check_call(['git', 'clone', 'https://github.com/CDPS-ETSIT/practica_creativa2.git'])
    
    os.chdir('practica_creativa2/bookinfo/src/productpage') #nos vemos al directorio productpage
    
    # los requirements
    with open('requirements.txt', 'w') as f:
        f.write("Flask==1.1.4\n")
        f.write("Werkzeug==0.16.1\n")
        f.write("Jinja2==2.11.3\n")
        f.write("MarkupSafe==2.0.1\n")
        f.write("flask_bootstrap\n")
        f.write("simplejson\n")
        f.write("json2html\n")
        f.write("jaeger-client==3.13.0\n") 
        f.write("opentracing==1.3.0\n")
        f.write("opentracing-instrumentation==2.4.1\n")
        f.write("tornado==4.5.3\n") 
        f.write("threadloop<2\n")
        f.write("thrift==0.11.0\n")
        f.write("requests==2.25.1\n")
        f.write("urllib3==1.26.5\n")
        f.write("certifi\n")
        f.write("chardet\n")
        f.write("idna\n")
    
    
    # Usamos --user para evitar líos de permisos si no se usa sudo con pip
    subprocess.check_call(['python3.9', '-m', 'pip', 'install', '--user', '-r', 'requirements.txt'])

    # Establecemos variable de entorno
    os.environ['TEAM_ID'] = TEAM_ID
    file_backend = 'productpage_monolith.py'
    
    with open(file_backend, 'r') as f:
        content = f.read()

    
    search_text = "'productpage.html',"
    replace_text = f"'productpage.html', team_id=os.environ.get('TEAM_ID', '{TEAM_ID}'),"
    content = content.replace(search_text, replace_text)
    
    #"guardamos" los cambios
    with open(file_backend, 'w') as f:
        f.write(content)
    

    file_html = 'templates/productpage.html'
    
    with open(file_html, 'r') as f:
        html_content = f.read()

  #cambiamos el Frontend
    html_content = html_content.replace(
        "{% block title %}Simple Bookstore App{% endblock %}", 
        "{% block title %}GRUPO: {{ team_id }}{% endblock %}"
    )
    
    with open(file_html, 'w') as f:
        f.write(html_content)



    subprocess.call(['python3.9', 'productpage_monolith.py', port])

def borrar():
    if os.path.exists('practica_creativa2'):
        subprocess.call(['rm', '-rf', 'practica_creativa2'])
        

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    
    action = sys.argv[1]

    if action == "iniciar":
        if len(sys.argv) > 2:
            iniciar(sys.argv[2])
        else:
            iniciar()
    elif action == "borrar":
        borrar()

if __name__ == '__main__':
    main()