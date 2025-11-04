📥 lambda--reclamacoes-tratativa-bacen
  Função Lambda responsável por receber, interpretar e padronizar reclamações oriundas do Banco Central (BACEN), garantindo ingestão segura, priorização adequada e encaminhamento para o sistema de processamento via SQS.

📌 Propósito
  Automatizar o tratamento de reclamações recebidas via protocolo BACEN (RDR), assegurando:
    Validação e extração de dados de XMLs malformados ou incompletos
    Padronização do formato interno de reclamação
    Priorização máxima no fluxo de atendimento
    Envio para fila SQS de alta prioridade

🔄 Fluxo de Execução
  Recepção do XML via evento HTTP (SOAP/XML)

Extração de dados relevantes:
  ID da demanda BACEN
  CPF/CNPJ do cliente
  Texto original da reclamação
  Padronização da estrutura interna
  Adição de metadados de rastreabilidade e prioridade
  Envio para fila SQS com atributos de prioridade
  Retorno HTTP com status e ID da reclamação

🧠 Lógica de Interpretação
  A função parse_bacen_xml realiza:
  Parsing seguro do XML recebido
  Extração de campos com fallback para valores padrão
  Geração de identificador único para rastreabilidade

Exemplo de saída padronizada:
    json
    {
      "Id": "e3f1c2a0-9d4b-4f3f-9a2e-123456789abc",
      "CustomerIdentifier": "12345678900",
      "ReclamationText": "Texto da reclamação BACEN...",
      "ReceivedDate": "2025-11-04T23:55:12.000Z",
      "SourceChannel": "BACEN",
      "CustomerHistory": null,
      "ClassifiedCategories": [],
      "IdRastreabilidadeBACEN": "RDR-abc12345"
    }

🛡️ Tratamento de Erros
  Erros de parsing XML: Retorno HTTP 400 com mensagem detalhada
  Falhas internas inesperadas: Retorno HTTP 500 com log crítico
  Falha no envio ao SQS: Retorno HTTP 500 com sugestão de retentativa

📬 Integração com SQS
  A reclamação padronizada é enviada para a fila de alta prioridade com os seguintes atributos:
    Atributo	Valor
    Origem	BACEN
    Prioridade	ALTA

🧰 Tecnologias Utilizadas
  Componente	Tecnologia
  Função Serverless	AWS Lambda
  Parsing XML	xml.etree.ElementTree (Python)
  Fila de mensagens	Amazon SQS
  Identificação	UUID
  Logging	context.log

🧪 Testes Recomendados
  XMLs válidos e bem-formados
  XMLs incompletos ou malformados
  Falhas simuladas no envio ao SQS
  Verificação de atributos de prioridade e origem

🔐 Segurança e Rastreabilidade
  Identificador único por reclamação
  Tag de rastreabilidade BACEN (IdRastreabilidadeBACEN)
  Log completo de eventos e erros
  Priorização explícita para atendimento crítico
