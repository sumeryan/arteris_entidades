{
    "entities": 
    [
      {"id":"P1","entity_type":["Parent"],"attributes":[
                  {"key":"id","value":"P1","type":"string"}
      ]},
      {"id":"C1","entity_type":["Child"],"attributes":[
          {"key":"parentId","value":"P1","type":"string"},
          {"key":"x","value":"3","type":"number"}
      ]},
      {"id":"C2","entity_type":["Child"],"attributes":[
          {"key":"parentId","value":"P1","type":"string"},
          {"key":"x","value":"7","type":"number"}
      ]},
      {"id":"G1","entity_type":["Grand"],"attributes":[
          {"key":"childId","value":"C1","type":"string"},
          {"key":"y","value":"2","type":"number"}
      ]},
      {"id":"G2","entity_type":["Grand"],"attributes":[
          {"key":"childId","value":"C1","type":"string"},
          {"key":"y","value":"4","type":"number"}
      ]},
      {"id":"G3","entity_type":["Grand"],"attributes":[
          {"key":"childId","value":"C2","type":"string"},
          {"key":"y","value":"1","type":"number"}
      ]}
    ]
}


Considere os arquivos como referencia:
output_data.json = Dados dos DocTypes
output_hierarchical.json = Hierarquia dos DocTypes
Crie um novo modulo data_to_engine_entities_v2.py, para o formato de entitie_engine como abaixo, o metodo devera receber como parametro uma lista de output_data e uma lista de output_hierarchical (Não carregar de arquivos, estes são apenas para refeencia):
{
    "entities": 
    {
        {
            "id": [name do registro do DocType - key],
            "entity_type": [nome do DocType, porem utilizar o valor de key da lista como em output_hierarchical.json],
            "attributes": [
                {
                    "key": [nome do campo],
                    "value": [valor do campo],
                    "type": [tipo do campo]
                }
            ]
        }
    }
}
Para relações, como por exemplo Contract_Measurement_Work_Role, o primeiro registro de attributes deve conter o id de parent, exemplo:
[
    {
        "doctype": "Contract Measurement",
        "key": "019678b6-ff93-75d2-912d-a654e42f8cb1",
        "data": {
            "name": "019678b6-ff93-75d2-912d-a654e42f8cb1",
            "contrato": "01966f13-c251-7093-9534-e5ae31671748",
            "contratada": "01966f01-1ae9-72a1-86e1-464b5faba430",
            "data_ejak": "2023-07-14",
            "data_final_do_contrato": "2023-07-31",
            "obra": "OPERAÇÃO DA RODOVIA - MANUTENÇÃO PEDÁGIO",
            "doctype": "Contract Measurement",
            "table_iqgd": [
                {
                    "name": "019678be-2991-7893-9056-a82503920e00",
                    "data_e_hora": "2025-04-03 16:30:22",
                    "item": "01966f89-7148-7163-93dd-c2e6e9b8d5bf",
                    "funcao": "01967345-0e75-7200-8d82-84d37b4f010c",
                    "quantidade_medida": 202.0,
                    "funcaoitem": "01967374-d549-7d91-9b62-e14b371b9f20",
                    "parent": "019678b6-ff93-75d2-912d-a654e42f8cb1",
                    "doctype": "Contract Measurement Work Role"
                },
                {
                    "name": "019678c3-054f-7e30-95d1-0dc63fcd01c3",
                    "data_e_hora": "2025-04-04 16:37:41",
                    "item": "01966f89-a62b-75d1-aef5-fab65638be12",
                    "funcao": "01967345-0e75-7200-8d82-84d37b4f010c",
                    "quantidade_medida": 202.0,
                    "funcaoitem": "01967375-c2bc-75a1-95bc-a4c2f4ab35d9",
                    "parent": "019678b6-ff93-75d2-912d-a654e42f8cb1",
                    "doctype": "Contract Measurement Work Role"
                }
            ]
        }
    }
]
Será transcrito desta forma
{
    "entities": 
    {
        {
            "id": "019678b6-ff93-75d2-912d-a654e42f8cb1",
            "entity_type": "Contract_Measurement",
            "attributes": [
                {
                    "key": "contrato",
                    "value": "01966f13-c251-7093-9534-e5ae31671748",
                    "type": "string"
                },
                ...
                {
                    "key": "obra",
                    "value": "OPERAÇÃO DA RODOVIA - MANUTENÇÃO PEDÁGIO",
                    "type": "string"
                },
            ]
        },
        {
            "id": "019678be-2991-7893-9056-a82503920e00",
            "entity_type": "Contract_Measurement_Work_Role",
            "attributes": [
                {
                    "key": "Contract_Measurement",
                    "value": "019678b6-ff93-75d2-912d-a654e42f8cb1",
                    "type": "string"
                },
                ...
                {
                    "key": "item",
                    "value":"01966f89-7148-7163-93dd-c2e6e9b8d5bf",
                    "type": "string"
                },                
                {
                    "key": "quantidade_medida",
                    "value": 202.0,
                    "type": "numeric"
                },
            ]
        },
        {
            "id": "019678c3-054f-7e30-95d1-0dc63fcd01c3",
            "entity_type": "Contract_Measurement_Work_Role",
            "attributes": [
                {
                    "key": "Contract_Measurement",
                    "value": "019678b6-ff93-75d2-912d-a654e42f8cb1",
                    "type": "string"
                },
                ...
                {
                    "key": "item",
                    "value": "01966f89-a62b-75d1-aef5-fab65638be12",
                    "type": "string"
                },                
                {
                    "key": "quantidade_medida",
                    "value": 202.0,
                    "type": "numeric"
                },
            ]
        }          
    }
}

