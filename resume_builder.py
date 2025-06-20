import json
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from pathlib import Path

class ResumeBuilder:
    def __init__(self):
        self.resume_data = {
            'personal_info': {
                'name': '',
                'location': '',
                'email': '',
                'phone': '',
                'linkedin': '',
                'github': ''
            },
            'profile_summary': '',
            'experience': [],
            'education': [],
            'skills': {
                'programming': [],
                'technical': [],
                'software': []
            },
            'projects': [],
            'certifications': []
        }
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles matching the LaTeX resume format"""
        # Name header style
        self.styles.add(ParagraphStyle(
            name='NameHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=2,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            spaceAfter=8,
            fontName='Helvetica'
        ))
        
        # Section header style (like "Berufsprofil", "Berufliche Erfahrung")
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=11,
            spaceAfter=3,
            spaceBefore=8,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        # Job title and company style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=2,
            spaceBefore=4,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=1,
            leftIndent=15,
            bulletIndent=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Skills category style
        self.styles.add(ParagraphStyle(
            name='SkillCategory',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=1,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))
        
        # Education/Project title style
        self.styles.add(ParagraphStyle(
            name='SubsectionTitle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=2,
            spaceBefore=3,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Date/location style
        self.styles.add(ParagraphStyle(
            name='DateLocation',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        ))

    def add_personal_info(self, name, location, email, phone, linkedin=None, github=None):
        """Add personal information"""
        self.resume_data['personal_info'] = {
            'name': name,
            'location': location,
            'email': email,
            'phone': phone,
            'linkedin': linkedin or '',
            'github': github or ''
        }
    
    def add_profile_summary(self, summary):
        """Add profile summary (Berufsprofil)"""
        self.resume_data['profile_summary'] = summary
    
    def add_experience(self, job_title, company, location, start_date, end_date, responsibilities, technologies=None):
        """Add work experience"""
        experience = {
            'job_title': job_title,
            'company': company,
            'location': location,
            'start_date': start_date,
            'end_date': end_date,
            'responsibilities': responsibilities,  # List of bullet points
            'technologies': technologies or ''
        }
        self.resume_data['experience'].append(experience)
    
    def add_education(self, institution, location, degree, field, start_date, end_date, focus_areas=None):
        """Add education"""
        education = {
            'institution': institution,
            'location': location,
            'degree': degree,
            'field': field,
            'start_date': start_date,
            'end_date': end_date,
            'focus_areas': focus_areas or []
        }
        self.resume_data['education'].append(education)
    
    def add_skills(self, programming=None, technical=None, software=None):
        """Add technical skills"""
        if programming:
            self.resume_data['skills']['programming'].extend(programming)
        if technical:
            self.resume_data['skills']['technical'].extend(technical)
        if software:
            self.resume_data['skills']['software'].extend(software)
    
    def add_project(self, title, subtitle, location, date_range, description):
        """Add project"""
        project = {
            'title': title,
            'subtitle': subtitle,
            'location': location,
            'date_range': date_range,
            'description': description
        }
        self.resume_data['projects'].append(project)
    
    def add_certification(self, name, issuer):
        """Add certification"""
        cert = {
            'name': name,
            'issuer': issuer
        }
        self.resume_data['certifications'].append(cert)
    
    def _create_header(self, story):
        """Create the header section with name and contact info"""
        # Name
        name_para = Paragraph(self.resume_data['personal_info']['name'], self.styles['NameHeader'])
        story.append(name_para)
        
        # Contact information
        contact_parts = []
        info = self.resume_data['personal_info']
        
        if info['location']:
            contact_parts.append(info['location'])
        if info['email']:
            contact_parts.append(info['email'])
        if info['phone']:
            contact_parts.append(info['phone'])
        if info['linkedin']:
            contact_parts.append(f"LinkedIn: {info['linkedin']}")
        if info['github']:
            contact_parts.append(info['github'])
        
        contact_text = ' | '.join(contact_parts)
        contact_para = Paragraph(contact_text, self.styles['ContactInfo'])
        story.append(contact_para)
    
    def _create_section_with_line(self, story, title):
        """Create a section header with underline (like in LaTeX version)"""
        # Create a table with the title and a line
        section_para = Paragraph(f"<b>{title}</b>", self.styles['SectionHeader'])
        story.append(section_para)
        
        # Add a horizontal line
        line_table = Table([[''], ['']], colWidths=[7.5*inch], rowHeights=[1, 1])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 2))
    
    def _create_profile_section(self, story):
        """Create profile summary section"""
        if not self.resume_data['profile_summary']:
            return
            
        self._create_section_with_line(story, 'Berufsprofil')
        
        profile_para = Paragraph(self.resume_data['profile_summary'], self.styles['Normal'])
        story.append(profile_para)
        story.append(Spacer(1, 6))
    
    def _create_experience_section(self, story):
        """Create work experience section"""
        if not self.resume_data['experience']:
            return
            
        self._create_section_with_line(story, 'Berufliche Erfahrung')
        
        for exp in self.resume_data['experience']:
            # Job title with date range in a table
            job_data = [[
                f"{exp['job_title']} | {exp['company']} | {exp['location']}",
                f"({exp['start_date']} - {exp['end_date']})"
            ]]
            
            job_table = Table(job_data, colWidths=[5.5*inch, 2*inch])
            job_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),  # Make job title bold
            ]))
            story.append(job_table)
            story.append(Spacer(1, 2))
            
            # Responsibilities as bullet points
            for resp in exp['responsibilities']:
                bullet_para = Paragraph(f"• {resp}", self.styles['BulletPoint'])
                story.append(bullet_para)
            
            # Technologies if provided
            if exp['technologies']:
                tech_para = Paragraph(f"<b>Technologien:</b> {exp['technologies']}", self.styles['Normal'])
                story.append(tech_para)
            
            story.append(Spacer(1, 4))
    
    def _create_education_section(self, story):
        """Create education section"""
        if not self.resume_data['education']:
            return
            
        self._create_section_with_line(story, 'AUSBILDUNG')
        
        for edu in self.resume_data['education']:
            # Institution and degree
            edu_title = f"{edu['institution']}, {edu['location']}, {edu['degree']} in {edu['field']}"
            edu_para = Paragraph(edu_title, self.styles['JobTitle'])  # Use JobTitle style which is bold
            story.append(edu_para)
            
            # Focus areas
            if edu['focus_areas']:
                focus_text = f"Schwerpunkt: {', '.join(edu['focus_areas'])}"
                focus_para = Paragraph(focus_text, self.styles['Normal'])
                story.append(focus_para)
            
            # Date range
            date_text = f"({edu['start_date']} – {edu['end_date']})"
            date_para = Paragraph(date_text, self.styles['Normal'])
            story.append(date_para)
            story.append(Spacer(1, 4))
    
    def _create_skills_section(self, story):
        """Create technical skills section"""
        skills = self.resume_data['skills']
        if not any([skills['programming'], skills['technical'], skills['software']]):
            return
            
        self._create_section_with_line(story, 'Technische Fähigkeiten')
        
        if skills['programming']:
            prog_text = f"• <b>Programmiersprachen:</b> {', '.join(skills['programming'])}"
            prog_para = Paragraph(prog_text, self.styles['SkillCategory'])
            story.append(prog_para)
        
        if skills['technical']:
            tech_text = f"• <b>Technische Fähigkeiten:</b> {', '.join(skills['technical'])}"
            tech_para = Paragraph(tech_text, self.styles['SkillCategory'])
            story.append(tech_para)
        
        if skills['software']:
            soft_text = f"• <b>Software-Entwicklung:</b> {', '.join(skills['software'])}"
            soft_para = Paragraph(soft_text, self.styles['SkillCategory'])
            story.append(soft_para)
        
        story.append(Spacer(1, 6))
    
    def _create_projects_section(self, story):
        """Create projects section"""
        if not self.resume_data['projects']:
            return
            
        self._create_section_with_line(story, 'PROJEKT ARBEITEN')
        
        for project in self.resume_data['projects']:
            # Project title
            title_para = Paragraph(f"{project['title'].upper()} | {project['subtitle']}, {project['location']}", 
                                 self.styles['JobTitle'])  # Use JobTitle style which is bold
            story.append(title_para)
            
            # Date range
            date_para = Paragraph(f"({project['date_range']})", self.styles['Normal'])
            story.append(date_para)
            story.append(Spacer(1, 2))
            
            # Description as bullet points
            for desc in project['description']:
                bullet_para = Paragraph(f"• {desc}", self.styles['BulletPoint'])
                story.append(bullet_para)
            
            story.append(Spacer(1, 4))
    
    def _create_certifications_section(self, story):
        """Create certifications section"""
        if not self.resume_data['certifications']:
            return
            
        self._create_section_with_line(story, 'Zertifikate')
        
        for cert in self.resume_data['certifications']:
            cert_text = f"• <b>{cert['name']}</b> - Herausgegeben von {cert['issuer']}"
            cert_para = Paragraph(cert_text, self.styles['SkillCategory'])
            story.append(cert_para)
        
        story.append(Spacer(1, 6))
    
    def generate_pdf(self, filename="resume.pdf"):
        """Generate the PDF resume"""
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        story = []
        
        # Build the resume sections
        self._create_header(story)
        self._create_profile_section(story)
        self._create_experience_section(story)
        self._create_education_section(story)
        self._create_skills_section(story)
        self._create_projects_section(story)
        self._create_certifications_section(story)
        
        # Build PDF
        doc.build(story)
        print(f"Resume generated successfully: {filename}")
    
    def save_data_to_json(self, filename="resume_data.json"):
        """Save resume data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.resume_data, f, indent=2, ensure_ascii=False)
        print(f"Resume data saved to: {filename}")
    
    def load_data_from_json(self, filename="resume_data.json"):
        """Load resume data from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.resume_data = json.load(f)
            print(f"Resume data loaded from: {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found. Using empty resume data.")


# Example usage and demo
def create_sample_resume():
    """Create a sample resume similar to the provided example"""
    resume = ResumeBuilder()
    
    # Personal information
    resume.add_personal_info(
        name="Muhammad Waleed",
        location="Ilmenau, Germany",
        email="weedu34@gmail.com",
        phone="+49 176 56964658",
        linkedin="Muhammad Waleed",
        github="github.com/weedu34"
    )
    
    # Profile summary
    resume.add_profile_summary(
        "Masterabsolvent in Medientechnologie mit praktischer Erfahrung in Python-Anwendungsentwicklung und "
        "Systemintegration für technische Anwendungen. Spezialisiert auf Datenbankintegration, "
        "Schnittstellen-Entwicklung und Softwareoptimierung. Fundierte Kenntnisse in strukturierter "
        "Problemlösung, technischer Dokumentation und Mitarbeiterschulung bei IT-Systemen. Analytisches "
        "Denkvermögen und eigenständige Arbeitsweise mit ausgeprägtem Teamgeist durch erfolgreiche Projektarbeit."
    )
    
    # Work experience
    resume.add_experience(
        job_title="Master-Arbeit",
        company="Carl Zeiss Jena GmbH",
        location="Germany",
        start_date="April 2024",
        end_date="Okt 2024",
        responsibilities=[
            "Computer Vision-Pipeline-Entwicklung: Entwickelte Echtzeit-Bildverarbeitungssystem für Multispektral-Kamerasysteme mit OpenCV-basierten Algorithmen für Objekterkennung und -verfolgungs",
            "Sensorfusion & Kalibrierung: Implementierte Multi-Sensor-Datenintegration (Kameras, Akzelerometer) für präzise 3D-Objektlokalisierung und Bewegungserkennung",
            "Echtzeit-Objekterkennung: Optimierte Computer Vision-Algorithmen für <50ms Latenz bei 30fps Bildverarbeitung für zeitkritische Anwendungen"
        ],
        technologies="Python, OpenCV, NumPy, Multi-Threading, Sensorfusion, Kamerakalibrierung"
    )
    
    resume.add_experience(
        job_title="Studentische Hilfskraft",
        company="Technische Universität Ilmenau",
        location="Germany",
        start_date="Mai 2022",
        end_date="Sept 2023",
        responsibilities=[
            "Objekterkennung & Klassifizierung: Entwickelte OpenCV-basierte Algorithmen für automatisierte Objekterkennung in beweglichen Umgebungen und Materialdefektklassifizierung",
            "Machine Learning-Integration: Entwickelte und trainierte ML-Modelle für Echtzeit-Objektklassifizierung mit 84% Erkennungsgenauigkei",
            "Prozessunterstützung: Unterstützte Forschungsabteilungen bei der Optimierung von Arbeitsabläufen durch maßgeschneiderte Software-Lösungen"
        ]
    )
    
    # Education
    resume.add_education(
        institution="Technische Universität Ilmenau",
        location="Germany",
        degree="Master",
        field="Medientechnologie",
        start_date="April 2021",
        end_date="Feb 2025",
        focus_areas=["Computer Vision", "Signal Processing", "Bildverarbeitung", "Sensor Technology"]
    )
    
    resume.add_education(
        institution="University of Engineering and Technology",
        location="Taxila, Pakistan",
        degree="Bachelor",
        field="Elektrotechnik",
        start_date="Nov 2012",
        end_date="Juli 2016",
        focus_areas=["Embedded Systems", "Automatisierungstechnik", "Control Systems"]
    )
    
    # Skills
    resume.add_skills(
        programming=["Python", "SQL", "HTML/CSS", "C++", "API-Integration", "Hardware-Software-Schnittstellen", "SQLite", "PostgreSQL - Database Design"],
        technical=["Multi-Sensor-Fusion: Kamera-IMU-Integration", "Sensordatensynchronisation", "Serial Communication", "USB/Bluetooth APIs", "Embedded-Controller-Integration", "Kamerakalibrierung", "Multi-Kamera-Setups", "Bildqualitätsoptimierung"],
        software=["Modulare, wiederverwendbare Komponenten", "User Interface Design", "User Experience Optimization"]
    )
    
    # Projects
    resume.add_project(
        title="IMPLEMENTATION OF A DATA ACQUISITION AND ANALYSIS SOFTWARE FOR HANDHELD MULTISPECTRAL CAMERA SYSTEM",
        subtitle="Masterarbeit, Carl Zeiss Jena GmbH",
        location="Deutschland",
        date_range="April 2024 – Okt 2024",
        description=[
            "Vollständige Software-Stack-Entwicklung von Anforderungsanalyse bis Deployment für präzise optische Systeme",
            "Integration verschiedener Hardware-Komponenten (Kameras, Sensoren, Embedded-Controller) mit Python Interfaces"
        ]
    )
    
    resume.add_project(
        title="VIDEO BASED HUMAN ACTION RECOGNITION USING RESERVOIR COMPUTING",
        subtitle="Medienprojekt, Technische Universität Ilmenau",
        location="Deutschland",
        date_range="Dez 2022 – Mai 2023",
        description=[
            "Entwicklung und Training von ML-Modellen für Echtzeit-Anwendungen mit Python und numerischen Optimierungsalgorithmen"
        ]
    )
    
    # Certifications
    resume.add_certification("Python for Data Science, AI & Development", "Coursera")
    resume.add_certification("Machine Learning- From Basics to Advanced", "Udemy")
    resume.add_certification("Python Programming - From Basic to Advanced Level", "Udemy")
    
    return resume


# Interactive resume builder function
def interactive_resume_builder():
    """Interactive function to build resume step by step"""
    resume = ResumeBuilder()
    print("=== Python Resume Builder ===\n")
    
    # Personal Info
    print("1. Personal Information:")
    name = input("Full Name: ")
    location = input("Location: ")
    email = input("Email: ")
    phone = input("Phone: ")
    linkedin = input("LinkedIn (optional): ")
    github = input("GitHub (optional): ")
    resume.add_personal_info(name, location, email, phone, linkedin, github)
    
    # Profile Summary
    print("\n2. Profile Summary:")
    summary = input("Enter your profile summary: ")
    resume.add_profile_summary(summary)
    
    # Experience
    print("\n3. Work Experience:")
    while True:
        add_exp = input("Add work experience? (y/n): ").lower()
        if add_exp != 'y':
            break
            
        job_title = input("Job Title: ")
        company = input("Company: ")
        location = input("Location: ")
        start_date = input("Start Date: ")
        end_date = input("End Date: ")
        
        responsibilities = []
        print("Enter responsibilities (press Enter twice to finish):")
        while True:
            resp = input("• ")
            if not resp:
                break
            responsibilities.append(resp)
        
        technologies = input("Technologies used (optional): ")
        resume.add_experience(job_title, company, location, start_date, end_date, responsibilities, technologies)
    
    return resume


if __name__ == "__main__":
    # Demo: Create sample resume
    print("Creating sample resume...")
    sample_resume = create_sample_resume()
    sample_resume.generate_pdf("sample_resume.pdf")
    sample_resume.save_data_to_json("sample_resume_data.json")
    
    print("\nSample resume created!")
    print("Files generated:")
    print("- sample_resume.pdf")
    print("- sample_resume_data.json")
    
    # Uncomment the line below to use interactive builder
    # interactive_resume = interactive_resume_builder()
    # interactive_resume.generate_pdf("my_resume.pdf")