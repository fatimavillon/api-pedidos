import boto3
import os
import json

def lambda_handler(event, context):
    try:
        # Validar y procesar el cuerpo de la solicitud
        if 'body' not in event:
            raise ValueError("El cuerpo de la solicitud es obligatorio.")
        
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'El cuerpo de la solicitud debe estar en formato JSON válido.'})
            }

        # Extraer parámetros necesarios
        tenant_id = body.get('tenant_id')
        order_id = body.get('order_id')
        status = body.get('status')
        items = body.get('items')

        if not (tenant_id and order_id and status):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Los campos tenant_id, order_id y status son obligatorios.'})
            }

        # Conectar a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table_name = os.getenv("TABLE_NAME")
        if not table_name:
            raise Exception("El nombre de la tabla no está configurado en las variables de entorno.")
        table = dynamodb.Table(table_name)

        # Logs para depuración
        print(f"Actualizando el pedido con tenant_id={tenant_id}, order_id={order_id} en la tabla {table_name}")

        # Actualizar el pedido en DynamoDB
        table.update_item(
            Key={
                'tenant_id': tenant_id,
                'order_id': order_id
            },
            UpdateExpression="SET #status = :status, #items = :items",
            ExpressionAttributeNames={
                '#status': 'status',
                '#items': 'items'
            },
            ExpressionAttributeValues={
                ':status': status,
                ':items': items if items else []
            }
        )

        # Respuesta exitosa
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Pedido actualizado exitosamente.'})
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
