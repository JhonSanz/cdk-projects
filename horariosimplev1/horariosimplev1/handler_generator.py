import os

def generate_lambda_function(instance_ip):
    with open(f"lambda_function.py", "w") as f:
        f.write(
            "import requests\n\n"
            "def handler(event, context):\n"
            f"\turl = f'http://<instance_ip>/generate-backup'\n\n"
            "\ttry:\n"
            "\t\tresponse = requests.post(url)\n"
            "\t\tprint('Respuesta de la instancia EC2:', response.text)\n"
            "\t\treturn {'statusCode': response.status_code, 'body': response.text}\n"
            "\texcept Exception as e:\n"
            "\t\tprint('Error:', str(e))\n"
            "\t\treturn {'statusCode': 500, 'body': 'Error al realizar la solicitud POST'}\n"
        )
