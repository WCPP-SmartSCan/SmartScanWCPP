import requests
import csv
from http.server import HTTPServer, BaseHTTPRequestHandler

def designation_to_numerical(designation):
        if designation == '.':
            return -1
        elif designation == '|':
            return -1
        elif designation == '-':
            return 0
        elif designation == '-a':
            return 1
        elif designation == '-e':
            return 1
        else:
            return 2
        
def numerical_to_light(numerical):
        if numerical == -1:
            return 'unknown'
        elif numerical == 0:
            return 'green'
        elif numerical == 1:
            return 'yellow'
        elif numerical == 2:
            return 'red'

def light_to_numerical(light):
        if light == 'green':
            return 0
        elif light == 'yellow':
            return 1
        elif light == 'red':
            return 2
        else:
            return -1
        
def product_designation(lights):
    
    biggest_seen = -1
    for i in range(len(lights)):
        if light_to_numerical(lights[i]) > biggest_seen:
            biggest_seen = light_to_numerical(lights[i])
    
    return numerical_to_light(biggest_seen)
        

class Serv(BaseHTTPRequestHandler):
    
    def do_GET(self):
        barcode = self.path[1:]
        
        api_url_base = 'https://world.openfoodfacts.org/api/v0/product/'
        url = api_url_base + barcode+'.json'
        response = requests.get(url)
        product = response.json()
        ingredients_list = []
        carcinogens = get_carcinogens()
        try:
            ingredients = product['product']['ingredients_text']
            
            ingredients = ingredients.replace('[', '')
            ingredients = ingredients.replace('.', '')
            ingredients = ingredients.replace(']', '')
            ingredients = ingredients.replace(' (',', ')
            ingredients = ingredients.replace('), ', ', ').upper()
            ingredients = ingredients.replace('(','')
            ingredients = ingredients.replace(')','')
            ingredients = ingredients.replace('*','')
            
            ingredients_list = ingredients.split(', ')
            ingredients_list = set(ingredients_list)
            
            color_list = []
            for i in ingredients_list:
                for chemical in carcinogens:
                    if i.lower()==chemical.name.lower():
                        color_list += [chemical.light_value()]
            if color_list == []:
                color_list = ["No matches"]
        except:
            color_list = ["No ingredients"]
            
        product_light = product_designation(color_list)
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes("Ingredient colors found: " + str(color_list), 'utf-8'))
        self.wfile.write(bytes('\n' + 'Product is ' + str(product_light), 'utf-8'))

class chemical():
            
    def __init__(self, data):
        self.name = f'{data[0]}'
        self.salmonella = f'{data[1]}'
        self.male_rat = f'{data[2]}'
        self.female_rat = f'{data[3]}'
        self.male_mouse = f'{data[4]}'
        self.female_mouse = f'{data[5]}'
        
    def light_value(self):
        numerical_cats = []
        numerical_cats += [designation_to_numerical(self.male_rat)]
        numerical_cats += [designation_to_numerical(self.female_rat)]
        numerical_cats += [designation_to_numerical(self.male_mouse)]
        numerical_cats += [designation_to_numerical(self.female_mouse)]
        
        return numerical_to_light(max(numerical_cats)) # -1 = 'unknown', 0 = 'green', 1 = 'yellow', 2 = 'red'
    
def get_carcinogens():
    carcinogens = []
    with open('NCIChemicals.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        for row in csv_reader:
            carcinogens += [chemical(row)]
    return carcinogens
    
httpd = HTTPServer(('localhost', 8080), Serv)
httpd.serve_forever()
#carcinogens = get_carcinogens()
#for i in range(3,len(carcinogens)):
#    print('Name:', carcinogens[i].name, ', Light Value:', carcinogens[i].light_value())
