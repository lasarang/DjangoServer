from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError
# You can generate a Token from the "Tokens Tab" in the UI
token = "wOCjQgmTsWfpiOdA2PHWnBNmY6RQSQFNL7O5eKlhEaaS5jQXfOej0_Cy_nRQRSlyAPa2otxQypMgynLr6cdWYg=="
# token = "BnHJ5_uOagFae6QcjRY-u3IDtCg_l6maAT_I3y6swwnlb5GixnXCZrzCHtoVv8oM036WsYbqUQ7gw8syDqogJw=="
#org = "CIDIS-ESPOL"
org = "ESPOL"


# client = InfluxDBClient(url="http://172.25.128.1:8086", token=token)
client = InfluxDBClient(url="http://localhost:8086", token=token)
#client = InfluxDBClient(url="http://localhost:9002", token=token)
#client = InfluxDBClient(url="https://basetsdb-cidis.ngrok.io/", token=token)


def get_cultivos(bucket):
    try:
        query = f' import "influxdata/influxdb/schema" \
                    schema.measurementTagValues( \
                        bucket: "Tester", \
                        tag: "planta",\
                        predicate: (r) => r["_measurement"] == "temperatura" and \
                        r["usuario"] == "{bucket}", \
                        start: -30d \
                        )'

        result = client.query_api().query(query, org=org)
        cultivos = []
        for table in result:
            for record in table.records:
                cultivos.append(record.get_value())

        return cultivos
    except Exception as e:
        print(e)
        return None


def get_fincas(bucket, cultivo):
    try:
        query = f' import "influxdata/influxdb/schema" \
                    schema.tagValues( \
                    bucket: "Tester", \
                    tag: "finca", \
                    predicate: (r) => r["_measurement"] == "temperatura" and \
                    r["usuario"] == "{bucket}", \
                    r["planta"] == "{cultivo}", \
                    start: -30d \
                    )'
        result = client.query_api().query(query, org=org)
        fincas = []
        for table in result:
            for record in table.records:
                fincas.append(record.get_value())

        return fincas
    except InfluxDBError as e:
        print(e)
        return None


def get_data_by_finca(start, stop, planta, bucket):
    try:
        query = f'base = from(bucket: "Tester") \
                            |> range(start: {start}, stop: {stop}) \
                                |> filter(fn: (r) => r["_field"] == "valor") \
                                |> filter(fn: (r) => r["usuario"] == "{bucket}") \
                                |> filter(fn: (r) => r["planta"] == "{planta}") \
                                |> group(columns: ["finca","_measurement"], mode:"by") \
                    a = base \
                        |> rename(columns: {{_value: "mean"}}) \
                        |> mean(column: "mean") \
                    b = base \
                        |> rename(columns: {{_value: "min"}}) \
                        |> min(column: "min") \
                        |> map(fn: (r) => ({{ \
                                r with min: float(v: r.min) \
                            }})) \
                    c = base \
                        |> rename(columns: {{_value: "max"}}) \
                        |> max(column: "max") \
                        |> map(fn: (r) => ({{ \
                                r with max: float(v: r.max) \
                            }})) \
                    d = join(tables: {{a: a, b: b}}, on: ["finca","_measurement"]) \
                        |> keep(columns: ["finca","_measurement","mean","min","_time"]) \
                    e = join(tables: {{a: d, b: c}}, on: ["finca","_measurement"]) \
                        |> keep(columns: ["finca","_measurement","mean","min","max","_time"]) \
                        |> yield()'

        result = client.query_api().query(query, org=org)
        nombres = {
            "temperatura": "Temperatura: ",
            "precipitacion": "Precipitacion:",
            "humedad": "Humedad: ",
            "radiacion": "Radiación Solar: "
        }
        simbolos = {
            "Temperatura: ": "",
            "Precipitacion:": "",
            "Humedad: ": "",
            "Radiación Solar: ": "",
        }
        diccionario = {}
        for table in result:
            for record in table.records:
                name = nombres[record.get_measurement()]
                if name not in diccionario.keys():
                    diccionario[name] = []

                diccionario[name].append([record['finca'], str("%.2f" % round(record['min'], 2)) + simbolos[name], str(
                    "%.2f" % round(record['mean'], 2)) + simbolos[name], str("%.2f" % round(record['max'], 2)) + simbolos[name]])

        return diccionario
    except InfluxDBError as e:
        print(e)
        return None


def get_data_by_finca_detalle(start, stop, medida, planta, finca, bucket):
    try:
        query = f'base = from(bucket: "Tester") \
                            |> range(start: {start}, stop: {stop}) \
                                |> filter(fn: (r) => r["_field"] == "valor") \
                                |> filter(fn: (r) => r["_measurement"] == "{medida}") \
                                |> filter(fn: (r) => r["usuario"] == "{bucket}") \
                                |> filter(fn: (r) => r["planta"] == "{planta}") \
                                |> filter(fn: (r) => r["finca"] == "{finca}")  \
                                |> group(columns: ["finca","_measurement"], mode:"by") \
                    a = base \
                        |> rename(columns: {{_value: "mean"}}) \
                        |> mean(column: "mean") \
                    b = base \
                        |> rename(columns: {{_value: "min"}}) \
                        |> min(column: "min") \
                        |> map(fn: (r) => ({{ \
                                r with min: float(v: r.min) \
                            }})) \
                    c = base \
                        |> rename(columns: {{_value: "max"}}) \
                        |> max(column: "max") \
                        |> map(fn: (r) => ({{ \
                                r with max: float(v: r.max) \
                            }})) \
                    d = join(tables: {{a: a, b: b}}, on: ["finca","_measurement"]) \
                        |> keep(columns: ["finca","_measurement","mean","min","_time"]) \
                    e = join(tables: {{a: d, b: c}}, on: ["finca","_measurement"]) \
                        |> keep(columns: ["finca","_measurement","mean","min","max","_time"]) \
                        |> yield()'

        result = client.query_api().query(query, org=org)
        nombres = {
            "temperatura": "Temperatura: ",
            "precipitacion": "Precipitacion:",
            "humedad": "Humedad: ",
            "radiacion": "Radiación Solar: "
        }
        simbolos = {
            "Temperatura: ": "",
            "Precipitacion:": "",
            "Humedad: ": "",
            "Radiación Solar: ": "",
        }
        lista = []

        for table in result:
            for record in table.records:
                name = nombres[record.get_measurement()]
                lista.append([record['finca'], str("%.2f" % round(record['min'], 2)) + simbolos[name], str("%.2f" %
                             round(record['mean'], 2)) + simbolos[name], str("%.2f" % round(record['max'], 2)) + simbolos[name]])

        return lista

    except InfluxDBError as e:
        print(e)
        return None


def get_data_by_finca_detalle_2(start, stop, planta, finca, bucket):
    try:
        query = f'base = from(bucket: "Tester") \
                            |> range(start: {start}, stop: {stop}) \
                                |> filter(fn: (r) => r["_field"] == "valor") \
                                |> filter(fn: (r) => r["usuario"] == "{bucket}") \
                                |> filter(fn: (r) => r["planta"] == "{planta}") \
                                |> filter(fn: (r) => r["finca"] == "{finca}")  \
                                |> group(columns: ["finca","_measurement"], mode:"by") \
                    a = base \
                        |> rename(columns: {{_value: "mean"}}) \
                        |> mean(column: "mean") \
                    b = base \
                        |> rename(columns: {{_value: "min"}}) \
                        |> min(column: "min") \
                        |> map(fn: (r) => ({{ \
                                r with min: float(v: r.min) \
                            }})) \
                    c = base \
                        |> rename(columns: {{_value: "max"}}) \
                        |> max(column: "max") \
                        |> map(fn: (r) => ({{ \
                                r with max: float(v: r.max) \
                            }})) \
                    d = join(tables: {{a: a, b: b}}, on: ["finca","_measurement"]) \
                        |> keep(columns: ["finca","_measurement","mean","min","_time"]) \
                    e = join(tables: {{a: d, b: c}}, on: ["finca","_measurement"]) \
                        |> keep(columns: ["finca","_measurement","mean","min","max","_time"]) \
                        |> yield()'

        result = client.query_api().query(query, org=org)
        nombres = {
            "temperatura": "Temperatura: ",
            "precipitacion": "Precipitacion:",
            "humedad": "Humedad: ",
            "radiacion": "Radiación Solar: "
        }
        simbolos = {
            "Temperatura: ": "",
            "Precipitacion:": "",
            "Humedad: ": "",
            "Radiación Solar: ": "",
        }

        diccionario = {}

        for table in result:
            for record in table.records:
                name = nombres[record.get_measurement()]
                if name not in diccionario.keys():
                    diccionario[name] = []

                diccionario[name].append([record['finca'], str("%.2f" % round(record['min'], 2)) + simbolos[name], str(
                    "%.2f" % round(record['mean'], 2)) + simbolos[name], str("%.2f" % round(record['max'], 2)) + simbolos[name]])

        return diccionario

    except InfluxDBError as e:
        print(e)
        return None


def get_data_by_nodo(start, stop, finca, planta, bucket):
    try:
        query = f'base = from(bucket: "Tester") \
                            |> range(start: {start}, stop: {stop}) \
                                |> filter(fn: (r) => r["_field"] == "valor") \
                                |> filter(fn: (r) => r["usuario"] == "{bucket}") \
                                |> filter(fn: (r) => r["planta"] == "{planta}") \
                                |> filter(fn: (r) => r["finca"] == "{finca}")  \
                                |> group(columns: ["id_sensor","_measurement"], mode:"by") \
                    a = base \
                        |> rename(columns: {{_value: "mean"}}) \
                        |> mean(column: "mean") \
                    b = base \
                        |> rename(columns: {{_value: "min"}}) \
                        |> min(column: "min") \
                        |> map(fn: (r) => ({{ \
                                r with min: float(v: r.min) \
                            }})) \
                    c = base \
                        |> rename(columns: {{_value: "max"}}) \
                        |> max(column: "max") \
                        |> map(fn: (r) => ({{ \
                                r with max: float(v: r.max) \
                            }})) \
                    d = join(tables: {{a: a, b: b}}, on: ["id_sensor","_measurement"]) \
                        |> keep(columns: ["id_sensor","_measurement","mean","min","_time"]) \
                    e = join(tables: {{a: d, b: c}}, on: ["id_sensor","_measurement"]) \
                        |> keep(columns: ["id_sensor","_measurement","mean","min","max","_time"]) \
                        |> yield()'

        result = client.query_api().query(query, org=org)
        nombres = {
            "temperatura": "Temperatura: ",
            "precipitacion": "Precipitacion:",
            "humedad": "Humedad: ",
            "radiacion": "Radiación Solar: "
        }
        simbolos = {
            "Temperatura: ": "",
            "Precipitacion:": "",
            "Humedad: ": "",
            "Radiación Solar: ": "",
        }

        diccionario = {}
        for table in result:
            for record in table.records:
                name = nombres[record.get_measurement()]
                if name not in diccionario.keys():
                    diccionario[name] = []

                diccionario[name].append([record['id_sensor'], str("%.2f" % round(record['min'], 2)) + simbolos[name], str(
                    "%.2f" % round(record['mean'], 2)) + simbolos[name], str("%.2f" % round(record['max'], 2)) + simbolos[name]])

        return diccionario
    except InfluxDBError as e:
        print(e)
        return None


def get_data_by_nodo_detalle(start, stop, medida, finca, planta, bucket):
    try:
        query = f'base = from(bucket: "Tester") \
                            |> range(start: {start}, stop: {stop}) \
                                |> filter(fn: (r) => r["_field"] == "valor") \
                                |> filter(fn: (r) => r["_measurement"] == "{medida}") \
                                |> filter(fn: (r) => r["usuario"] == "{bucket}") \
                                |> filter(fn: (r) => r["planta"] == "{planta}") \
                                |> filter(fn: (r) => r["finca"] == "{finca}")  \
                                |> group(columns: ["id_sensor","_measurement"], mode:"by") \
                    a = base \
                        |> rename(columns: {{_value: "mean"}}) \
                        |> mean(column: "mean") \
                    b = base \
                        |> rename(columns: {{_value: "min"}}) \
                        |> min(column: "min") \
                        |> map(fn: (r) => ({{ \
                                r with min: float(v: r.min) \
                            }})) \
                    c = base \
                        |> rename(columns: {{_value: "max"}}) \
                        |> max(column: "max") \
                        |> map(fn: (r) => ({{ \
                                r with max: float(v: r.max) \
                            }})) \
                    d = join(tables: {{a: a, b: b}}, on: ["id_sensor","_measurement"]) \
                        |> keep(columns: ["id_sensor","_measurement","mean","min","_time"]) \
                    e = join(tables: {{a: d, b: c}}, on: ["id_sensor","_measurement"]) \
                        |> keep(columns: ["id_sensor","_measurement","mean","min","max","_time"]) \
                        |> yield()'

        result = client.query_api().query(query, org=org)
        nombres = {
            "temperatura": "Temperatura: ",
            "precipitacion": "Precipitacion:",
            "humedad": "Humedad: ",
            "radiacion": "Radiación Solar: "
        }
        simbolos = {
            "Temperatura: ": "",
            "Precipitacion:": "",
            "Humedad: ": "",
            "Radiación Solar: ": "",
        }

        lista = []
        for table in result:
            for record in table.records:
                name = nombres[record.get_measurement()]
                lista.append([record['id_sensor'], str("%.2f" % round(record['min'], 2)) + simbolos[name], str("%.2f" %
                             round(record['mean'], 2)) + simbolos[name], str("%.2f" % round(record['max'], 2)) + simbolos[name]])

        return lista
    except Exception as e:
        print(e)
        return None


def get_data_by_nodo_detalle_2(start, stop, finca, planta, bucket, sensor):
    try:
        query = f'base = from(bucket: "Tester") \
                            |> range(start: {start}, stop: {stop}) \
                                |> filter(fn: (r) => r["_field"] == "valor") \
                                |> filter(fn: (r) => r["usuario"] == "{bucket}") \
                                |> filter(fn: (r) => r["planta"] == "{planta}") \
                                |> filter(fn: (r) => r["finca"] == "{finca}")  \
                                |> filter(fn: (r) => r["id_sensor"] == "{sensor}")  \
                                |> group(columns: ["id_sensor","_measurement"], mode:"by") \
                    a = base \
                        |> rename(columns: {{_value: "mean"}}) \
                        |> mean(column: "mean") \
                    b = base \
                        |> rename(columns: {{_value: "min"}}) \
                        |> min(column: "min") \
                        |> map(fn: (r) => ({{ \
                                r with min: float(v: r.min) \
                            }})) \
                    c = base \
                        |> rename(columns: {{_value: "max"}}) \
                        |> max(column: "max") \
                        |> map(fn: (r) => ({{ \
                                r with max: float(v: r.max) \
                            }})) \
                    d = join(tables: {{a: a, b: b}}, on: ["id_sensor","_measurement"]) \
                        |> keep(columns: ["id_sensor","_measurement","mean","min","_time"]) \
                    e = join(tables: {{a: d, b: c}}, on: ["id_sensor","_measurement"]) \
                        |> keep(columns: ["id_sensor","_measurement","mean","min","max","_time"]) \
                        |> yield()'

        result = client.query_api().query(query, org=org)
        nombres = {
            "temperatura": "Temperatura: ",
            "precipitacion": "Precipitacion:",
            "humedad": "Humedad: ",
            "radiacion": "Radiación Solar: "
        }
        simbolos = {
            "Temperatura: ": "",
            "Precipitacion:": "",
            "Humedad: ": "",
            "Radiación Solar: ": "",
        }

        diccionario = {}
        for table in result:
            for record in table.records:
                name = nombres[record.get_measurement()]
                if name not in diccionario.keys():
                    diccionario[name] = []

                diccionario[name].append([record['id_sensor'], str("%.2f" % round(record['min'], 2)) + simbolos[name], str(
                    "%.2f" % round(record['mean'], 2)) + simbolos[name], str("%.2f" % round(record['max'], 2)) + simbolos[name]])

        return diccionario
    except InfluxDBError as e:
        print(e)
        return None


def get_sensores(medida, cultivo, finca, user_tag):

    try:
        query = f' import "influxdata/influxdb/schema" \
                    schema.tagValues( \
                        bucket: "Tester", \
                        tag: "id_sensor",\
                        predicate: (r) => r["_measurement"] == "{medida}" and \
                        r["planta"] == "{cultivo}" and \
                        r["finca"] == "{finca}" and \
                        r["usuario"] == "{user_tag}", \
                        start: -30d \
                        )'
        result = client.query_api().query(query, org=org)
        sensores = []
        for table in result:
            for record in table.records:
                sensores.append(record.get_value())

        return sensores
    except InfluxDBError as e:
        print(e)
        return None
