import logging
import time
from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class Prop:
    # type == 'PTERODACTYL'
    #         'CACTUS_LARGE'
    #         'CACTUS_SMALL'

    def __init__(self, prop_type, x_pos, y_pos):
        super().__init__()
        self.prop_type = prop_type
        self.x_pos = x_pos
        self.y_pos = y_pos

    def __str__(self):
        return f"prop_type: {self.prop_type}, \n" \
               f"x_pos: {self.x_pos}, \n" \
               f"y_pos: {self.y_pos} \n"


class Game:
    driver = webdriver.Chrome('chromedriver.exe')
    canvas = None
    speed = 6.5
    jump_distance = 70
    FLYING_OBSTACLE_WIDTH = 46
    FLYING_OBSTACLE_HEIGHT = 50  # maior que 50 deve pular
    HACK_COMMAND = "Runner.prototype.gameOver = function () {}"

    def run(self):
        try:
            self.initialize_game_page()
            self.start()
        except Exception as e:
            logging.exception(e)
            self.driver.quit()
        finally:
            sleep(5)
            self.driver.close()
            self.driver.quit()

    def initialize_game_page(self):
        self.driver.get("https://chromedino.com/")
        self.canvas = self.driver.find_element_by_css_selector('.runner-canvas')
        WebDriverWait(self.driver, 1000).until(ec.visibility_of(self.canvas))

    def start(self):
        self.jump()
        while not self.game_over():
            self.check_obstacles()
        score = self.driver.execute_script("return Runner.instance_.distanceMeter.highScore.join(\"\").substring(4)")
        print(score)

    def check_obstacles(self):
        self.manage_speed()
        obstacles = self.driver.execute_script(
            "return Runner.instance_.horizon.obstacles.filter(o => (o.xPos > 25))[0] || {}")
        if obstacles is not None:
            if len(obstacles) > 0:
                prop = Prop(obstacles["typeConfig"]["type"], obstacles["xPos"], obstacles["yPos"])
                if prop.x_pos <= self.jump_distance:
                    if prop.prop_type != 'PTERODACTYL':
                        self.jump()
                    elif prop.y_pos > self.FLYING_OBSTACLE_HEIGHT:
                        self.jump()
                    else:
                        self.crounch()

    def manage_speed(self):
        cur_speed = self.driver.execute_script("return Runner.instance_.currentSpeed")
        if cur_speed > int(self.speed):
            self.jump_distance += 5
            self.speed += 1
        print(f"cur_speed: {cur_speed}")
        print(f"jump_distance: {self.jump_distance}")

    def jump(self):
        action = ActionChains(self.driver)
        action.send_keys(Keys.SPACE).perform()

    def crounch(self):
        action = ActionChains(self.driver)
        action.key_down(Keys.ARROW_DOWN).perform()
        time.sleep(0.1)
        action.key_up(Keys.ARROW_DOWN).perform()

    def game_over(self):
        if self.died():
            self.restart()
        number_of_plays = self.driver.execute_script("return Runner.instance_.playCount")
        return number_of_plays > 50

    def died(self):
        died = self.driver.execute_script("return Runner.instance_.crashed")
        return died

    def restart(self):
        self.speed = 6.5
        self.jump_distance = 70
        self.jump()


if __name__ == '__main__':
    Game().run()
