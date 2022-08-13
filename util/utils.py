import urllib.parse
from . import constantes

def get_url_grafana_by_time(data):
    medida = data['medida']
    finca = data['finca']
    cultivo = data['cultivo']
    id = data['id']
    modo = data['modo']
    tiempo = data['tiempo']
    user_tag = data['user_tag']
    return constantes.GRAFANA_URL + constantes.IDS[id][modo] + constantes.VAR_MEDIDAS + medida + constantes.VAR_FINCA + urllib.parse.quote(finca) + constantes.VAR_CULTIVO + cultivo + constantes.VAR_BUCKET + urllib.parse.quote(user_tag) + constantes.TIEMPOS[tiempo]['url']


def get_url_grafana_by_time_sensor(data, nodo):
    return get_url_grafana_by_time(data) + constantes.VAR_SENSOR + urllib.parse.quote(nodo)