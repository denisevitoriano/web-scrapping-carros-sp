def main():
    import pandas as pd
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

    # Define as opções do Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximixed")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")

    # Inicializa o WebDriver para baixar a versão correta do ChromeDriver
    # e iniciar o navegador com as opções definidas
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Define o tempo de espera máximo para encontrar elementos
    wait = WebDriverWait(driver, 5)

    # URL do site a ser acessado para fazer o scraping
    url = "https://carrosp.com.br/revendas/"

    # Acessa a URL no navegador
    driver.get(url)

    # Aguarda e clica no botão de aceitar cookies, se existir
    try:
        aceitar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Entendi')]")))
        aceitar_btn.click()
        print("Botão de cookies clicado.")
    except Exception:
        print("Botão de cookies não encontrado ou já fechado.")

    # Encontra os elememtos pela classe específica
    class_elements = driver.find_elements("class name", "col-md-4.col-ms-12.col-6.mb-4.pl-0.pl-sm-3")

    # Encontra todos os elementos <a> que têm links
    link_elements = driver.find_elements("tag name", "a")
    print(f"links encontrados: {link_elements}")

    # Extrai as URLs dos links encontrados e fltra os que não são vazios
    urls = [link.get_attribute("href") for link in link_elements if link.get_attribute("href") is not None]

    # Extrai o texto dos elementos encontrados da classe específica
    class_texts = [element.text for element in class_elements]

    # Remove as primeiras entradas de urls
    urls = urls[17:]
    urls = urls[:-71]

    # Garante que class_texts e urls tenham o mesmo tamanho
    min_len = min(len(class_texts), len(urls))
    class_texts = class_texts[:min_len]
    urls = urls[:min_len]

    print(f"Número de URLs encontradas: {len(urls)}")
    print(f"Número de textos de classe encontrados: {len(class_texts)}")
    print(f"Número mínimo entre URLs e textos de classe: {min_len}")
    
    # Cria um DataFrame com duas colunas
    data = {
        "loja": class_texts[:len(urls)], # Limita o tamanho ao número de URLs
        "url": urls
    }

    df = pd.DataFrame(data)

    # Adiciona a coluna "telefone"
    df["telefone"] = None # Inicializa a coluna com valores nulos

    # Extrai os números de telefone de cada link
    for i, row in df.iterrows():
        link = row["url"]
        driver.get(link) # Acessa cada link individualmente
        
        for attempt in range(3):  # Tenta até 3 vezes
            try:
                # Clica no botão para revelar o telefone
                ver_telefone_button = driver.find_element("xpath", "/html/body/div[2]/main/div[1]/div/div/div[2]/div[2]/div[4]/div/div/div[2]/button[2]")
                ver_telefone_button.click()  
    
                # Busca o elemento que contém o telefone
                telefone_element = driver.find_element("xpath", "//*[@id='verTelefone']/div/div[2]/div")
                telefone = telefone_element.text.strip()  # Extrai o texto e remove espaços em branco
                df.at[i, "telefone"] = telefone  # Atualiza o DataFrame com o telefone encontrado        
            except (NoSuchElementException, StaleElementReferenceException):
                # Se não encontrar o telefone, registra uma mensagem padrão
                time.sleep(1) # Aguarda e tenta de novo
                if attempt == 2:
                    df.at[i, "telefone"] = "Telefone não encontrado"

    # Exibe o DataFrame resultante
    print(df)
    
    # Salva o DataFrame em um arquivo CSV
    df.to_csv("telefones_anuciantes_carros_sp.csv", index=False, encoding="utf-8")
    
    # Fecha o navegador
    driver.quit()

if __name__ == "__main__":
    main()
