import requests
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
from PIL import Image
import json
from selenium.webdriver.chrome.options import Options

# Configura el navegador en modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")  # Activa el modo headless
chrome_options.add_argument("--disable-gpu")  # Desactiva la aceleración de hardware (opcional, solo para algunos casos)
chrome_options.add_argument("--no-sandbox")
browser = webdriver.Chrome(options=chrome_options)

browser.get('https://www.sat.gob.pe/VirtualSAT/modulos/Capturas.aspx')

# Espera 5 segundos
browser.implicitly_wait(5)
# Localizar la imagen (puedes usar el selector adecuado para tu imagen)
captcha_element = browser.find_element(By.CLASS_NAME, 'captcha_class')  # Reemplaza con el XPath o selector de la imagen
location = captcha_element.location
size = captcha_element.size
# Obtener la URL de la imagen

screenshot = browser.save_screenshot('my_screenshot.png')
screenshot = Image.open('my_screenshot.png')
    # Obtén la ubicación y tamaño del captcha

    # Calcula las coordenadas del recorte
left = location['x']
top = location['y']
right = left + size['width']
bottom = top + size['height']

    # Recorta la región de la imagen del CAPTCHA



def ocr_space_file(filename, overlay=False, api_key='K86916059788957', language='eng'): 
    """ OCR.space API request with local file.
        :param filename: Your file path & name.
        :param overlay: Is OCR.space overlay required in your response. Defaults to False.
        :param api_key: OCR.space API key. Defaults to 'K86916059788957'.
        :param language: Language code to be used in OCR. Defaults to 'eng'.
        :return: Result in JSON format.
    """

    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               'OCREngine':2,
               'filetype':'PNG'
               }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          )
    return r.content.decode()

def valid(placa):
    screenshot = browser.save_screenshot('my_screenshot.png')
    screenshot = Image.open('my_screenshot.png')
    captcha_image = screenshot.crop((left, top, right, bottom))
   
    # Guarda la imagen recortada
    captcha_image.save('captcha_image.png')
    time.sleep(1)
    test_file = ocr_space_file(filename='captcha_image.png', language='spa')

    response_dict = json.loads(test_file)

    # Extraemos el texto del OCR (el valor de "ParsedText")
    captcha_text = response_dict["ParsedResults"][0]["ParsedText"]

    # Imprimimos el texto del CAPTCHA extraído
    print("Texto del CAPTCHA:", captcha_text)

    captcha_input = browser.find_element(By.NAME, 'ctl00$cplPrincipal$txtCaptcha')
    captcha_input.clear() 
    captcha_input.send_keys(captcha_text)

    captcha_input2 = browser.find_element(By.NAME, 'ctl00$cplPrincipal$txtPlaca')
    captcha_input2.clear() 
    captcha_input2.send_keys(placa)

    buscar_button = browser.find_element(By.NAME, 'ctl00$cplPrincipal$CaptchaContinue')
    time.sleep(1)
    buscar_button.click()

    error_message = browser.find_element(By.ID, 'ctl00_cplPrincipal_lblMensajeCapcha')
            # Verifica si el mensaje contiene "incorrecto"
    if error_message.text == "Código de seguridad incorrecta.":
        print("CAPTCHA incorrecto, reintentando...")
        return False
    else:
        print("CAPTCHA correcto, busqueda completada.")
        

    
        return True




# Use examples:
placas=["AYD706","AVQ856"]
papeletas=[0]*2
for placa in placas:
    for attempt in range(2):
        if valid(placa):
            message = browser.find_element(By.ID, 'ctl00_cplPrincipal_lblMensajeVacio')
            if message.text==f'El vehículo de placa {placa} no tiene orden de captura en la provincia de Lima.':
                print("Vehículo no tiene paeketas")
                
            else:
                print("Vehículo tiene paeketas")
                papeletas[placas.index(placa)]=1
            break
        time.sleep(2)
    else:
        print(f"No se pudo encontrar el vehículo de placa {placa} en {attempt} intentos.")
if sum(papeletas) ==2:
    print("-------Todos los vehículos tienen paeketas---------") 
elif sum(papeletas) ==0:
    print("-----------------no tienen paeketas-----------------------")         
#print(message)
