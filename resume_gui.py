import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
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

# Include the ResumeBuilder class from the previous code
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
        """Setup custom styles with minimal spacing for one-page resume"""
        # Name header style - MINIMAL spacing
        self.styles.add(ParagraphStyle(
            name='NameHeader',
            parent=self.styles['Heading1'],
            fontSize=14,                # Reduced from 16
            spaceAfter=1,              # Reduced from 2
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Times-Bold'
        ))
        
        # Contact info style - MINIMAL spacing
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            spaceAfter=4,              # Reduced from 8
            fontName='Times-Roman'
        ))
        
        # Section header style - MINIMAL spacing
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=10,               # Reduced from 11
            spaceAfter=1,              # Reduced from 3
            spaceBefore=4,             # Reduced from 8
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Times-Bold'
        ))
        
        # Job title and company style - MINIMAL spacing
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=9,                # Reduced from 10
            spaceAfter=1,              # Reduced from 2
            spaceBefore=2,             # Reduced from 4
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Times-Bold'
        ))
        
        # Bullet point style - MINIMAL spacing
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=8,                # Reduced from 9
            spaceAfter=0,              # Reduced from 1
            leftIndent=12,             # Reduced from 15
            bulletIndent=6,            # Reduced from 8
            alignment=TA_JUSTIFY,
            fontName='Times-Roman'
        ))
        
        # Skills category style - MINIMAL spacing
        self.styles.add(ParagraphStyle(
            name='SkillCategory',
            parent=self.styles['Normal'],
            fontSize=8,                # Reduced from 9
            spaceAfter=0,              # Reduced from 1
            alignment=TA_LEFT,
            fontName='Times-Roman'
        ))
        
        # Education/Project title style - MINIMAL spacing
        self.styles.add(ParagraphStyle(
            name='SubsectionTitle',
            parent=self.styles['Normal'],
            fontSize=9,                # Reduced from 10
            spaceAfter=1,              # Reduced from 2
            spaceBefore=1,             # Reduced from 3
            alignment=TA_LEFT,
            fontName='Times-Bold'
        ))
        
        # Normal style override for general text - MINIMAL spacing
        self.styles.add(ParagraphStyle(
            name='CompactNormal',
            parent=self.styles['Normal'],
            fontSize=8,                # Reduced font size
            spaceAfter=0,              # No space after
            spaceBefore=0,             # No space before
            alignment=TA_JUSTIFY,
            fontName='Times-Roman'
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
        # Name
        name_para = Paragraph(self.resume_data['personal_info']['name'], self.styles['NameHeader'])
        story.append(name_para)
        
        # Contact with manual hyperlinks
        contact_parts = []
        info = self.resume_data['personal_info']
        
        if info.get('location'):
            contact_parts.append(info['location'])
        if info.get('email'):
            contact_parts.append(f'<a href="mailto:{info["email"]}" color="black">{info["email"]}</a>')
        if info.get('phone'):
            contact_parts.append(f'<a href="tel:{info["phone"]}" color="black">{info["phone"]}</a>')
        if info.get('linkedin_display') and info.get('linkedin_url'):
            contact_parts.append(f'<a href="{info["linkedin_url"]}" color="black">{info["linkedin_display"]}</a>')
        if info.get('github_display') and info.get('github_url'):
            contact_parts.append(f'<a href="{info["github_url"]}" color="black">{info["github_display"]}</a>')
        
        contact_text = ' | '.join(contact_parts)
        contact_para = Paragraph(contact_text, self.styles['ContactInfo'])
        story.append(contact_para)

    
    # Updated section methods with minimal spacing
    def _create_section_with_line(self, story, title):
        """Create a section header with underline - NO spacing between title and line"""
        
        # Method 1: Use a single table with text and line (RECOMMENDED)
        section_data = [[title], ['']]
        section_table = Table(section_data, colWidths=[7.5*inch], rowHeights=[12, 1])
        section_table.setStyle(TableStyle([
            # Title row styling
            ('FONTNAME', (0, 0), (0, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 10),
            ('VALIGN', (0, 0), (0, 0), 'BOTTOM'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 0), (0, 0), 0),
            
            # Line row styling
            ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
            ('VALIGN', (0, 1), (0, 1), 'TOP'),
            ('LEFTPADDING', (0, 1), (0, 1), 0),
            ('RIGHTPADDING', (0, 1), (0, 1), 0),
            ('TOPPADDING', (0, 1), (0, 1), 0),
            ('BOTTOMPADDING', (0, 1), (0, 1), 0),
        ]))
        story.append(section_table)
        story.append(Spacer(1, 3))  # Small space after the section header
    
    def _create_profile_section(self, story):
        """Create profile summary section - MINIMAL spacing"""
        if not self.resume_data['profile_summary']:
            return
            
        self._create_section_with_line(story, 'Berufsprofil')
        
        profile_para = Paragraph(self.resume_data['profile_summary'], self.styles['CompactNormal'])
        story.append(profile_para)
        story.append(Spacer(1, 2))     # Reduced from 6
    
    def _create_experience_section(self, story):
        """Create work experience section - MINIMAL spacing"""
        if not self.resume_data['experience']:
            return
            
        self._create_section_with_line(story, 'Berufliche Erfahrung')
        
        for exp in self.resume_data['experience']:
            # Job title with date range in a table - MINIMAL spacing
            job_data = [[
                f"{exp['job_title']} | {exp['company']} | {exp['location']}",
                f"({exp['start_date']} - {exp['end_date']})"
            ]]
            
            job_table = Table(job_data, colWidths=[5.5*inch, 2*inch])
            job_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),     # Reduced from 10
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, 0), 'Times-Bold'),
            ]))
            story.append(job_table)
            # NO SPACER - removed
            
            # Responsibilities as bullet points - MINIMAL spacing
            for resp in exp['responsibilities']:
                bullet_para = Paragraph(f"• {resp}", self.styles['BulletPoint'])
                story.append(bullet_para)
            
            # Technologies if provided - MINIMAL spacing
            if exp['technologies']:
                tech_para = Paragraph(f"<b>Technologien:</b> {exp['technologies']}", self.styles['CompactNormal'])
                story.append(tech_para)
            
            story.append(Spacer(1, 2))                 # Reduced from 4                 
    
    def _create_education_section(self, story):
        """Create education section - MINIMAL spacing"""
        if not self.resume_data['education']:
            return
            
        self._create_section_with_line(story, 'AUSBILDUNG')
        
        for edu in self.resume_data['education']:
            # Institution and degree - MINIMAL spacing
            edu_title = f"{edu['institution']}, {edu['location']}, {edu['degree']} in {edu['field']}"
            edu_para = Paragraph(edu_title, self.styles['JobTitle'])
            story.append(edu_para)
            
            # Focus areas - MINIMAL spacing
            if edu['focus_areas']:
                focus_text = f"Schwerpunkt: {', '.join(edu['focus_areas'])}"
                focus_para = Paragraph(focus_text, self.styles['CompactNormal'])
                story.append(focus_para)
            
            # Date range - MINIMAL spacing
            date_text = f"({edu['start_date']} – {edu['end_date']})"
            date_para = Paragraph(date_text, self.styles['CompactNormal'])
            story.append(date_para)
            story.append(Spacer(1, 2))             # Reduced from 4
    
    def _create_skills_section(self, story):
        """Create technical skills section - MINIMAL spacing"""
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
        
        story.append(Spacer(1, 2))                 # Reduced from 6

    
    def _create_projects_section(self, story):
        """Create projects section - MINIMAL spacing"""
        if not self.resume_data['projects']:
            return
            
        self._create_section_with_line(story, 'PROJEKT ARBEITEN')
        
        for project in self.resume_data['projects']:
            # Project title - MINIMAL spacing
            title_para = Paragraph(f"{project['title'].upper()} | {project['subtitle']}, {project['location']}", 
                                self.styles['JobTitle'])
            story.append(title_para)
            
            # Date range - MINIMAL spacing
            date_para = Paragraph(f"({project['date_range']})", self.styles['CompactNormal'])
            story.append(date_para)
            # NO SPACER - removed
            
            # Description as bullet points - MINIMAL spacing
            for desc in project['description']:
                bullet_para = Paragraph(f"• {desc}", self.styles['BulletPoint'])
                story.append(bullet_para)
            
            story.append(Spacer(1, 2))             # Reduced from 4
    
    def _create_certifications_section(self, story):
        """Create certifications section - MINIMAL spacing"""
        if not self.resume_data['certifications']:
            return
            
        self._create_section_with_line(story, 'Zertifikate')
        
        for cert in self.resume_data['certifications']:
            cert_text = f"• <b>{cert['name']}</b> - Herausgegeben von {cert['issuer']}"
            cert_para = Paragraph(cert_text, self.styles['SkillCategory'])
            story.append(cert_para)
    
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
        return True
    
    def save_data_to_json(self, filename="resume_data.json"):
        """Save resume data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.resume_data, f, indent=2, ensure_ascii=False)
    
    def load_data_from_json(self, filename="resume_data.json"):
        """Load resume data from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.resume_data = json.load(f)
            return True
        except FileNotFoundError:
            return False


class ResumeBuilderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Builder - Professional PDF Generator")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize resume builder
        self.resume_builder = ResumeBuilder()
        
        # Create the GUI
        self.setup_gui()
        
        # Load existing data if available
        self.load_existing_data()
    
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Create main frame with scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_frame, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Create sections
        self.create_header_section(scrollable_frame)
        self.create_personal_info_section(scrollable_frame)
        self.create_profile_section(scrollable_frame)
        self.create_experience_section(scrollable_frame)
        self.create_education_section(scrollable_frame)
        self.create_skills_section(scrollable_frame)
        self.create_projects_section(scrollable_frame)
        self.create_certifications_section(scrollable_frame)
        self.create_action_buttons(scrollable_frame)
    
    def create_header_section(self, parent):
        """Create header with title and file operations"""
        header_frame = ttk.LabelFrame(parent, text="Resume Builder", padding="10")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File operations
        file_frame = ttk.Frame(header_frame)
        file_frame.pack(fill=tk.X)
        
        ttk.Button(file_frame, text="Load Data", command=self.load_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_frame, text="Save Data", command=self.save_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_frame, text="Clear All", command=self.clear_all_data).pack(side=tk.LEFT, padx=(0, 5))
    
    def create_personal_info_section(self, parent):
        """Create personal information section with proper hyperlink fields"""
        personal_frame = ttk.LabelFrame(parent, text="Personal Information", padding="10")
        personal_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Name
        ttk.Label(personal_frame, text="Full Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.name_var, width=50).grid(row=0, column=1, columnspan=2, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Location
        ttk.Label(personal_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.location_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.location_var, width=50).grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Email
        ttk.Label(personal_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.email_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.email_var, width=50).grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Phone
        ttk.Label(personal_frame, text="Phone:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.phone_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.phone_var, width=50).grid(row=3, column=1, columnspan=2, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # LinkedIn - UPDATED with separate fields
        linkedin_frame = ttk.Frame(personal_frame)
        linkedin_frame.grid(row=4, column=0, columnspan=3, sticky=tk.W+tk.E, pady=2)
        
        ttk.Label(linkedin_frame, text="LinkedIn Display Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.linkedin_display_var = tk.StringVar()
        ttk.Entry(linkedin_frame, textvariable=self.linkedin_display_var, width=25).grid(row=0, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 10))
        
        ttk.Label(linkedin_frame, text="LinkedIn URL:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.linkedin_url_var = tk.StringVar()
        ttk.Entry(linkedin_frame, textvariable=self.linkedin_url_var, width=40).grid(row=0, column=3, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Helper text for LinkedIn
        linkedin_help = ttk.Label(linkedin_frame, text="Example: Display='Muhammad Waleed', URL='https://linkedin.com/in/muhammad-waleed'", 
                                font=('Arial', 8), foreground='gray')
        linkedin_help.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(2, 5))
        
        # GitHub - UPDATED with separate fields
        github_frame = ttk.Frame(personal_frame)
        github_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W+tk.E, pady=2)
        
        ttk.Label(github_frame, text="GitHub Display:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.github_display_var = tk.StringVar()
        ttk.Entry(github_frame, textvariable=self.github_display_var, width=25).grid(row=0, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 10))
        
        ttk.Label(github_frame, text="GitHub URL:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.github_url_var = tk.StringVar()
        ttk.Entry(github_frame, textvariable=self.github_url_var, width=40).grid(row=0, column=3, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Helper text for GitHub
        github_help = ttk.Label(github_frame, text="Example: Display='github.com/weedu34', URL='https://github.com/weedu34'", 
                            font=('Arial', 8), foreground='gray')
        github_help.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(2, 5))
        
        # Configure column weights
        personal_frame.columnconfigure(1, weight=1)
        linkedin_frame.columnconfigure(1, weight=1)
        linkedin_frame.columnconfigure(3, weight=2)
        github_frame.columnconfigure(1, weight=1)
        github_frame.columnconfigure(3, weight=2)   
    
    def create_profile_section(self, parent):
        """Create profile summary section"""
        profile_frame = ttk.LabelFrame(parent, text="Profile Summary (Berufsprofil)", padding="10")
        profile_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(profile_frame, text="Profile Summary:").pack(anchor=tk.W)
        self.profile_text = scrolledtext.ScrolledText(profile_frame, height=4, wrap=tk.WORD)
        self.profile_text.pack(fill=tk.X, pady=(5, 0))
    
    def create_experience_section(self, parent):
        """Create work experience section"""
        exp_frame = ttk.LabelFrame(parent, text="Work Experience", padding="10")
        exp_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Experience list
        self.experience_list = []
        
        # Frame for experience entries
        self.exp_entries_frame = ttk.Frame(exp_frame)
        self.exp_entries_frame.pack(fill=tk.X)
        
        # Add experience button
        ttk.Button(exp_frame, text="Add Experience", command=self.add_experience_entry).pack(pady=(10, 0))
    
    def add_experience_entry(self):
        """Add a new experience entry"""
        exp_entry_frame = ttk.LabelFrame(self.exp_entries_frame, text=f"Experience {len(self.experience_list) + 1}", padding="5")
        exp_entry_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Job details
        details_frame = ttk.Frame(exp_entry_frame)
        details_frame.pack(fill=tk.X)
        
        # Job Title
        ttk.Label(details_frame, text="Job Title:").grid(row=0, column=0, sticky=tk.W, pady=2)
        job_title_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=job_title_var, width=30).grid(row=0, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 10))
        
        # Company
        ttk.Label(details_frame, text="Company:").grid(row=0, column=2, sticky=tk.W, pady=2)
        company_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=company_var, width=30).grid(row=0, column=3, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Location
        ttk.Label(details_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=2)
        location_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=location_var, width=30).grid(row=1, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 10))
        
        # Start Date
        ttk.Label(details_frame, text="Start Date:").grid(row=1, column=2, sticky=tk.W, pady=2)
        start_date_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=start_date_var, width=30).grid(row=1, column=3, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # End Date
        ttk.Label(details_frame, text="End Date:").grid(row=2, column=0, sticky=tk.W, pady=2)
        end_date_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=end_date_var, width=30).grid(row=2, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 10))
        
        # Technologies
        ttk.Label(details_frame, text="Technologies:").grid(row=2, column=2, sticky=tk.W, pady=2)
        technologies_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=technologies_var, width=30).grid(row=2, column=3, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Configure column weights
        details_frame.columnconfigure(1, weight=1)
        details_frame.columnconfigure(3, weight=1)
        
        # Responsibilities
        ttk.Label(exp_entry_frame, text="Responsibilities (one per line):").pack(anchor=tk.W, pady=(10, 0))
        responsibilities_text = scrolledtext.ScrolledText(exp_entry_frame, height=3, wrap=tk.WORD)
        responsibilities_text.pack(fill=tk.X, pady=(5, 0))
        
        # Remove button
        ttk.Button(exp_entry_frame, text="Remove", 
                  command=lambda: self.remove_experience_entry(exp_entry_frame)).pack(pady=(5, 0))
        
        # Store references
        exp_data = {
            'frame': exp_entry_frame,
            'job_title': job_title_var,
            'company': company_var,
            'location': location_var,
            'start_date': start_date_var,
            'end_date': end_date_var,
            'technologies': technologies_var,
            'responsibilities': responsibilities_text
        }
        self.experience_list.append(exp_data)
    
    def remove_experience_entry(self, frame):
        """Remove an experience entry"""
        frame.destroy()
        self.experience_list = [exp for exp in self.experience_list if exp['frame'] != frame]
        self.update_experience_labels()
    
    def update_experience_labels(self):
        """Update experience entry labels"""
        for i, exp in enumerate(self.experience_list):
            exp['frame'].configure(text=f"Experience {i + 1}")
    
    def create_education_section(self, parent):
        """Create education section"""
        edu_frame = ttk.LabelFrame(parent, text="Education", padding="10")
        edu_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.education_list = []
        self.edu_entries_frame = ttk.Frame(edu_frame)
        self.edu_entries_frame.pack(fill=tk.X)
        
        ttk.Button(edu_frame, text="Add Education", command=self.add_education_entry).pack(pady=(10, 0))
    
    def add_education_entry(self):
        """Add a new education entry"""
        edu_entry_frame = ttk.LabelFrame(self.edu_entries_frame, text=f"Education {len(self.education_list) + 1}", padding="5")
        edu_entry_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Education details
        details_frame = ttk.Frame(edu_entry_frame)
        details_frame.pack(fill=tk.X)
        
        # Institution
        ttk.Label(details_frame, text="Institution:").grid(row=0, column=0, sticky=tk.W, pady=2)
        institution_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=institution_var, width=40).grid(row=0, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 10))
        
        # Location
        ttk.Label(details_frame, text="Location:").grid(row=0, column=2, sticky=tk.W, pady=2)
        location_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=location_var, width=30).grid(row=0, column=3, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Degree
        ttk.Label(details_frame, text="Degree:").grid(row=1, column=0, sticky=tk.W, pady=2)
        degree_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=degree_var, width=40).grid(row=1, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 10))
        
        # Field
        ttk.Label(details_frame, text="Field:").grid(row=1, column=2, sticky=tk.W, pady=2)
        field_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=field_var, width=30).grid(row=1, column=3, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Start Date
        ttk.Label(details_frame, text="Start Date:").grid(row=2, column=0, sticky=tk.W, pady=2)
        start_date_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=start_date_var, width=40).grid(row=2, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 10))
        
        # End Date
        ttk.Label(details_frame, text="End Date:").grid(row=2, column=2, sticky=tk.W, pady=2)
        end_date_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=end_date_var, width=30).grid(row=2, column=3, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Configure column weights
        details_frame.columnconfigure(1, weight=1)
        details_frame.columnconfigure(3, weight=1)
        
        # Focus Areas
        ttk.Label(edu_entry_frame, text="Focus Areas (comma separated):").pack(anchor=tk.W, pady=(10, 0))
        focus_areas_var = tk.StringVar()
        ttk.Entry(edu_entry_frame, textvariable=focus_areas_var).pack(fill=tk.X, pady=(5, 0))
        
        # Remove button
        ttk.Button(edu_entry_frame, text="Remove", 
                  command=lambda: self.remove_education_entry(edu_entry_frame)).pack(pady=(5, 0))
        
        # Store references
        edu_data = {
            'frame': edu_entry_frame,
            'institution': institution_var,
            'location': location_var,
            'degree': degree_var,
            'field': field_var,
            'start_date': start_date_var,
            'end_date': end_date_var,
            'focus_areas': focus_areas_var
        }
        self.education_list.append(edu_data)
    
    def remove_education_entry(self, frame):
        """Remove an education entry"""
        frame.destroy()
        self.education_list = [edu for edu in self.education_list if edu['frame'] != frame]
        self.update_education_labels()
    
    def update_education_labels(self):
        """Update education entry labels"""
        for i, edu in enumerate(self.education_list):
            edu['frame'].configure(text=f"Education {i + 1}")
    
    def create_skills_section(self, parent):
        """Create skills section"""
        skills_frame = ttk.LabelFrame(parent, text="Technical Skills", padding="10")
        skills_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Programming Languages
        ttk.Label(skills_frame, text="Programming Languages (comma separated):").pack(anchor=tk.W)
        self.programming_var = tk.StringVar()
        ttk.Entry(skills_frame, textvariable=self.programming_var).pack(fill=tk.X, pady=(5, 10))
        
        # Technical Skills
        ttk.Label(skills_frame, text="Technical Skills (comma separated):").pack(anchor=tk.W)
        self.technical_var = tk.StringVar()
        ttk.Entry(skills_frame, textvariable=self.technical_var).pack(fill=tk.X, pady=(5, 10))
        
        # Software Development
        ttk.Label(skills_frame, text="Software Development (comma separated):").pack(anchor=tk.W)
        self.software_var = tk.StringVar()
        ttk.Entry(skills_frame, textvariable=self.software_var).pack(fill=tk.X, pady=(5, 0))
    
    def create_projects_section(self, parent):
        """Create projects section"""
        proj_frame = ttk.LabelFrame(parent, text="Projects", padding="10")
        proj_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.projects_list = []
        self.proj_entries_frame = ttk.Frame(proj_frame)
        self.proj_entries_frame.pack(fill=tk.X)
        
        ttk.Button(proj_frame, text="Add Project", command=self.add_project_entry).pack(pady=(10, 0))
    
    def add_project_entry(self):
        """Add a new project entry"""
        proj_entry_frame = ttk.LabelFrame(self.proj_entries_frame, text=f"Project {len(self.projects_list) + 1}", padding="5")
        proj_entry_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Project details
        details_frame = ttk.Frame(proj_entry_frame)
        details_frame.pack(fill=tk.X)
        
        # Title
        ttk.Label(details_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=2)
        title_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=title_var, width=50).grid(row=0, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Subtitle
        ttk.Label(details_frame, text="Subtitle:").grid(row=1, column=0, sticky=tk.W, pady=2)
        subtitle_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=subtitle_var, width=50).grid(row=1, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Location
        ttk.Label(details_frame, text="Location:").grid(row=2, column=0, sticky=tk.W, pady=2)
        location_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=location_var, width=50).grid(row=2, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Date Range
        ttk.Label(details_frame, text="Date Range:").grid(row=3, column=0, sticky=tk.W, pady=2)
        date_range_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=date_range_var, width=50).grid(row=3, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        
        # Configure column weights
        details_frame.columnconfigure(1, weight=1)
        
        # Description
        ttk.Label(proj_entry_frame, text="Description (one bullet point per line):").pack(anchor=tk.W, pady=(10, 0))
        description_text = scrolledtext.ScrolledText(proj_entry_frame, height=3, wrap=tk.WORD)
        description_text.pack(fill=tk.X, pady=(5, 0))
        
        # Remove button
        ttk.Button(proj_entry_frame, text="Remove", 
                  command=lambda: self.remove_project_entry(proj_entry_frame)).pack(pady=(5, 0))
        
        # Store references
        proj_data = {
            'frame': proj_entry_frame,
            'title': title_var,
            'subtitle': subtitle_var,
            'location': location_var,
            'date_range': date_range_var,
            'description': description_text
        }
        self.projects_list.append(proj_data)
    
    def remove_project_entry(self, frame):
        """Remove a project entry"""
        frame.destroy()
        self.projects_list = [proj for proj in self.projects_list if proj['frame'] != frame]
        self.update_project_labels()
    
    def update_project_labels(self):
        """Update project entry labels"""
        for i, proj in enumerate(self.projects_list):
            proj['frame'].configure(text=f"Project {i + 1}")
    
    def create_certifications_section(self, parent):
        """Create certifications section"""
        cert_frame = ttk.LabelFrame(parent, text="Certifications", padding="10")
        cert_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.certifications_list = []
        self.cert_entries_frame = ttk.Frame(cert_frame)
        self.cert_entries_frame.pack(fill=tk.X)
        
        ttk.Button(cert_frame, text="Add Certification", command=self.add_certification_entry).pack(pady=(10, 0))
    
    def add_certification_entry(self):
        """Add a new certification entry"""
        cert_entry_frame = ttk.Frame(self.cert_entries_frame)
        cert_entry_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Name
        ttk.Label(cert_entry_frame, text="Certification Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        name_var = tk.StringVar()
        ttk.Entry(cert_entry_frame, textvariable=name_var, width=40).grid(row=0, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 10))
        
        # Issuer
        ttk.Label(cert_entry_frame, text="Issuer:").grid(row=0, column=2, sticky=tk.W, pady=2)
        issuer_var = tk.StringVar()
        ttk.Entry(cert_entry_frame, textvariable=issuer_var, width=30).grid(row=0, column=3, sticky=tk.W+tk.E, pady=2, padx=(5, 10))
        
        # Remove button
        ttk.Button(cert_entry_frame, text="Remove", 
                  command=lambda: self.remove_certification_entry(cert_entry_frame)).grid(row=0, column=4, padx=(5, 0))
        
        # Configure column weights
        cert_entry_frame.columnconfigure(1, weight=1)
        cert_entry_frame.columnconfigure(3, weight=1)
        
        # Store references
        cert_data = {
            'frame': cert_entry_frame,
            'name': name_var,
            'issuer': issuer_var
        }
        self.certifications_list.append(cert_data)
    
    def remove_certification_entry(self, frame):
        """Remove a certification entry"""
        frame.destroy()
        self.certifications_list = [cert for cert in self.certifications_list if cert['frame'] != frame]
    
    def create_action_buttons(self, parent):
        """Create action buttons"""
        action_frame = ttk.LabelFrame(parent, text="Actions", padding="10")
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        button_frame = ttk.Frame(action_frame)
        button_frame.pack()
        
        ttk.Button(button_frame, text="Generate PDF", command=self.generate_pdf, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Preview Data", command=self.preview_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Load Sample", command=self.load_sample_data).pack(side=tk.LEFT)
    
    def collect_data(self):
        """Collect all data from the GUI"""
        # Reset resume builder
        self.resume_builder = ResumeBuilder()
        
        # Personal info with manual hyperlinks
        self.resume_builder.resume_data['personal_info'] = {
            'name': self.name_var.get(),
            'location': self.location_var.get(),
            'email': self.email_var.get(),
            'phone': self.phone_var.get(),
            'linkedin_display': self.linkedin_display_var.get(),
            'linkedin_url': self.linkedin_url_var.get(),
            'github_display': self.github_display_var.get(),
            'github_url': self.github_url_var.get()
        }
        
        # Profile summary
        profile_text = self.profile_text.get("1.0", tk.END).strip()
        if profile_text:
            self.resume_builder.add_profile_summary(profile_text)
        
        # Experience
        for exp in self.experience_list:
            responsibilities_text = exp['responsibilities'].get("1.0", tk.END).strip()
            responsibilities = [line.strip() for line in responsibilities_text.split('\n') if line.strip()]
            
            if exp['job_title'].get() and exp['company'].get():
                self.resume_builder.add_experience(
                    job_title=exp['job_title'].get(),
                    company=exp['company'].get(),
                    location=exp['location'].get(),
                    start_date=exp['start_date'].get(),
                    end_date=exp['end_date'].get(),
                    responsibilities=responsibilities,
                    technologies=exp['technologies'].get()
                )
        
        # Education
        for edu in self.education_list:
            focus_areas_text = edu['focus_areas'].get()
            focus_areas = [area.strip() for area in focus_areas_text.split(',') if area.strip()]
            
            if edu['institution'].get() and edu['degree'].get():
                self.resume_builder.add_education(
                    institution=edu['institution'].get(),
                    location=edu['location'].get(),
                    degree=edu['degree'].get(),
                    field=edu['field'].get(),
                    start_date=edu['start_date'].get(),
                    end_date=edu['end_date'].get(),
                    focus_areas=focus_areas
                )
        
        # Skills
        programming_skills = [skill.strip() for skill in self.programming_var.get().split(',') if skill.strip()]
        technical_skills = [skill.strip() for skill in self.technical_var.get().split(',') if skill.strip()]
        software_skills = [skill.strip() for skill in self.software_var.get().split(',') if skill.strip()]
        
        self.resume_builder.add_skills(
            programming=programming_skills,
            technical=technical_skills,
            software=software_skills
        )
        
        # Projects
        for proj in self.projects_list:
            description_text = proj['description'].get("1.0", tk.END).strip()
            description = [line.strip() for line in description_text.split('\n') if line.strip()]
            
            if proj['title'].get():
                self.resume_builder.add_project(
                    title=proj['title'].get(),
                    subtitle=proj['subtitle'].get(),
                    location=proj['location'].get(),
                    date_range=proj['date_range'].get(),
                    description=description
                )
        
        # Certifications
        for cert in self.certifications_list:
            if cert['name'].get() and cert['issuer'].get():
                self.resume_builder.add_certification(
                    name=cert['name'].get(),
                    issuer=cert['issuer'].get()
                )
    
    def generate_pdf(self):
        """Generate PDF resume"""
        try:
            self.collect_data()
            
            # Ask for filename
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Resume As"
            )
            
            if filename:
                self.resume_builder.generate_pdf(filename)
                messagebox.showinfo("Success", f"Resume generated successfully!\nSaved as: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF:\n{str(e)}")
    
    def preview_data(self):
        """Preview collected data"""
        try:
            self.collect_data()
            
            # Create preview window
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Data Preview")
            preview_window.geometry("600x400")
            
            # Create text widget with scrollbar
            text_frame = ttk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            preview_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
            preview_text.pack(fill=tk.BOTH, expand=True)
            
            # Display data
            data_str = json.dumps(self.resume_builder.resume_data, indent=2, ensure_ascii=False)
            preview_text.insert("1.0", data_str)
            preview_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview data:\n{str(e)}")
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            self.collect_data()
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                title="Save Resume Data As"
            )
            
            if filename:
                self.resume_builder.save_data_to_json(filename)
                messagebox.showinfo("Success", f"Data saved successfully!\nSaved as: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data:\n{str(e)}")
    
    def load_data(self):
        """Load data from JSON file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")],
                title="Load Resume Data"
            )
            
            if filename:
                if self.resume_builder.load_data_from_json(filename):
                    self.populate_gui_from_data()
                    messagebox.showinfo("Success", "Data loaded successfully!")
                else:
                    messagebox.showerror("Error", "Failed to load data from file")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n{str(e)}")
    
    def load_existing_data(self):
        """Load existing sample data if available"""
        if self.resume_builder.load_data_from_json("resume_data.json"):
            self.populate_gui_from_data()
    
    def populate_gui_from_data(self):
        """Populate GUI fields from loaded data"""
        data = self.resume_builder.resume_data
        
        # Personal info
        self.name_var.set(data['personal_info'].get('name', ''))
        self.location_var.set(data['personal_info'].get('location', ''))
        self.email_var.set(data['personal_info'].get('email', ''))
        self.phone_var.set(data['personal_info'].get('phone', ''))
        # Handle both old and new data formats
        personal_info = data['personal_info']

        # LinkedIn fields
        if 'linkedin_display' in personal_info:
            # New format with separate display and URL
            self.linkedin_display_var.set(personal_info.get('linkedin_display', ''))
            self.linkedin_url_var.set(personal_info.get('linkedin_url', ''))
        else:
            # Old format - convert to new format
            linkedin_old = personal_info.get('linkedin', '')
            if linkedin_old:
                self.linkedin_display_var.set(f"LinkedIn: {linkedin_old}")
                self.linkedin_url_var.set(f"https://linkedin.com/in/{linkedin_old.lower().replace(' ', '-')}")
            else:
                self.linkedin_display_var.set('')
                self.linkedin_url_var.set('')

        # GitHub fields
        if 'github_display' in personal_info:
            # New format with separate display and URL
            self.github_display_var.set(personal_info.get('github_display', ''))
            self.github_url_var.set(personal_info.get('github_url', ''))
        else:
            # Old format - convert to new format
            github_old = personal_info.get('github', '')
            if github_old:
                # Check if it already contains github.com
                if github_old.startswith('github.com/'):
                    self.github_display_var.set(github_old)
                    self.github_url_var.set(f"https://{github_old}")
                elif github_old.startswith('https://'):
                    self.github_display_var.set(github_old.replace('https://', ''))
                    self.github_url_var.set(github_old)
                else:
                    # Just username
                    self.github_display_var.set(f"github.com/{github_old}")
                    self.github_url_var.set(f"https://github.com/{github_old}")
            else:
                self.github_display_var.set('')
                self.github_url_var.set('')
        
        # Profile summary
        self.profile_text.delete("1.0", tk.END)
        self.profile_text.insert("1.0", data.get('profile_summary', ''))
        
        # Clear existing entries
        self.clear_dynamic_entries()
        
        # Experience
        for exp in data.get('experience', []):
            self.add_experience_entry()
            last_exp = self.experience_list[-1]
            last_exp['job_title'].set(exp.get('job_title', ''))
            last_exp['company'].set(exp.get('company', ''))
            last_exp['location'].set(exp.get('location', ''))
            last_exp['start_date'].set(exp.get('start_date', ''))
            last_exp['end_date'].set(exp.get('end_date', ''))
            last_exp['technologies'].set(exp.get('technologies', ''))
            last_exp['responsibilities'].delete("1.0", tk.END)
            last_exp['responsibilities'].insert("1.0", '\n'.join(exp.get('responsibilities', [])))
        
        # Education
        for edu in data.get('education', []):
            self.add_education_entry()
            last_edu = self.education_list[-1]
            last_edu['institution'].set(edu.get('institution', ''))
            last_edu['location'].set(edu.get('location', ''))
            last_edu['degree'].set(edu.get('degree', ''))
            last_edu['field'].set(edu.get('field', ''))
            last_edu['start_date'].set(edu.get('start_date', ''))
            last_edu['end_date'].set(edu.get('end_date', ''))
            last_edu['focus_areas'].set(', '.join(edu.get('focus_areas', [])))
        
        # Skills
        skills = data.get('skills', {})
        self.programming_var.set(', '.join(skills.get('programming', [])))
        self.technical_var.set(', '.join(skills.get('technical', [])))
        self.software_var.set(', '.join(skills.get('software', [])))
        
        # Projects
        for proj in data.get('projects', []):
            self.add_project_entry()
            last_proj = self.projects_list[-1]
            last_proj['title'].set(proj.get('title', ''))
            last_proj['subtitle'].set(proj.get('subtitle', ''))
            last_proj['location'].set(proj.get('location', ''))
            last_proj['date_range'].set(proj.get('date_range', ''))
            last_proj['description'].delete("1.0", tk.END)
            last_proj['description'].insert("1.0", '\n'.join(proj.get('description', [])))
        
        # Certifications
        for cert in data.get('certifications', []):
            self.add_certification_entry()
            last_cert = self.certifications_list[-1]
            last_cert['name'].set(cert.get('name', ''))
            last_cert['issuer'].set(cert.get('issuer', ''))
    
    def clear_dynamic_entries(self):
        """Clear all dynamic entries"""
        # Clear experience entries
        for exp in self.experience_list:
            exp['frame'].destroy()
        self.experience_list.clear()
        
        # Clear education entries
        for edu in self.education_list:
            edu['frame'].destroy()
        self.education_list.clear()
        
        # Clear project entries
        for proj in self.projects_list:
            proj['frame'].destroy()
        self.projects_list.clear()
        
        # Clear certification entries
        for cert in self.certifications_list:
            cert['frame'].destroy()
        self.certifications_list.clear()
    
    def clear_all_data(self):
        """Clear all data from the form"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all data?"):
            # Clear personal info
            self.name_var.set('')
            self.location_var.set('')
            self.email_var.set('')
            self.phone_var.set('')
            self.linkedin_var.set('')
            self.github_var.set('')
            
            # Clear profile summary
            self.profile_text.delete("1.0", tk.END)
            
            # Clear skills
            self.programming_var.set('')
            self.technical_var.set('')
            self.software_var.set('')
            
            # Clear dynamic entries
            self.clear_dynamic_entries()
    
    def load_sample_data(self):
        """Load sample data for demonstration"""
        if messagebox.askyesno("Confirm", "This will replace all current data with sample data. Continue?"):
            # Create sample resume
            sample_resume = create_sample_resume()
            self.resume_builder = sample_resume
            self.populate_gui_from_data()
            messagebox.showinfo("Success", "Sample data loaded successfully!")


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


if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeBuilderGUI(root)
    root.mainloop()