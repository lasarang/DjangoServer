import urllib.request

url = 'http://localhost:3000/render/d-solo/2_cZSKuMz/plantilla?orgId=1&refresh=5s&from=1618932525954&to=1618933425954&var-buckets=Tester&var-cultivos=cebollas&var-fincas=Jes%C3%BAs,%20el%20Gran%20Poder&var-fincas2=El%20Manaba&var-medidas=humedad&panelId=28&width=1000&height=500&tz=America%2FGuayaquil'

urllib.request.urlretrieve(url, "local-filename.png")