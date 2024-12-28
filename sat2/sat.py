import requests
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
from PIL import Image
import json
import smtplib
from selenium.webdriver.chrome.options import Options
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from selenium.webdriver.firefox.options import Options

# Configurar opciones para Firefox
options = Options()
options.add_argument("--headless")  # Activa el modo headless

# Inicializar el navegador Firefox con las opciones configuradas
browser = webdriver.Firefox(options=options)
browser.implicitly_wait(8)
browser.get('https://www.sat.gob.pe/VirtualSAT/modulos/Capturas.aspx')

# Espera 5 segundos

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
    time.sleep(1)
    screenshot = Image.open('my_screenshot.png')
    captcha_image = screenshot.crop((left, top, right, bottom))
   
    # Guarda la imagen recortada
    captcha_image.save('captcha_image.png')
    time.sleep(2)
    test_file = ocr_space_file(filename='captcha_image.png', language='spa')

    response_dict = json.loads(test_file)

    # Extraemos el texto del OCR (el valor de "ParsedText")
    captcha_text = response_dict["ParsedResults"][0]["ParsedText"]

    # Imprimimos el texto del CAPTCHA extraído
    texto_limpio = ''.join([char for char in captcha_text if char.isalnum()])
    print("Texto del CAPTCHA:", texto_limpio)
    print("Texto del json:", response_dict)
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

def send_email(body):
    # Configuración del servidor SMTP de Gmail
    gmail_user = os.getenv('GMAIL_USER')  # Obtiene tu correo de Gmail desde las variables de entorno
    gmail_password = os.getenv('GMAIL_PASSWORD')  # Obtiene la contraseña de Gmail desde las variables de entorno
    recipient_email = os.getenv('RECIPIENT_EMAIL') 
     # Tu contraseña o contraseña de aplicación si tienes habilitada la verificación en 2 pasos
    print(f"Correo del remitente: {gmail_user}")
    print(f"Correo destinatario: {recipient_email}")

    smtp_host = "smtp.gmail.com"
    smtp_port = 587

    # Crear el mensaje
    from_addr = gmail_user
    to_addr = recipient_email  # Usamos la variable de entorno para el destinatario

    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = "Alerta: Error detectado en GitHub Actions"

    body = "¡Se ha producido un error en el flujo de trabajo de GitHub Actions!"
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Conectar al servidor SMTP y enviar el correo
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()  # Inicia el cifrado TLS
        server.login(gmail_user, gmail_password)  # Usa las credenciales del entorno
        text = msg.as_string()
        server.sendmail(from_addr, to_addr, text)  # Envía el correo
        server.quit()
        print("Correo enviado con éxito.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# Llamar a la función para enviar el correo



# Use examples:
placas=["AYD706","AVQ856"]

for placa in placas:
    found_papeletas = False
    for attempt in range(10):
        if valid(placa):
            message = browser.find_element(By.ID, 'ctl00_cplPrincipal_lblMensajeVacio')
            if message.text==f'El vehículo de placa {placa} no tiene orden de captura en la provincia de Lima.':
                print(f"Vehículo no tiene paeketas  {placa}")
                
            else:
                print("Vehículo tiene paeketas")
                found_papeletas = True 
            break
        time.sleep(2)
    else:
        print(f"No se encontró CAPTCHA de  {placa}")
        
    if found_papeletas:
        print("-------Todos los vehículos tienen paeketas---------") 
        send_email()
        break

          
#print(message)
