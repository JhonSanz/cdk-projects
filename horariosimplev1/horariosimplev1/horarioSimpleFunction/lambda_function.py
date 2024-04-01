import requests

def handler(event, context):
	url = f'http://<instance_ip>/generate-backup'

	try:
		response = requests.post(url)
		print('Respuesta de la instancia EC2:', response.text)
		return {'statusCode': response.status_code, 'body': response.text}
	except Exception as e:
		print('Error:', str(e))
		return {'statusCode': 500, 'body': 'Error al realizar la solicitud POST'}
