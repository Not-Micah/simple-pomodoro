from kivymd.app import MDApp
from kivy.clock import Clock, mainthread
###########
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.fitimage import FitImage
############
from data import themes_list, themes_accent, read_data, write_data
############
from kivy.core.audio import SoundLoader
############
from threading import Thread
############
from android.runnable import run_on_ui_thread
from jnius import autoclass
from kivy.properties import BooleanProperty


Color = autoclass("android.graphics.Color")
WindowManager = autoclass('android.view.WindowManager$LayoutParams')
activity = autoclass('org.kivy.android.PythonActivity').mActivity


class AppSettings(MDBoxLayout):
    pass

class MainApp(MDApp):
    isready = BooleanProperty(False)
    
    @run_on_ui_thread
    def statusbar(self, color):
        window = activity.getWindow()
        window.clearFlags(WindowManager.FLAG_TRANSLUCENT_STATUS)
        window.addFlags(WindowManager.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
        window.setStatusBarColor(Color.parseColor(color)) 
        window.setNavigationBarColor(Color.parseColor("#000000"))

    def build(self):
        self.theme_cls.theme_style = "Dark"

    def update_data(self):
        items = [
            f"{self.seconds//60} ",
            f"{self.short_break} ",
            f"{self.long_break} ",
            f"{int(self.alert_sound)} ",
            f"{self.background_index} "
        ]
        write_data(items)

    def on_start(self):
        self.isready = True

    def on_isready(self, *largs):
        def load_all(*l):
            # initialize variables
            self.themes = themes_list

            # loading in data
            self.data = read_data()

            # loading bg image without lag
            self.background_index = int(self.data[4]) 
            self.root.ids.background.source = self.themes[self.background_index+1]

            # initializing variables
            self.timer_event, self.active_state, self.active_break = None, "Timer", "Short"

            # storing config in variables
            self.seconds = self.default = int(self.data[0]) * 60
            self.short_break = int(self.data[1])
            self.long_break = int(self.data[2])
            self.alert_sound = int(self.data[3])
            self.statusbar(themes_accent[self.themes[self.background_index+1]])

            # sound effects
            self.alert_sfx = SoundLoader.load("alert.mp3")

            # load timer
            minutes, seconds = self.seconds//60, self.seconds % 60
            self.root.ids.timer.text = '[b]{:02d}:{:02d}[/b]'.format(minutes, seconds)

            # load dialog + image choices
            self.settings_dialog = MDDialog(title="Settings", type="custom", content_cls=AppSettings())

            for i in range(len(self.themes)):
                self.settings_dialog.content_cls.ids.carousel.add_widget(
                    FitImage(
                        source=self.themes[i+1]
                    )
                )

            Clock.schedule_once(lambda *l: setattr(self.root.ids.background, 'opacity', 1), 1)

        Clock.schedule_once(load_all, .2)   

    ''' TIMER FUNCTIONS '''
    def start_timer(self, state):
        # if currently start and pressed, button changed to pause
        if state == "[b]start[/b]":
            self.timer_event = Clock.schedule_interval(self.update_timer, 1)            # start the interval seconds
            self.root.ids.timer_button.text = "[b]pause[/b]"
            self.root.ids.setting_button.disabled = True
            
        elif state == "[b]pause[/b]":
            self.timer_event.cancel()
            self.root.ids.timer_button.text = "[b]start[/b]"
            self.root.ids.setting_button.disabled = False

    def update_timer(self, dt):
        self.seconds -= 1

        if self.seconds <= 0:
            self.timer_event.cancel()
            
            if self.active_state == "Timer":
                self.root.ids.timer.text = "[b]00:00[/b]"
                self.insert_break_buttons()
                self.active_state = "Break"

            elif self.active_state == "Break":                              # if the timer stops on break
                self.root.ids.timer.text = "[b]00:00[/b]"                   # the label 0:00 will be initially set
                self.seconds = self.default                                 # but the seconds are restored to the pomodoro
                self.start_timer("[b]pause[/b]")                            # and the timer is read to be started
                self.active_state = "Timer"                 

            if self.alert_sound:
                self.alert_sfx.play()

        minutes, seconds = self.seconds//60, self.seconds % 60

        # format time as 'mm:ss'
        self.root.ids.timer.text = '[b]{:02d}:{:02d}[/b]'.format(minutes, seconds)

    def restart_timer(self):
        if self.timer_event:                            # if the timer event has already started
            if self.active_state == "Break":           
                self.seconds = self.current_break
            elif self.active_state == "Timer":
                self.seconds = self.default

            # set button to "start"
            self.start_timer("[b]pause[/b]")

            # setting the timer to default time
            minutes, seconds = self.seconds//60, self.seconds % 60
            self.root.ids.timer.text = '[b]{:02d}:{:02d}[/b]'.format(minutes, seconds)

    ''' BREAK FUNCTIONS '''
    def insert_break_buttons(self):
        root = self.root.ids

        # hiding the default button container
        root.default_buttons.opacity = 0

        # disabling the buttons
        root.timer_button.disabled = True
        root.restart_button.disabled = True
        root.setting_button.disabled = True

        # showing the break button container
        root.break_buttons.opacity = 1

        # enabling the buttons
        root.short_button.disabled = False
        root.long_button.disabled = False
        root.continue_button.disabled = False

    def insert_default_buttons(self):
        root = self.root.ids

        # hiding the break button container
        root.break_buttons.opacity = 0

        # disabling the buttons
        root.short_button.disabled = True
        root.long_button.disabled = True
        root.continue_button.disabled = True

        # showing the default button container
        root.default_buttons.opacity = 1

        # enabling the buttons
        root.timer_button.disabled = False
        root.restart_button.disabled = False
        root.setting_button.disabled = False

    def start_break(self, time):
        self.insert_default_buttons()

        if time == self.default:
            self.seconds = self.default
        else:
            self.current_break = time * 60
            self.seconds = time * 60

        self.start_timer("[b]start[/b]")
    
    ''' CONFIG FUNCTIONS '''
    def open_settings(self):
        content = self.settings_dialog.content_cls.ids

        content.carousel.index = self.background_index
        content.short_break.text = str(self.short_break)
        content.long_break.text = str(self.long_break)
        content.pomodoro.text = str(self.default//60)
        content.alert_toggler.active = self.alert_sound

        self.settings_dialog.open()

    def threaded_save(self):
        Thread(target=self.save_settings).start()
        self.settings_dialog.dismiss()

    @mainthread
    def save_settings(self):
        content = self.settings_dialog.content_cls.ids

        short_entry = content.short_break.text
        long_entry = content.long_break.text
        pomodoro_entry = content.pomodoro.text

        if short_entry and long_entry and pomodoro_entry:
            started = True
            if self.seconds == self.default:                                                    # declaring constant to know whether timer was already started
                started = False

            self.background_index = content.carousel.index
            self.short_break = int(short_entry)
            self.long_break = int(long_entry)
            self.default = int(pomodoro_entry) * 60

            if self.active_state == "Timer" and not started:                                    # if on timer and it has not yet started, the update will occur 
                self.seconds = self.default

            self.alert_sound = content.alert_toggler.active
            self.apply_new_settings()
        
            if self.active_break == "Long": self.current_break = self.long_break * 60
            elif self.active_break == "Short": self.current_break = self.short_break * 60

            self.update_data()

    @mainthread
    def apply_new_settings(self):
        # update timer appearance
        minutes, seconds = self.seconds//60, self.seconds % 60
        self.root.ids.timer.text = '[b]{:02d}:{:02d}[/b]'.format(minutes, seconds)
        
        if self.timer_event: self.timer_event.cancel()

        # update the background
        self.root.ids.background.source = self.themes[self.background_index+1]
        self.statusbar(themes_accent[self.themes[self.background_index+1]])
    
if __name__ == "__main__":
    MainApp().run()