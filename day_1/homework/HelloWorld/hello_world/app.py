import json

import urllib3

def lambda_handler(event, context):

    try:
        gender = event['queryStringParameters'].get('gender', '')
        validate_gender(gender)
        
        url = f"https://pokeapi.co/api/v2/gender/{gender}"
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        pokemons = json.loads(r.data)['pokemon_species_details']
        return {
            "statusCode": 200,
            "body": json.dumps({
                "data": pokemons
            })
        }
    except ValueError as ve:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid input', 'details': str(ve)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }

def validate_gender(gender):
    
    genders = ['male', 'female', 'genderless']
    if gender not in genders:
        raise ValueError('Invalid gender')
    
    return "Valid gender"
