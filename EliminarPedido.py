import boto3
import os
import json

def lambda_handler(event, context):
    try:
        # Validar y obtener parámetros de consulta
        tenant_id = event['queryStringParameters'].get('tenant_id')
        order_id = event['queryStringParameters'].get('order_id')

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

        # Eliminar el pedido de DynamoDB
        table.delete_item(
            Key={
                'tenant_id': tenant_id,
                'order_id': order_id
            }
        )

        # Respuesta exitosa
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Pedido eliminado exitosamente.'})
        }

    except ValueError as ve:
        # Manejo de errores relacionados con validación de entrada
        print(f"Error de validación: {str(ve)}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': str(ve)})
        }

    except Exception as e:
        # Error interno
        print(f"Error interno: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': f'Error interno: {str(e)}'})
        }
