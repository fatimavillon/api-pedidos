import boto3
import uuid
from datetime import datetime
import json
import os

def validate_user(tenant_id, user_id):
    """Consulta la tabla de usuarios para validar que user_id pertenece a tenant_id."""
    dynamodb = boto3.resource('dynamodb')
    users_table = os.getenv("USERS_TABLE")
    table = dynamodb.Table(users_table)
    
    response = table.get_item(
        Key={
            'tenant_id': tenant_id,
            'user_id': user_id
        }
    )
    return 'Item' in response  # Retorna True si el usuario existe, False si no



def lambda_handler(event, context):
    try:
        headers = event['headers']
        
        body = json.loads(event['body'])
        tenant_id = body['tenant_id']
        user_id = body['user_id']
        items = body['items']

        if not (tenant_id and user_id and items):
            return {
                'statusCode': 400,
                'body': 'Los campos tenant_id, user_id y items son obligatorios.'
            }
        if not validate_user(tenant_id, user_id):
            return{
                'statusCode': 403,
                'body': 'Usuario no valido para este tenant'
            }
        dynamodb = boto3.resource('dynamodb')
        table_name = os.getenv("TABLE_NAME")
        if not table_name:
            raise Exception("El nombre de la tabla no esta configurado en las variables de entorno.")
        table = dynamodb.Table(table_name)

        print("Nombre de la tabla DynamoDB", table_name)
        order_id = str(uuid.uuid4())
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        item={
                'tenant_id': tenant_id,
                'order_id': order_id,
                'user_id': user_id,
                'items': items,
                'created_at': created_at,
                'status': 'CREATED'
        }
        print("Item a insertar:", item)
        table.put_item(Item=item)

        return {
            'statusCode': 200,  # Código HTTP esperado
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Pedido creado exitosamente.'})
        }


    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': 'El cuerpo de la solicitud debe ser JSON válido.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error interno: {str(e)}'
        }

        
