import sqlite3
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage, Image
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex
import matplotlib.pyplot as plt
from matplotlib import use as mpl_use
from kivy.core.image import Image as CoreImage
from io import BytesIO

# Use Agg backend for matplotlib
mpl_use('Agg')

DB_NAME = "survey.db"

# --- QUESTIONS BY SECTION ---
infra_questions = [
    "Is the subcentre a Government or Rented building?",
    "What is the condition of the building? (Good/Average/Poor)",
    "Is the surrounding cleanliness satisfactory?",
    "Is electricity supply available?",
    "Is power backup (Inverter/Solar) available?",
    "Is safe drinking water available?",
    "Are toilets available and functional?",
    "Is the hand washing facility functional?",
    "Is the BMWM facility functional?",
    "Is patient seating adequate?",
    "Are ANC IEC posters displayed?",
    "Are Danger Signs IEC posters displayed?",
    "Are HRP IEC posters displayed?",
    "Are Breastfeeding IEC posters displayed?",
    "Are BPCR IEC posters displayed?",
    "Are BMW IEC posters displayed?",
    "Are Steps of Hand Washing posters displayed?"
]
anc_questions = [
    "Is the newborn weighing machine functional?",
    "Is the examination table available?",
    "Is the adult weighing scale available?",
    "Is the infant weighing scale available?",
    "Is the adult height scale available?",
    "Is the infantometer available?",
    "Is the BP apparatus available?",
    "Is the stethoscope available?",
    "Is the fetoscope available?",
    "Is the thermometer (digital & low-reading) available?",
    "Is the hemoglobinometer available?",
    "Are urine sugar/albumin strips available?",
    "Is a glucometer with strips available?",
    "Is the pregnancy test kit (Nischay) available?",
    "Is the vaccine carrier with ice packs available?",
    "Is a measuring tape available?",
    "Are IFA tablets available?",
    "Are calcium tablets available?",
    "Is albendazole available?",
    "Are tetanus / Td vials available?",
    "Is vitamin K injection available?",
    "Is oxytocin injection available?",
    "Is the emergency drug kit available?",
    "Is the HBNC Kit for ASHA available?"
]
delivery_questions = [
    "Is a digital watch available?",
    "Is a digital thermometer available?",
    "Is a neonatal weighing scale with sling available?",
    "Is a baby blanket available?",
    "Is a feeding spoon available?",
    "Is a warm bag available?",
    "Are essential newborn medicines available?",
    "Are sterile gloves available?",
    "Is a delivery/SBA kit available?",
    "Is hand sanitizer available?",
    "Is soap available?",
    "Is a towel available?",
    "Is chlorine solution available?",
    "Is bucket & mug available?",
    "Is a needle/hub cutter available?",
    "Are color-coded waste bins available?",
    "Are MCP cards with RCH ID available?",
    "Are PMSMA stickers available?",
    "Are ANC/PNC registers available?",
    "Are referral slips available?",
    "Is data entered in ANMOL/UWIN within 48 hours?",
    "Is contact of nearest FRU displayed?",
    "Is stock register updated?",
    "Is ANC first visit within 12 weeks conducted?",
    "Are all first visit lab investigations done?"
]
hbnc_questions = [
    "Are all first visit clinical assessments done?",
    "Are first visit medications given?",
    "Is danger signs counselling provided in first visit?",
    "Is counselling on nutrition, hygiene and breastfeeding done?",
    "Is ANC second visit conducted between 14–26 weeks?",
    "Are second visit lab investigations done?",
    "Are second visit clinical assessments done?",
    "Are second visit medications given?",
    "Is danger signs counselling provided in second visit?",
    "Is ANC third visit conducted?",
    "Are third visit lab investigations done?",
    "Are third visit clinical assessments done?",
    "Is danger signs counselling provided in third visit?",
    "Is ANC fourth visit (36–40 wks) conducted?",
    "Are fourth visit lab investigations done?",
    "Are fourth visit clinical assessments done?",
    "Is danger signs counselling provided in fourth visit?",
    "Is institutional delivery promoted?",
    "Is trained staff available for deliveries?",
    "Are referral slips/registers maintained for deliveries?",
    "Are hygiene protocols and clean delivery kits used?",
    "Is transport arranged for delivery?",
    "Are HRPs/emergencies referred timely with feedback?",
    "Are JSY/JSSK/Ija Boi incentives disbursed properly?",
    "Is respectful maternity care ensured?",
    "Is breastfeeding initiated within 1 hour of birth?",
    "Is postnatal care equipment available (clamp, resuscitator, wraps)?",
    "Are PNC visits conducted on recommended days?",
    "Is postnatal assessment of mother and baby documented?",
    "Is the newborn monitored for weight, feeding, danger signs?",
    "Is exclusive breastfeeding promoted postnatally?",
    "Are postnatal visit records properly maintained?",
    "Is counselling on cord care, hygiene, immunization provided?",
    "Is KMC advised for LBW/preterm babies?",
    "Has ASHA completed 7 HBNC visits (13 for LBW)?",
    "Did ASHA assess temperature, weight, cord care in each visit?",
    "Is ASHA trained and equipped for HBNC?",
    "Is exclusive breastfeeding promoted by ASHA?",
    "Are danger signs identified and referred by ASHA?",
    "Are ASHAs equipped with HBNC kits?",
    "Are ASHAs trained on breastfeeding, hygiene, danger signs?",
    "Are ASHAs oriented on JSY/Eja Boi schemes?",
    "Are ASHA incentives regularly disbursed?",
    "Is ASHA diary/register reviewed regularly?",
    "Are ASHAs treated respectfully at health facilities?"
]

def create_db():
    # Always delete old DB to avoid schema mismatch
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            date TEXT, 
            sub_centre TEXT,
            location TEXT,
            phc TEXT,
            reported_by TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS survey_categories (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY, 
            category_id INTEGER,
            question_text TEXT,
            FOREIGN KEY(category_id) REFERENCES survey_categories(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY, 
            session_id INTEGER,
            question_id INTEGER, 
            answer TEXT, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id),
            FOREIGN KEY(question_id) REFERENCES questions(id)
        )
    ''')
    # Insert categories
    categories = [
        "Infrastructure & Equipment",
        "ANC Services",
        "Delivery & Postnatal Care",
        "HBNC & ASHA Activities"
    ]
    for name in categories:
        c.execute("INSERT INTO survey_categories (name) VALUES (?)", (name,))
    # Insert questions per category
    for cat_id, questions in enumerate([
        infra_questions, anc_questions, delivery_questions, hbnc_questions
    ], start=1):
        for q in questions:
            c.execute('INSERT INTO questions (category_id, question_text) VALUES (?, ?)', (cat_id, q))
    conn.commit()
    conn.close()

def get_categories():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name FROM survey_categories")
    categories = c.fetchall()
    conn.close()
    return categories

def get_questions_by_category(category_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT id, question_text FROM questions WHERE category_id=?''', (category_id,))
    questions = c.fetchall()
    conn.close()
    return questions

def get_category_name(category_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name FROM survey_categories WHERE id=?", (category_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else ""

def get_responses_by_category(category_id, session_id=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if session_id:
        c.execute('''
            SELECT q.id, q.question_text, r.answer, COUNT(r.id)
            FROM questions q
            LEFT JOIN responses r ON q.id = r.question_id AND r.session_id = ?
            WHERE q.category_id=?
            GROUP BY q.id, r.answer
            ORDER BY q.id
        ''', (session_id, category_id))
    else:
        c.execute('''
            SELECT q.id, q.question_text, r.answer, COUNT(r.id)
            FROM questions q
            LEFT JOIN responses r ON q.id = r.question_id
            WHERE q.category_id=?
            GROUP BY q.id, r.answer
            ORDER BY q.id
        ''', (category_id,))
    
    rows = c.fetchall()
    conn.close()
    return rows

def insert_response(session_id, question_id, answer):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''INSERT INTO responses (session_id, question_id, answer) VALUES (?, ?, ?)''', (session_id, question_id, answer))
    conn.commit()
    conn.close()

class DetailsFormScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.date = TextInput(hint_text="Date (YYYY-MM-DD)", multiline=False)
        self.sub_centre = TextInput(hint_text="Sub-Centre Name", multiline=False)
        self.location = TextInput(hint_text="Location", multiline=False)
        self.phc = TextInput(hint_text="PHC", multiline=False)
        self.reported_by = TextInput(hint_text="Reported By", multiline=False)
        self.layout.add_widget(Label(text="Survey Details", font_size=24, bold=True))
        self.layout.add_widget(self.date)
        self.layout.add_widget(self.sub_centre)
        self.layout.add_widget(self.location)
        self.layout.add_widget(self.phc)
        self.layout.add_widget(self.reported_by)
        submit_btn = Button(text="Submit & Proceed", size_hint_y=None, height=50)
        submit_btn.bind(on_press=self.submit_details)
        self.layout.add_widget(submit_btn)
        self.add_widget(self.layout)
    
    def submit_details(self, instance):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''INSERT INTO sessions (date, sub_centre, location, phc, reported_by)
                     VALUES (?, ?, ?, ?, ?)''',
                 (self.date.text, self.sub_centre.text, self.location.text, 
                  self.phc.text, self.reported_by.text))
        session_id = c.lastrowid
        conn.commit()
        conn.close()
        app = App.get_running_app()
        app.current_session_id = session_id
        app.root.current = "dashboard"

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.layout.add_widget(Label(text="Select Survey Category", font_size=24, bold=True))
        self.category_container = GridLayout(cols=2, spacing=10, size_hint_y=0.8)
        self.layout.add_widget(self.category_container)
        # Add Show Results button
        show_results_btn = Button(
            text="Show Survey Results",
            size_hint_y=None,
            height=60,
            background_color=get_color_from_hex("#1cc88a"),
            color=(1,1,1,1),
            font_size=18
        )
        show_results_btn.bind(on_press=self.show_results)
        self.layout.add_widget(show_results_btn)
        self.add_widget(self.layout)
        Clock.schedule_once(self.load_categories)
    
    def load_categories(self, dt):
        self.category_container.clear_widgets()
        categories = get_categories()
        for cat_id, name in categories:
            btn = Button(
                text=name, 
                size_hint_y=None, 
                height=60,
                background_color=get_color_from_hex("#4e73df"),
                color=(1,1,1,1),
                font_size=18
            )
            btn.bind(on_press=lambda x, cid=cat_id: self.open_survey(cid))
            self.category_container.add_widget(btn)
    
    def open_survey(self, category_id):
        app = App.get_running_app()
        app.current_category = category_id
        app.root.current = "survey"
    
    def show_results(self, *args):
        app = App.get_running_app()
        app.root.current = "results"
        app.root.get_screen("results").refresh_categories()

class SurveyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.spinners = {}
        self.build_ui()
    
    def on_pre_enter(self):
        self.load_questions()
    
    def build_ui(self):
        with self.layout.canvas.before:
            Color(*get_color_from_hex("#f5f7fa"))
            self.bg = Rectangle(size=self.layout.size, pos=self.layout.pos)
            self.layout.bind(size=self._update_bg)
        
        # Header
        header = BoxLayout(size_hint=(1, None), height=dp(70), padding=[10, 10, 10, 10], spacing=10)
        with header.canvas.before:
            Color(*get_color_from_hex("#4e73df"))
            self.header_bg = Rectangle(pos=header.pos, size=header.size)
            header.bind(pos=self._update_header_bg, size=self._update_header_bg)
        
        header.add_widget(Label(
            text="Survey App", 
            font_size=26, 
            bold=True, 
            color=(1, 1, 1, 1)
        ))
        self.layout.add_widget(header)

        # ScrollView for questions
        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.questions_box = BoxLayout(
            orientation="vertical", 
            spacing=15, 
            size_hint_y=None, 
            padding=[0, 10, 0, 10]
        )
        self.questions_box.bind(minimum_height=self.questions_box.setter('height'))
        self.scroll.add_widget(self.questions_box)
        self.layout.add_widget(self.scroll)

        # Navigation buttons
        btns = BoxLayout(size_hint=(1, None), height=dp(50), spacing=15, padding=[0, 5, 0, 0])
        
        back_btn = Button(
            text="Back to Dashboard",
            background_color=get_color_from_hex("#6c757d"),
            font_size=16,
            size_hint=(0.5, None),
            height=dp(45)
        )
        back_btn.bind(on_press=self.back_to_dashboard)
        btns.add_widget(back_btn)
        
        submit_btn = Button(
            text="Submit Survey",
            background_color=get_color_from_hex("#1cc88a"),
            font_size=16,
            size_hint=(0.5, None),
            height=dp(45)
        )
        submit_btn.bind(on_press=self.submit)
        btns.add_widget(submit_btn)
        
        self.layout.add_widget(btns)
        self.add_widget(self.layout)
    
    def _update_bg(self, *a):
        self.bg.size = self.layout.size
        self.bg.pos = self.layout.pos

    def _update_header_bg(self, *a):
        self.header_bg.size = self.layout.children[-1].size
        self.header_bg.pos = self.layout.children[-1].pos

    def load_questions(self):
        self.questions_box.clear_widgets()
        self.spinners.clear()
        
        # Get current category from app
        app = App.get_running_app()
        category_id = app.current_category
        category_name = get_category_name(category_id)
        
        # Add category title
        title = Label(
            text=f"Survey: {category_name}",
            font_size=20,
            bold=True,
            size_hint_y=None,
            height=dp(40),
            color=(0.1, 0.1, 0.1, 1)
        )
        self.questions_box.add_widget(title)
        
        # Load questions for this category
        questions = get_questions_by_category(category_id)
        
        for qid, text in questions:
            b = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(100), padding=dp(10), spacing=5)
            with b.canvas.before:
                Color(1, 1, 1, 1)
                RoundedRectangle(pos=b.pos, size=b.size, radius=[14])
                b.bind(pos=self._update_card_bg, size=self._update_card_bg)

            question_label = Label(
                text=text,
                font_size=17,
                bold=True,
                color=(0.15, 0.15, 0.25, 1),
                size_hint_y=None,
                height=dp(35),
                halign='left',
                valign='middle',
            )
            question_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
            b.add_widget(question_label)
            
            rating_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(35))
            radio_group = []
            for i in range(6):
                rb = ToggleButton(
                    group=str(qid),
                    text=str(i),
                    size_hint=(None, None),
                    width=dp(35),
                    height=dp(35),
                    background_color=(0.95, 0.95, 0.98, 1),
                    color=(0.2, 0.2, 0.2, 1),
                    allow_no_selection=True
                )
                rating_box.add_widget(rb)
                radio_group.append(rb)
            self.spinners[qid] = radio_group
            b.add_widget(rating_box)

            label_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(20))
            for label in ["Bad", "Poor", "Avg", "Optimum", "Good", "Excellent"]:
                label_box.add_widget(Label(
                    text=label, 
                    font_size=12, 
                    color=(0.3,0.3,0.3,1), 
                    size_hint=(None, None), 
                    width=dp(35), 
                    height=dp(20), 
                    halign='center', 
                    valign='middle'
                ))
            b.add_widget(label_box)

            self.questions_box.add_widget(b)

    def _update_card_bg(self, instance, *args):
        for instr in instance.canvas.before.children:
            if isinstance(instr, RoundedRectangle):
                instr.pos = instance.pos
                instr.size = instance.size

    def submit(self, *a):
        # Get current session ID
        app = App.get_running_app()
        session_id = app.current_session_id
        
        # Validate all questions answered
        for qid, radio_group in self.spinners.items():
            selected = None
            for idx, btn in enumerate(radio_group):
                if btn.state == 'down':
                    selected = idx
                    break
            if selected is None:
                self.show_modal("Please answer all questions in this survey!", error=True)
                return
        
        # Save responses
        for qid, radio_group in self.spinners.items():
            for idx, btn in enumerate(radio_group):
                if btn.state == 'down':
                    insert_response(session_id, int(qid), str(idx))
                    btn.state = 'normal'
                    break
        
        self.show_modal("Survey submitted successfully!")
        self.back_to_dashboard()

    def back_to_dashboard(self, *args):
        App.get_running_app().root.current = "dashboard"

    def show_modal(self, msg, error=False):
        modal = ModalView(size_hint=(0.7, 0.25))
        color = (1,0,0,1) if error else (0,0.5,0,1)
        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        with box.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=box.pos, size=box.size, radius=[12])
            box.bind(pos=self._update_card_bg, size=self._update_card_bg)
        box.add_widget(Label(text=msg, color=color, font_size=18, bold=True))
        btn = Button(
            text="OK", 
            size_hint=(1, None), 
            height=dp(38), 
            background_color=get_color_from_hex("#4e73df"), 
            color=(1,1,1,1), 
            font_size=16
        )
        btn.bind(on_press=modal.dismiss)
        box.add_widget(btn)
        modal.add_widget(box)
        modal.open()

class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.add_widget(self.layout)
        # Category selection
        self.category_dropdown = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.category_dropdown.bind(minimum_height=self.category_dropdown.setter('height'))
        self.layout.add_widget(Label(text="Select Survey to View Results", font_size=22, bold=True))
        self.layout.add_widget(self.category_dropdown)
        # Results area
        self.result_scroll = ScrollView(size_hint=(1, 1))
        self.result_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.result_box.bind(minimum_height=self.result_box.setter('height'))
        self.result_scroll.add_widget(self.result_box)
        self.layout.add_widget(self.result_scroll)
        self.selected_category = None

    def refresh_categories(self):
        self.category_dropdown.clear_widgets()
        self.result_box.clear_widgets()
        categories = get_categories()
        for cat_id, name in categories:
            btn = Button(
                text=name,
                size_hint_y=None,
                height=50,
                background_color=get_color_from_hex("#4e73df"),
                color=(1,1,1,1),
                font_size=16
            )
            btn.bind(on_press=lambda x, cid=cat_id: self.show_results_for_category(cid))
            self.category_dropdown.add_widget(btn)

    def show_results_for_category(self, category_id):
        self.result_box.clear_widgets()
        category_name = get_category_name(category_id)
        self.result_box.add_widget(Label(text=f"Results: {category_name}", font_size=20, bold=True, size_hint_y=None, height=40))
        
        # Get results for this category
        results = get_responses_by_category(category_id)
        if not results:
            self.result_box.add_widget(Label(text="No responses yet.", font_size=16, color=(1,0,0,1), size_hint_y=None, height=30))
            return
        
        # Group results by question
        question_map = {}
        for qid, text, answer, count in results:
            if qid not in question_map:
                question_map[qid] = {"text": text, "counts": [0]*6}
            if answer is not None and answer.isdigit():
                idx = int(answer)
                if 0 <= idx <= 5:
                    question_map[qid]["counts"][idx] += count
        
        # Display results with pie charts
        for qid, data in question_map.items():
            text = data["text"]
            counts = data["counts"]
            
            # Create question box
            q_box = BoxLayout(orientation='vertical', size_hint_y=None, height=220, padding=5)
            q_box.add_widget(Label(text=text, font_size=15, bold=True, size_hint_y=None, height=30, color=(0.1,0.1,0.2,1)))
            
            # Add pie chart
            if sum(counts) > 0:
                pie_img = self.create_pie_chart(counts)
                q_box.add_widget(pie_img)
            else:
                q_box.add_widget(Label(text="No responses for this question", font_size=14, color=(0.5,0,0,1)))
            
            self.result_box.add_widget(q_box)
        
        # Back button
        back_btn = Button(
            text="Back to Dashboard",
            size_hint_y=None,
            height=45,
            background_color=get_color_from_hex("#1cc88a"),
            color=(1,1,1,1),
            font_size=15
        )
        back_btn.bind(on_press=lambda x: setattr(App.get_running_app().root, 'current', 'dashboard'))
        self.result_box.add_widget(back_btn)

    def create_pie_chart(self, counts):
        labels = ["Bad", "Poor", "Avg", "Optimum", "Good", "Excellent"]
        # Remove zero-counts for better pie chart
        filtered_counts = []
        filtered_labels = []
        for i, (count, label) in enumerate(zip(counts, labels)):
            if count > 0:
                filtered_counts.append(count)
                filtered_labels.append(f"{label} ({count})")
        
        if not filtered_counts:
            filtered_counts = [1]
            filtered_labels = ["No Data"]
        
        # Create the pie chart
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.pie(filtered_counts, labels=filtered_labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Save to buffer
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        
        # Convert to Kivy image
        img = CoreImage(buf, ext='png')
        return Image(texture=img.texture, size_hint_y=None, height=160)

class SurveyApp(App):
    current_category = 1
    current_session_id = None
    
    def build(self):
        create_db()
        sm = ScreenManager()
        
        # Create screens
        sm.add_widget(DetailsFormScreen(name="details"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(SurveyScreen(name="survey"))
        sm.add_widget(ResultsScreen(name="results"))
        
        # Start with details form
        sm.current = "details"
        return sm

if __name__ == "__main__":
    SurveyApp().run()
