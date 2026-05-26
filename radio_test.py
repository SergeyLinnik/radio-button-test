"""
Автоматизированный тест для проверки radio buttons на сайте https://demoqa.com/radio-button
Следует best practices: используются assert, конкретные исключения, нет вложенных try-except
"""

import logging
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
    WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def setup_driver() -> webdriver.Chrome:
    """Настройка драйвера — без try-except, ошибки должны падать"""
    logging.info("Начинаем настройку ChromeDriver...")
    
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=service, options=options)
    logging.info("ChromeDriver успешно настроен и запущен")
    
    return driver


def find_radio_button(driver: webdriver.Chrome, value: str) -> WebElement:
    """
    Находит радиокнопку. Если не найдена — тест падает.
    Используем конкретное исключение NoSuchElementException.
    """
    # Прямой поиск без try-except — пусть падает с понятной ошибкой
    return driver.find_element(By.XPATH, f"//label[contains(text(), '{value}')]/preceding-sibling::input")


def click_radio_button(driver: webdriver.Chrome, radio_button: WebElement, value: str) -> None:
    """
    Кликает по радиокнопке.
    Без вложенных try-except — используем проверку перед кликом.
    """
    # Проверяем, что элемент видим и кликабелен
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(radio_button)
    )
    
    # JavaScript клик (более надёжный для радио-кнопок)
    driver.execute_script("arguments[0].click();", radio_button)
    logging.info(f"✓ Клик по радиокнопке '{value}' выполнен")


def get_selected_status_text(driver: webdriver.Chrome) -> Optional[str]:
    """
    Получает текст сообщения. Возвращает None, если сообщения нет.
    Без Exception — проверяем существование элемента.
    """
    elements = driver.find_elements(By.CLASS_NAME, "mt-3")
    
    if not elements:
        return None
    
    text = elements[0].text
    return text if text and "You have selected" in text else None


def test_radio_button(driver: webdriver.Chrome, radio_value: str) -> None:
    """
    Тестирование одной радиокнопки.
    Все проверки через assert.
    """
    logging.info(f"=" * 50)
    logging.info(f"Тестируем радиокнопку: '{radio_value}'")
    logging.info(f"=" * 50)
    
    # 1. Найти радиокнопку — если нет, упадёт с NoSuchElementException
    radio_btn = find_radio_button(driver, radio_value)
    
    # 2. Проверка, что кнопка существует
    assert radio_btn is not None, f"Радиокнопка '{radio_value}' не найдена"
    
    # 3. Особый случай: кнопка "No" должна быть disabled
    if radio_value == "No":
        assert not radio_btn.is_enabled(), f"Кнопка '{radio_value}' должна быть заблокирована"
        logging.info(f"✓ Кнопка 'No' корректно заблокирована")
        return  # Дальнейшие проверки не нужны
    
    # 4. Клик по кнопке
    click_radio_button(driver, radio_btn, radio_value)
    time.sleep(0.5)  # Небольшая задержка для стабильности
    
    # 5. assert, что кнопка выбрана
    assert radio_btn.is_selected(), f"Радиокнопка '{radio_value}' не выбрана после клика"
    logging.info(f"✅ Радиокнопка '{radio_value}' успешно выбрана")
    
    # 6. Проверка текста подтверждения
    success_message = get_selected_status_text(driver)
    expected_text = f"You have selected {radio_value}"
    
    assert success_message is not None, "Сообщение об успешном выборе не появилось"
    assert expected_text in success_message, \
        f"Ожидалось: '{expected_text}', получено: '{success_message}'"
    
    logging.info(f"✅ Текст подтверждения корректен: '{success_message}'")


def main() -> None:
    """
    Главная функция. Все ошибки падают наружу — так видно, что пошло не так.
    """
    driver = None
    
    try:
        # Конкретные ошибки, которые мы ожидаем на этом уровне
        driver = setup_driver()
        driver.get("https://demoqa.com/radio-button")
        
        # Ждём загрузки страницы
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Список тестов
        radio_values = ["Yes", "Impressive", "No"]
        
        for value in radio_values:
            test_radio_button(driver, value)
            time.sleep(0.5)
        
        logging.info("=" * 50)
        logging.info("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО")
        logging.info("=" * 50)
        
    except (NoSuchElementException, TimeoutException, AssertionError) as e:
        # Только конкретные исключения, которые мы ожидаем
        logging.error(f"❌ ТЕСТ НЕ ПРОЙДЕН: {type(e).__name__}: {e}")
        raise  # Перебрасываем, чтобы тест точно упал
        
    except WebDriverException as e:
        logging.error(f"❌ ОШИБКА ДРАЙВЕРА: {type(e).__name__}: {e}")
        raise
        
    finally:
        if driver:
            driver.quit()
            logging.info("Браузер закрыт")


if __name__ == "__main__":
    main()
