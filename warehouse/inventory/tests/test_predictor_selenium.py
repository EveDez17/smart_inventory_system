from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_form_interaction(self):
        self.selenium.get(f'{self.live_server_url}/form-page')
        input_box = self.selenium.find_element_by_id('id_of_input')
        submit_button = self.selenium.find_element_by_id('submit_button_id')

        input_box.send_keys('test input')
        submit_button.click()

        # Check for the expected outcome on the page or redirection
        result_text = self.selenium.find_element_by_id('result_text_id').text
        self.assertIn('expected result', result_text)
