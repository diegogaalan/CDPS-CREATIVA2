FROM python:3.9-slim

# Instalamos git para clonar el repo
RUN apt-get update 
RUN apt-get install -y git
RUN git clone https://github.com/CDPS-ETSIT/practica_creativa2.git

#vamos a productpage
WORKDIR /practica_creativa2/bookinfo/src/productpage

# Instalamos dependencias
RUN pip3 install -r requirements.txt


# podriamos haber usado COPY pero asi no modificamos el repo original, por ello usamos sed que de la teoria se que es una de las opciones
# Modificamos el fichero productpage_monolith.py para pasar las variables de entorno a la plantilla HTML
RUN sed -i '/def front():/a \    team_id = os.environ.get("TEAM_ID", "Unknown")\n    app_owner = os.environ.get("APP_OWNER", "Unknown")' productpage_monolith.py && \
    sed -i "s/'productpage.html',/'productpage.html', team_id=team_id, app_owner=app_owner,/g" productpage_monolith.py

# Modificamos la plantilla HTML para que salgan las variables en el título
# Buscamos el bloque de título original y lo reemplazamos.
WORKDIR /practica_creativa2/bookinfo/src/productpage/templates
RUN sed -i 's/{% block title %}Simple Bookstore App{% endblock %}/{% block title %}{{ app_owner }} - Group: {{ team_id }}{% endblock %}/g' productpage.html

# Volvemos al directorio de la app
WORKDIR /practica_creativa2/bookinfo/src/productpage

# uerto interno 8080
EXPOSE 8080

# Definimos variables de entorno por defecto (se sobreescriben al ejecutar run)
ENV TEAM_ID=3
ENV APP_OWNER=Grupo3

# Arrancamos la aplicación en el puerto 8080
CMD ["python3", "productpage_monolith.py", "8080"]