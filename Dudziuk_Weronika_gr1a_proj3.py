from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.garden.mapview import MapMarker, MapView
from kivy.lang import Builder
#from kivy.properties import ObjectProperty
from Vincenty import vincenty
import random
import math

Builder.load_string("""
<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'Show me on the map'
            on_press: root.manager.current = 'showme'
        Button:
            text: 'Capital cities'
            on_press: root.manager.current = 'flags'

<ShowMeScreen>:
    search_lat: coor_lat
	search_long: coor_long
	my_map: map
	my_image: image
    my_score: score
    current_step: step
    next_button: next
    GridLayout:
        rows: 4
        cols: 1
        BoxLayout:
            size_hint_y: 1
            MapView:
                zoom: 1
                lat: 52
                lon: 21
                id: map
                on_map_relocated:root.draw_marker()
            GridLayout:
                rows: 2
                cols: 1
                BoxLayout:
                    size_hint_y: 0.1
                    Label:
                        text: ""
                        id: step
                BoxLayout:
                    Image:
                        source: 'photo1.jpg'
                        id: image
        BoxLayout: 
    		size_hint_y: 0.1
    		Label:
    			size_hint_x: 25
    			text: "Lat"
    		Label:
    			size_hint_x: 25
    			id: coor_lat
    		Label:
    			size_hint_x: 25
    			text: "Long"
    		Label:
    			size_hint_x: 25
    			id: coor_long
    	BoxLayout:
    		size_hint_y: 0.1
    		Label:
    			size_hint_x: 25
    			text: "Score"
    		Label:
    			size_hint_x: 25
    			text: '0'
                id: score
            Button:
    			size_hint_x: 25
    			text: "Next"
                id: next
                on_press: root.next_level()
    		Button:
    			size_hint_x: 25
    			text: "Finish"
    			on_press: root.finish()
            Button:
    			size_hint_x: 25
    			text: "Reset"
                on_press: root.reset_levels()
        BoxLayout:
            size_hint_y: 0.1
            Button:
                height: "40dp"
                text: 'Back to menu'
                on_press: root.manager.current = 'menu'
            
<CountryScreen>:
    b1: b1
    b2: b2
    b3: b3
    b4: b4
    question: question
    GridLayout:
        rows: 3
        cols: 1
        BoxLayout:
            size_hint_y: 0.2
            Label:
                text: ''
                id: question
        GridLayout
            rows: 2
            cols: 1
            BoxLayout:
                Button:
                    size_hint_y: 0.5
                    size_hint_y: 0.5
                    height: "20dp"
                    text: '1'
                    id: b1
                    on_press: root.btn_press(b1)
                Button:
                    size_hint_y: 0.5
                    size_hint_y: 0.5
                    height: "20dp"
                    text: '2'
                    id: b2
                    on_press: root.btn_press(b2)
            BoxLayout:
                Button:
                    size_hint_y: 0.5
                    size_hint_y: 0.5
                    height: "20dp"
                    text: '3'
                    id: b3
                    on_press: root.btn_press(b3)
                Button:
                    size_hint_y: 0.5
                    height: "20dp"
                    text: '4'
                    id: b4
                    on_press: root.btn_press(b4)
        BoxLayout:
            size_hint_y: 0.1
            Button:
                height: "40dp"
                text: 'Back to menu'
                on_press: root.manager.current = 'menu'
""")

class MenuScreen(Screen):
    pass

class ShowMeScreen(Screen):
    
    # metoda inicjalizujaca wszystkie zmienne wykorzystywane w widoku ShowMe
    def __init__(self, **kwargs): 
        super(ShowMeScreen, self).__init__(**kwargs)

        self.latitude = self.my_map.lat
        self.longitude = self.my_map.lon
        self.marker = MapMarker(lat=self.latitude, lon=self.longitude)
        self.my_map.add_marker(self.marker)

        self.list_of_points = [
                ["photo1.jpg",52.22977,21.01178],
                ["Wenecja.jpg",45.43713,12.33265],
                ["Rio.jpg",-22.90278,-43.20750],
                ["Krakow.jpg",50.0614300,19.9365800],
                ["Moskwa.jpg",55.7522200,37.6155600],
                ["Londyn.jpg",51.5085300,-0.1257400],
                ["NowyJork.jpg",40.7142700,-74.0059700],
                ["Paryz.jpg",48.8534100,2.3488000],
                ["Sydney.jpg",-33.8678500,151.2073200],
                ["Dubaj.jpg",25.0657000,55.1712800]
        ]

        self.quizLevels = len(self.list_of_points)
        self.currentLevel = 0
        self.totalScore = 0
        self.tolerance = 500000
        
        self.current_step.text = "Step {} of {}".format((self.currentLevel + 1), self.quizLevels)
    
    # metoda odpowiedzialna za zmiane koordynat punktu
    def draw_marker(self):
        try:
            self.my_map.remove_marker(self.marker)
        except:
            print ("exception")

        self.latitude = self.my_map.lat
        self.longitude = self.my_map.lon
        self.marker.lat = self.latitude
        self.marker.lon = self.longitude
        self.my_map.add_marker(self.marker)
        
        self.search_lat.text = "{:.5f}".format(self.latitude)
        self.search_long.text = "{:.5f}".format(self.longitude)
    
    # metoda odpowiedzialna za przalaczenie kolejnego obrazka oraz zliczanie wyniku uzytkownika
    def next_level(self):
        dist = self.getDistance() # sprawdz dystans miedzy wskazanym punktem a realnymi wspolrzednymi
        if (dist and dist < self.tolerance): # jesli odleglosc jest mniejsza od dopuszczalnego marginesu bledu, dodaj punkt
            self.totalScore = self.totalScore + 1
        self.my_score.text = "{}/{}".format(self.totalScore, self.quizLevels) # wyswietla aktualny wynik na ekranie
        
        if self.currentLevel < self.quizLevels - 1: # warunek zmieniajacy obrazek oraz pokazujacy aktualny poziom
            self.currentLevel = self.currentLevel + 1
            self.my_image.source = self.list_of_points[self.currentLevel][0]
            self.current_step.text = "{} of {}".format((self.currentLevel + 1), self.quizLevels)
        
        if self.currentLevel == self.quizLevels - 1: # jesli ostatni poziom, dezaktywuj przycisk Next
            self.next_button.disabled = True
    
    # resetuje ustawienia w 2 przypadkach: nacisniecia przycisku reset lub po dojsciu do konca gry i zamknieciu popup'a
    def reset_levels(self):
        self.currentLevel = 0
        self.totalScore = 0
        self.next_button.disabled = False
        self.my_score.text = "0"
        self.my_image.source = self.list_of_points[self.currentLevel][0]
        self.current_step.text = "Step {} of {}".format((self.currentLevel + 1), self.quizLevels)

    # metoda liczaca dystans miedzy wskazanym punktem a realnymi wspolrzednymi na podstawie algorytmu Vincentego
    def getDistance(self):
        if self.my_image.source == self.list_of_points[self.currentLevel][0]:
            dist = vincenty(self.list_of_points[self.currentLevel][1], self.list_of_points[self.currentLevel][2], self.latitude, self.longitude)
            return dist
        return None

    # metoda obslugujaca nacisniecie przycisku Finish, konczaca aktualna gre
    def finish(self):
        self.popup()
        self.my_score.text = "{}/{}".format(self.totalScore, self.quizLevels)
    
    # metoda odpowiedzialna za wyswietlenie komunikatu z wynikiem koncowym
    def popup(self):
        layout = BoxLayout(orientation='vertical')
        myLabel = Label(text="Your score: {}/{}".format(self.totalScore, self.quizLevels))
        myBtn = Button(text='Ok')
        layout.add_widget(myLabel)
        layout.add_widget(myBtn)
        self.myPopup = Popup(title='Total score', content=layout, auto_dismiss=False, size_hint=(None, None), size=(200, 200))
        myBtn.bind(on_press=self.close_popup)
        self.myPopup.open()
    
    # metoda obslugujaca przycisk w komunikacie koncowym, zamyka komunikat i resetuje ustawienia gry do poczatkowych
    def close_popup(self, button):
        self.myPopup.dismiss()
        self.reset_levels()


class CountryScreen(Screen):
    
    # metoda inicjalizujaca wszystkie zmienne wykorzystywane w widoku Country
    def __init__(self, **kwargs):
        super(CountryScreen, self).__init__(**kwargs)
        self.quizData = self.countries()
        self.levels = 20
        self.reset()

    # resetuje ustawienia do poczatkowych
    def reset(self):
        self.questionsCountries, self.questionsAnswers = self.createQuestionsAndAnswers()
        self.currentLevel = 0
        self.totalScore = 0
        self.setLevel()

    # ustawia/przelacza poziomy (ustawia pytanie oraz 4 odpowiedzi)
    def setLevel(self):
        self.question.text = "[{}/{}] Kraj: {}".format(self.currentLevel + 1, self.levels, self.questionsCountries[self.currentLevel])
        self.b1.text = self.questionsAnswers[self.currentLevel][0]
        self.b2.text = self.questionsAnswers[self.currentLevel][1]
        self.b3.text = self.questionsAnswers[self.currentLevel][2]
        self.b4.text = self.questionsAnswers[self.currentLevel][3]

    # metoda obslugujaca wcisniecie opcji w quizie
    # wszystkie opcje sa powiazane z ta sama metoda, ktora jako argument przyjmuje wcisniety przycisk
    # na podstawie przycisku, przekazanego w argumencie, mozna odczytac tekst przycisku i sprawdzic czy odpowiedz jest prawidlowa,
    # a nastepnie dodac (lub nie) punkty i przejdz do nastepnego pytania
    def btn_press(self, button):
        answer = button.text # pobranie tekstu
        if self.currentLevel < self.levels and self.quizData[self.questionsCountries[self.currentLevel]] == answer: # sprawdzenie poprawnosci odpowiedzi
            self.totalScore += 1

        if self.currentLevel < self.levels: # zwiekszenie licznika poziomow, w przypadku gdy jest on mniejszy niz levels-1 (19)
            self.currentLevel += 1

        if self.currentLevel == self.levels: # wyswietlenie komunikatu z wynikiem, w przypadku ostatniego poziomu
            self.popup()
        else:
            self.setLevel() # zmiana poziomu w przypadku gdy jest on mniejszy niz ostatni

     # metoda odpowiedzialna za wyswietlenie komunikatu z wynikiem koncowym
    def popup(self):
        layout = BoxLayout(orientation='vertical')
        myLabel = Label(text="Your score: {}/{}.\nDo you want to start again?".format(self.totalScore, self.levels))
        myBtn = Button(text='Ok')
        layout.add_widget(myLabel)
        layout.add_widget(myBtn)
        self.myPopup = Popup(title='Total score', content=layout, auto_dismiss=False, size_hint=(None, None), size=(200, 200))
        myBtn.bind(on_press=self.close_popup)
        self.myPopup.open()
    
    # metoda obslugujaca przycisk w komunikacie koncowym, zamyka komunikat i resetuje ustawienia gry do poczatkowych
    def close_popup(self, button):
        self.myPopup.dismiss()
        self.reset()

    # wczytuje dane do quizu z pliku txt i zapisuje je do slownika w ktorym kluczem jest kraj, a wartoscia stolica tego kraju
    def countries(self):
        data = {}
        with open("stolice_hard.txt", encoding="utf8") as f:
            for line in f:
                if line.strip() != "":
                    data[line.split(',')[0]] = line.split(',')[1].strip()
        return data

    # metoda losujaca pytania i odpowiedzi na podstawie danych wczytanych z pliku wejsciowego
    def createQuestionsAndAnswers(self):
        randomCountries = random.sample(list(self.quizData.keys()), self.levels) # wylosuj losowe kraje z puli danych
        answersToCountries = [] # lista na odpowiedzi dla krajów (3 zle odpowiedzi + 1 dobra)
        for country in randomCountries: # ustal (w petli) odpowiedzi dla wszystkich wylosowanych krajów
            randomIncorrectAnswers = random.sample(list(self.quizData.values()), 3) # wylosuj 3 bledne odpowiedzi
            while self.quizData[country] in randomIncorrectAnswers: # jesli wsrod odpowiedzi jest poprawna, losuj kolejny raz
                randomIncorrectAnswers = random.sample(list(self.quizData.values()), 3) 
            randomIncorrectAnswers.append(self.quizData[country]) # dodaj poprawna odpowiedz
            randomIncorrectAnswers.sort() # posortuj alfabetycznie opowiedzi, aby poprawna nie byla zawsze na koncu
            
            # dodaj liste odpowiedzi dla danego pytania do ogolnej listy z odpowiedziami, 
            answersToCountries.append(randomIncorrectAnswers) # wyroznikiem opowiedzi jest indeks w liscie [ [odpowiedzi do 1 pytania], [odpowiedzi do 2 pytania], [...] ]

        # zwroc 2 listy o rownych rozmiarach ktorych index definiuje pytanie i odpowiedz
        return randomCountries, answersToCountries # [kraj_pytanie1, kraj_pytanie2, ...],  [[odpowiedzi do 1 pytania], [odpowiedzi do 2 pytania], [...]]


class multipleScreens(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(ShowMeScreen(name='showme'))
        sm.add_widget(CountryScreen(name='flags'))
        return sm

if __name__ == '__main__':
    multipleScreens().run()