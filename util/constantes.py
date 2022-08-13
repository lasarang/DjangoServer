
#Images path
LOCAL_URL = 'http://localhost:4000/'
LOCAL_URL_TEST = 'http://127.0.0.1:8000/'

URL_PROD = 'http://127.0.0.1:8000/'

LOGO = LOCAL_URL + 'static/images/assets/Logo-Crop-Sensing.png'
FOOTER_1 = LOCAL_URL + 'static/images/assets/footer.png'
FOOTER_2 = LOCAL_URL + 'static/images/assets/Logo-CIDIS.png'

#Grafana path
GRAFANA_URL = 'http://localhost:3000/render/d-solo/1dyTkHZnk/plantilla?orgId=1&refresh=5s&panelId='

IDS = {
    "temperatura": {
            "inicio" : "8&theme=dark",
            "historico": "14&theme=dark",
            "tabla": "44",
            "sensor_inicio": "54&theme=dark",
            "sensor_historico": "55&theme=dark",
            "title": "Temperatura",
        },
    "precipitacion": {
            "inicio": "10&theme=dark",
            "historico": "16&theme=dark",
            "tabla": "46",
            "sensor_inicio": "56&theme=dark",
            "sensor_historico": "57&theme=dark",
            "title": "Nivel de Lluvia",
        },
    "humedad": {
            "inicio": "12&theme=dark",
            "historico": "18&theme=dark",
            "tabla": "48",
            "sensor_inicio": "58&theme=dark",
            "sensor_historico": "59&theme=dark",
            "title": "Humedad",
        },
    "radiacion": {
            "inicio": "22&theme=dark",
            "historico": "24&theme=dark",
            "tabla": "50",
            "sensor_inicio": "52&theme=dark",
            "sensor_historico": "53&theme=dark",
            "title": "Radiación Solar",
        },
    "mapa": {
            "inicio": "51",
        },
}

VAR_BUCKET = "&var-buckets="
VAR_CULTIVO = "&var-cultivos="
VAR_FINCA = "&var-fincas="
VAR_MEDIDAS = "&var-medidas="
VAR_FINCA2 = "&var-fincas2="
VAR_SENSOR = "&var-sensor="
VAR_SENSOR2 = "&var-sensor2="

NOMBRES = {
            "temperatura": "Temperatura: ",
            "precipitacion": "Precipitacion:",
            "humedad": "Humedad: ",
            "radiacion": "Radiación Solar: "
        }

TIEMPOS = {
    "Última hora" : {
        "url" : "&from=now-1h&to=now",
        "start" : "-1h",
        "stop" : "now()",
        "title" : "la última hora"
    },
    "Últimas 3 horas" : {
        "url" : "&from=now-3h&to=now",
        "start" : "-3h",
        "stop" : "now()",
        "title" : "las últimas 3 horas"
    },
    "Últimas 6 horas" : {
        "url" : "&from=now-6h&to=now",
        "start" : "-6h",
        "stop" : "now()",
        "title" : "las últimas 6 horas"
    },
    "Últimas 12 horas" : {
        "url" : "&from=now-12h&to=now",
        "start" : "-12h",
        "stop" : "now()",
        "title" : "las últimas 12 horas"
    },
    "Este día" : {
        "url" : "&from=now%2Fd&to=now",
        "start" : "-1d",
        "stop" : "now()",
        "title" : "durante este día"
    },
    "Ayer" : {
        "url" : "&from=now-1d%2Fd&to=now-1d%2Fd",
        "start" : "-2d",
        "stop" : "-1d",
        "title" : "hace un día atras"
    },
    "Hace dos días" : {
        "url" : "&from=now-2d%2Fd&to=now-2d%2Fd",
        "start" : "-3d",
        "stop" : "-2d",
        "title" : "hace dos día atras"
    },
    "Esta semana" : {
        "url" : "&from=now%2Fw&to=now",
        "start" : "-1w",
        "stop" : "now()",
        "title" : "esta semana"
    },
    "Semana Pasada" : {
        "url" : "&from=now-1w%2Fw&to=now-1w%2Fw",
        "start" : "-2w",
        "stop" : "-1w",
        "title" : "la semana pasada"
    },
    "Este mes" : {
        "url" : "&from=now%2FM&to=now",
        "start" : "-1M",
        "stop" : "now()",
        "title" : "este mes"
    },
    "Mes pasado" : {
        "url" : "&from=now-1M%2FM&to=now-1M%2FM",
        "start" : "-2M",
        "stop" : "-1M",
        "title" : "el mes pasado"
    },
    "Este año" : {
        "url" : "&from=now%2Fy&to=now",
        "start" : "-1y",
        "stop" : "now()",
        "title" : "este año"
    },
    "El año pasado" : {
        "url" : "&from=now-1y%2Fy&to=now-1y%2Fy",
        "start" : "-2y",
        "stop" : "-1y",
        "title" : "el año pasado"
    },
    "Los últimos 5 años" : {
        "url" : "&from=now-5y&to=now",
        "start" : "-5y",
        "stop" : "now()",
        "title" : "los últimos 5 años"
    },
}