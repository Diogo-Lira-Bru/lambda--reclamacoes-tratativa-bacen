import json
import os
import uuid
import boto3
from datetime import datetime
import xml.etree.ElementTree as ET 

def parse_bacen_xml(xml_string):
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        raise ValueError(f"XML de entrada do BACEN malformado: {e}")
    
    id_bacen = root.findtext('.//ID_DEMANDA_RDR') or f"RDR-{uuid.uuid4().hex[:8]}"
    cpf_cnpj = root.findtext('.//IDENTIFICADOR_CLIENTE') or "00000000000"
    texto_reclamacao = root.findtext('.//TEXTO_ORIGINAL_RECLAMACAO') or "Texto da reclamação BACEN não fornecido."
    
    extracted_data = {
        'IdBACEN': id_bacen, 
        'CustomerIdentifier': cpf_cnpj, 
        'ReclamationText': texto_reclamacao, 
        'ReceivedDateBACEN': datetime.utcnow().isoformat() + 'Z'
    }
    
    return extracted_data


def lambda_handler(event, context):
    context.log(f"Iniciando ingestão BACEN (RDR).")

    # ----------------------------------------------------
    # 1. RECEPÇÃO, EXTRAÇÃO E TRATAMENTO DE ERROS DE PROTOCOLO
    # ----------------------------------------------------
    
    try:
        raw_xml_payload = event['body'] 
        
        extracted_data = parse_bacen_xml(raw_xml_payload) 

    except (ValueError, ET.ParseError) as e:
        context.log(f"ERRO 400: Falha na análise do XML/SOAP do BACEN. Erro: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': f'XML de entrada inválido: {e}'})
        }
    except Exception as e:
        context.log(f"ERRO CRÍTICO: Falha desconhecida na recepção BACEN. Erro: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Falha interna ao processar XML.'})
        }
    
    # ----------------------------------------------------
    # 2. PADRONIZAÇÃO E ADIÇÃO DA TAG DE PRIORIDADE MÁXIMA
    # ----------------------------------------------------

    standardized_reclamation = {
        'Id': str(uuid.uuid4()),
        'CustomerIdentifier': extracted_data['CustomerIdentifier'],
        'ReclamationText': extracted_data['ReclamationText'],
        'ReceivedDate': extracted_data['ReceivedDateBACEN'],
        'SourceChannel': 'BACEN',
        'CustomerHistory': None, 
        'ClassifiedCategories': [],
        'IdRastreabilidadeBACEN': extracted_data['IdBACEN']
    }
    
    message_body = json.dumps(standardized_reclamation)

    # ----------------------------------------------------
    # 3. ENVIO PARA O SQS DE ALTA PRIORIDADE
    # ----------------------------------------------------
    
    try:
        sqs_client.send_message(
            QueueUrl=SQS_PRIORITY_QUEUE_URL,
            MessageBody=message_body,
            MessageAttributes={
                'Origem': {'DataType': 'String', 'StringValue': 'BACEN'},
                'Prioridade': {'DataType': 'String', 'StringValue': 'ALTA'} 
            }
        )
        
        context.log(f"Reclamação BACEN {standardized_reclamation['Id']} enviada para o SQS de ALTA PRIORIDADE.")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'id': standardized_reclamation['Id'], 'status': 'Recebido com Prioridade BACEN'})
        }

    except Exception as e:
        context.log(f"ERRO CRÍTICO: Falha ao enviar para o SQS de Prioridade. Erro: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Falha interna crítica na ingestão BACEN (SQS).'
                                          ' O evento será retentado pela fonte.'})
        }