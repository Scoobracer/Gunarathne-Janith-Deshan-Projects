import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import webbrowser
import re

DATA_FILE = 'reports_data.json'

USERS = {'admin': 'password123'}

LAB_TESTS = {
    "Dengue Test": ["NS1", "IgM", "IgG"],
    "Diabetes Test": ["Fasting Glucose", "HbA1c"],
    "Blood Pressure Test": ["Systolic", "Diastolic"],
    "HIV Test": ["RMD", "MDD", "SSI"],
    "Thalassemia Test": ["Hemoglobin", "MCV", "MCH"],
    "Chikungunya Test": ["IgM", "IgG"],
    "Gonorrhea Test": ["NAAT", "Culture"],
    "CBC": ["WBC", "RBC", "Hemoglobin", "Hematocrit", "MCV", "MCH", "MCHC", "Platelets"],
    "Liver Function Test": ["ALT", "AST", "ALP", "Bilirubin", "Albumin"],
    "Kidney Function Test": ["Creatinine", "BUN", "Uric Acid"],
    "Lipid Profile": ["Total Cholesterol", "HDL", "LDL", "Triglycerides"],
    "Thyroid Function Test": ["TSH", "T3", "T4"],
    "Vitamin D Test": ["Vitamin D25"],
    "Iron Panel": ["Iron", "TIBC", "Ferritin"],
    "CRP": ["C-Reactive Protein"],
    "ESR": ["Erythrocyte Sedimentation Rate"],
    "Urinalysis": ["pH", "Protein", "Glucose", "Ketones", "RBC", "WBC"],
    "Stool Test": ["Occult Blood", "Parasites", "Consistency", "Color"],
    "Electrolyte Panel": ["Sodium", "Potassium", "Chloride", "Bicarbonate"],
    "Prostate Specific Antigen": ["PSA"],
    "Beta hCG": ["hCG Level"],
    "Coagulation Profile": ["PT", "aPTT", "INR"],
    "COVID-19 RT-PCR": ["Cycle Threshold"],
    "HbA1c": ["HbA1c%"],
    "Serum Calcium": ["Calcium Level"],
    "Magnesium Test": ["Serum Magnesium"],
    "Amylase": ["Amylase Level"],
    "Lipase": ["Lipase Level"],
    "Cortisol": ["Morning Cortisol"],
    "Insulin": ["Fasting Insulin"],
    "Troponin I": ["Troponin I Level"],
    "D-Dimer": ["D-Dimer Level"],
    "Hepatitis B": ["HBsAg", "Anti-HBs", "HBV DNA"],
    "Hepatitis C": ["Anti-HCV", "HCV RNA"]
    # Add more if needed...
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def calculate_result(test_name, values):
    try:
        if test_name == "HIV Test":
            score = sum(float(values[k]) for k in values)
            return "Positive" if score > 100000 else "Negative"
        elif test_name == "Diabetes Test":
            fbg = float(values.get("Fasting Glucose", 0))
            hb = float(values.get("HbA1c", 0))
            if fbg > 126 or hb > 6.5:
                return "Positive"
            elif fbg > 100 or hb > 5.7:
                return "Midrange"
            else:
                return "Negative"
        elif test_name == "Blood Pressure Test":
            sys = float(values.get("Systolic", 0))
            dia = float(values.get("Diastolic", 0))
            if sys >= 140 or dia >= 90:
                return "Positive"
            elif sys >= 120 or dia >= 80:
                return "Midrange"
            else:
                return "Negative"
        elif test_name in ["Dengue Test", "Thalassemia Test", "Chikungunya Test", "Gonorrhea Test"]:
            return "Positive"  # Placeholder logic
        else:
            return "-"  # No final diagnosis needed
    except:
        return "Error"

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Lab System Login")
        self.root.geometry("300x180")
        tk.Label(root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)
        tk.Label(root, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)
        tk.Button(root, text="Login", command=self.check_login).pack(pady=10)

    def check_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if USERS.get(username) == password:
            self.root.destroy()
            MainApp()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password")

class MainApp:
    def __init__(self):
        self.data = load_data()
        self.root = tk.Tk()
        self.root.title("Patient Lab Report System")
        self.root.geometry("500x400")
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(pady=20)
        tk.Label(self.main_frame, text="Patient Lab Report System", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.main_frame, text="Add New Report", width=25, command=self.open_add_report).pack(pady=10)
        tk.Button(self.main_frame, text="View Reports", width=25, command=self.open_view_reports).pack(pady=10)
        tk.Button(self.main_frame, text="Exit", width=25, command=self.root.quit).pack(pady=10)
        self.root.mainloop()

    def open_add_report(self):
        AddReportWindow(self.root, self.data, self.refresh_data)

    def open_view_reports(self):
        ViewReportsWindow(self.root, self.data)

    def refresh_data(self):
        self.data = load_data()

class AddReportWindow:
    def __init__(self, parent, data, refresh_callback):
        self.top = tk.Toplevel(parent)
        self.top.title("Add Report")
        self.top.geometry("500x600")
        self.data = data
        self.refresh_callback = refresh_callback

        tk.Label(self.top, text="Patient Name:").pack()
        self.name_entry = tk.Entry(self.top, width=40)
        self.name_entry.pack()

        tk.Label(self.top, text="Phone Number:").pack()
        self.phone_entry = tk.Entry(self.top, width=40)
        self.phone_entry.pack()

        tk.Label(self.top, text="Select Test:").pack()
        self.test_var = tk.StringVar()
        self.test_dropdown = ttk.Combobox(self.top, textvariable=self.test_var, values=list(LAB_TESTS.keys()))
        self.test_dropdown.pack()
        self.test_dropdown.bind("<<ComboboxSelected>>", self.render_parameters)

        self.params_frame = tk.Frame(self.top)
        self.params_frame.pack(pady=10)
        self.param_entries = {}

        self.save_button = tk.Button(self.top, text="Save Report", command=self.save_report)
        self.save_button.pack(pady=10)

    def render_parameters(self, event):
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        self.param_entries = {}
        test_name = self.test_var.get()
        for param in LAB_TESTS[test_name]:
            tk.Label(self.params_frame, text=param + ":").pack()
            entry = tk.Entry(self.params_frame, width=40)
            entry.pack()
            self.param_entries[param] = entry

    def save_report(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        test_name = self.test_var.get()
        values = {param: self.param_entries[param].get().strip() for param in self.param_entries}
        result = calculate_result(test_name, values)
        report = {
            'name': name,
            'test': test_name,
            'values': values,
            'result': result,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data.setdefault(phone, []).append(report)
        save_data(self.data)
        messagebox.showinfo("Saved", f"Report saved")
        self.refresh_callback()
        self.top.destroy()
        

class ViewReportsWindow:
    def __init__(self, parent, data):
        self.top = tk.Toplevel(parent)
        self.top.title("View Reports")
        self.top.geometry("700x600")
        self.data = data

        tk.Label(self.top, text="Enter Phone Number:").pack(pady=5)
        self.phone_entry = tk.Entry(self.top, width=40)
        self.phone_entry.pack()

        tk.Button(self.top, text="Search Reports", command=self.search_reports).pack(pady=5)

        self.report_select_var = tk.StringVar()
        self.report_dropdown = ttk.Combobox(self.top, textvariable=self.report_select_var, state='readonly')
        self.report_dropdown.pack(pady=5)

        self.pdf_button = tk.Button(self.top, text="Generate PDF for Selected Report", command=self.generate_pdf_for_selected, state='disabled')
        self.pdf_button.pack(pady=5)

        self.result_text = scrolledtext.ScrolledText(self.top, width=80, height=20)
        self.result_text.pack(pady=10)

        self.reports_for_phone = []

    def search_reports(self):
        phone = self.phone_entry.get().strip()
        self.result_text.delete('1.0', tk.END)
        self.report_dropdown['values'] = []
        self.report_select_var.set('')
        self.pdf_button.config(state='disabled')

        if phone in self.data:
            self.reports_for_phone = self.data[phone]
            report_list = [f"Report #{i+1}: {r['test']}" for i, r in enumerate(self.reports_for_phone)]
            self.report_dropdown['values'] = report_list

            if report_list:
                self.report_select_var.set(report_list[0])
                self.pdf_button.config(state='normal')

            for idx, report in enumerate(self.reports_for_phone, 1):
                self.result_text.insert(tk.END, f"Report #{idx}\n")
                self.result_text.insert(tk.END, f"Name: {report['name']}\n")
                for param, val in report['values'].items():
                    self.result_text.insert(tk.END, f"  {param}: {val}\n")
                if report['result'] != "-":
                    self.result_text.insert(tk.END, f"Final Result: {report['result']}\n")
                self.result_text.insert(tk.END, "-" * 50 + "\n")
        else:
            self.result_text.insert(tk.END, "No reports found for that number.")

    def generate_pdf_for_selected(self):
        selected = self.report_select_var.get()
        if not selected:
            messagebox.showwarning("Warning", "Please select a report from the dropdown.")
            return

        match = re.search(r'#(\d+):', selected)
        if match:
            idx = int(match.group(1)) - 1
        else:
            messagebox.showerror("Error", "Invalid report format selected.")
            return

        report = self.reports_for_phone[idx]
        phone = self.phone_entry.get().strip()
        self.generate_pdf(phone, report, idx + 1)

    def generate_pdf(self, phone, report, report_number):
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(
            temp_pdf.name,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=80,
            bottomMargin=40
        )

        story = []

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='CenterTitle', fontSize=24, alignment=1, spaceAfter=20,
                                  textColor=colors.darkblue, fontName='Helvetica-Bold'))
        styles.add(ParagraphStyle(name='Heading', fontSize=14, textColor=colors.darkred,
                                  spaceAfter=10, fontName='Helvetica-Bold'))
        styles.add(ParagraphStyle(name='NormalBold', fontSize=12, fontName='Helvetica-Bold'))

        # Optional logo
        logo_path = "asiri.jpg"
        if os.path.exists(logo_path):
            img = Image(logo_path, width=3.0 * inch, height=2.0 * inch)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 12))

        # Title
        story.append(Paragraph("Asiri Laboratories Sri Lanka", styles['CenterTitle']))

        # Receipt and Phone
        receipt_num = random.randint(100000, 999999)
        story.append(Paragraph(f"<b>Receipt Number:</b> {receipt_num}", styles['NormalBold']))
        story.append(Paragraph(f"<b>Time:</b> {report['timestamp']}", styles['NormalBold']))
        story.append(Spacer(1, 12))

        # Report Info
        story.append(Paragraph(f"Report #{report_number}: {report['test']}", styles['Heading']))
        story.append(Paragraph(f"Patient Name: {report['name']}", styles['NormalBold']))
        story.append(Paragraph(f"Phone Number: {phone}", styles['NormalBold']))
        story.append(Spacer(1, 10))

        # Table Data
        data = [["Test", "Result"]]
        for param, val in report['values'].items():
            data.append([param, val])
        if report['result'] != "-":
            data.append(["Observation", report['result']])

        table = Table(data, colWidths=[3 * inch, 3 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.steelblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),

            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

        doc.build(story)
        webbrowser.open_new(temp_pdf.name)

if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
