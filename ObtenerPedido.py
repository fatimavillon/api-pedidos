import boto3
import os
import json

def lambda_handler(event, context):
    try:
        # Validar clave API
        headers = event['headers']

        # Validar parámetros de consulta
        query_params = event.get('queryStringParameters', {})
        tenant_id = query_params.get('tenant_id')
        order_id = query_params.get('order_id')

        if not (tenant_id and order_id):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Los parámetros tenant_id y order_id son obligatorios.'})
            }

        # Conectar a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table_name = os.getenv("TABLE_NAME")
        if not table_name:
            raise Exception("El nombre de la tabla no está configurado en las variables de entorno.")
        table = dynamodb.Table(table_name)

        # Logs para depuración
        print(f"Buscando en la tabla {table_name} el pedido con tenant_id={tenant_id} y order_id={order_id}")

        # Obtener el pedido
        response = table.get_item(
            Key={
                'tenant_id': tenant_id,
                'order_id': order_id
            }
        )
        item = response.get('Item')

        if not item:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Pedido no encontrado.'})
            }

        # Respuesta exitosa
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Pedido encontrado.', 'pedido': item})
        }


    except Exception as e:
        # Error interno
        print(f"Error interno: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': f'Error interno: {str(e)}'})
        }
