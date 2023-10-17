from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import numpy as np
import time,datetime
import yfinance as yf
import pandas as pd
from lxml import etree 
from bs4 import BeautifulSoup
import requests
import matplotlib
matplotlib.use('TkAgg')  # Configura matplotlib para trabajar en modo no interactivo
import matplotlib.pyplot as plt



# Definir variables globales
df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision=pd.DataFrame(),None,None,None,None

#iniciando driver selenium
chrome_options = ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--silent")
chrome_options.add_argument("--log-level=3")
driver = webdriver.Chrome(service=Service('chromedriver.exe'), options=chrome_options)


def importar_base_bitcoin():
    global df_bitcoin,precio_actual, tendencia, media_bitcoin, algoritmo_decision
    symbol = 'BTC-USD'

    # fecha de inicio y fin para los últimos 7 días
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)

    # Descarga el precio histórico del bitcoin en intervalos de 5 minutos
    data = yf.download(symbol, start=start_date, end=end_date, interval='5m')

    # Pausa durante 5 minutos antes de la próxima actualización
    #time.sleep(300)  # 300 segundos = 5 minutos
    df_bitcoin = pd.DataFrame(data)

    
def extraer_tendencias():
    global df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision
    driver.get("https://coinmarketcap.com/")
    # Extraer el precio de Bitcoin
    seleccionar = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[2]/div/div[1]/div[4]/table/tbody/tr[1]/td[4]/div/a/span")))
    time.sleep(1)
    precio_actual=seleccionar.text
    precio_actual = float(precio_actual.replace(",", "").replace("$", ""))
 
    # Extraer variación
    seleccionar = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[2]/div/div[1]/div[4]/table/tbody/tr[1]/td[5]/span")))
    variacion = seleccionar.text
    variacion = float(variacion.replace("%", ""))
    
     
    seleccionar = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[2]/div/div[1]/div[4]/table/tbody/tr[1]/td[5]/span/span"))) 
    clase_tendencia = seleccionar.get_attribute("class")
    if clase_tendencia=="icon-Caret-up":
         tendencia="alta"
    if clase_tendencia=="icon-Caret-down":
         tendencia="baja"
    print(f"Precio actual: {precio_actual}, Variación: {variacion}, Tendencia: {tendencia}")


def limpieza_datos():
    global df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision
    df_bitcoin_limpio = df_bitcoin.copy()
    # Identificar valores duplicados en el índice
    valores_duplicados_en_indice = df_bitcoin_limpio.index.duplicated()
    # Eliminar los valores duplicados en el índice
    df_bitcoin_limpio = df_bitcoin_limpio[~df_bitcoin_limpio.index.duplicated(keep='first')]
    # verificar y ver los valores nulos en la columna 
    df_bitcoin_nulos = df_bitcoin_limpio['Close'].isnull().sum()
    #print("Valores nulos en Close:", df_bitcoin_nulos)
    # Elimina valores nulos en la columna Close
    df_bitcoin_limpio = df_bitcoin_limpio.dropna(subset=['Close'])
    # Filtra los registros con Volumen mayor a 0
    df_bitcoin_limpio = df_bitcoin_limpio[df_bitcoin_limpio['Volume'] > 0]
    # crea un grafico de caja de la columna close
    """
    plt.figure(figsize=(8, 6))
    plt.boxplot(df_bitcoin_limpio['Close'], vert=True)
    plt.ylabel('Precio de Cierre (Close)')
    plt.title('Boxplot del Precio de Cierre de Bitcoin')
    plt.show()
    """
    # Calcula los cuartiles Q1 y Q3 
    Q1 = df_bitcoin_limpio['Close'].quantile(0.25)
    Q3 = df_bitcoin_limpio['Close'].quantile(0.75)
    print("cuartil 1 :", Q1)
    print("cuartil 3 :", Q3)
    # Filtra para tener un precio de cierre entre Q1 y Q3
    df_bitcoin_limpio = df_bitcoin_limpio[(df_bitcoin_limpio['Close'] >= Q1) & (df_bitcoin_limpio['Close'] <= Q3)]
    # grafico el df con los valores entre q1 y q3
    """
    plt.figure(figsize=(8, 6))
    plt.boxplot(df_bitcoin_limpio['Close'], vert=True)
    plt.ylabel('Precio de Cierre (Close)')
    plt.title('Boxplot del Precio de Cierre de Bitcoin entre Q1 y Q3')
    plt.show()
    """
    # Calcula el precio promedio de la columna close
    media_bitcoin = df_bitcoin_limpio['Close'].mean()
    print("Precio promedio: ", media_bitcoin)

def tomar_decisiones():
    global df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision
    if precio_actual >= media_bitcoin and tendencia == 'baja':
        algoritmo_decision = 'Vender'
    elif precio_actual < media_bitcoin and tendencia == 'alta':
        algoritmo_decision = 'Comprar'
    else:
        algoritmo_decision = ''
    print(algoritmo_decision)
 

while True:
 importar_base_bitcoin()
 extraer_tendencias()
 limpieza_datos()
 tomar_decisiones() 
 