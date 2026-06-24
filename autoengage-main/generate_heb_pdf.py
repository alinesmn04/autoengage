import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import arabic_reshaper
from bidi.algorithm import get_display

def draw_hebrew_text(c, text, x, y, size=12):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    c.setFont('Arial', size)
    # Right align calculation approx
    c.drawRightString(x, y, bidi_text)

def generate_pdf():
    file_path = "AutoEngage_Presentation.pdf"
    
    # Register font
    pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
    
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    
    # Title
    c.setFillColorRGB(0.3, 0.28, 0.9)  # Indigo
    draw_hebrew_text(c, "AutoEngage - סוכן שיווק אוטונומי", width - 50, height - 80, 24)
    
    c.setFillColorRGB(0.4, 0.45, 0.55)
    draw_hebrew_text(c, "סקירת תכונות ויכולות המערכת", width - 50, height - 110, 16)
    
    c.setFillColorRGB(0.1, 0.1, 0.1)
    
    y = height - 160
    
    sections = [
        ("1. גילוי ומחקר (Discovery & Analytics)", [
            ("סריקת פוסטים ויראליים: איתור פוסטים עם פוטנציאל מעורבות גבוה ברשתות חברתיות (Reddit/LinkedIn).",),
            ("דירוג לידים (Lead Scoring): כל משתמש מקבל ציון (חם/קר) על בסיס טקסט התגובה שלו.",)
        ]),
        ("2. יצירת תוכן וקול המותג (Brand Voice)", [
            ("חיקוי קול המותג: למידת סגנון הכתיבה של העסק ושכפולו באמצעות חיפוש וקטורי.",),
            ("כתיבת פוסטים: יצירת פוסטים מותאמים, רעיונות לתוכן והכנת מבחני A/B.",)
        ]),
        ("3. אוטומציה של מובילי לידים (Lead Magnets)", [
            ("סטודיו ספרוני PDF: יצירת מדריכים שיווקיים ברמת פרימיום בצורה אוטומטית לחלוטין.",),
            ("הסוכן מקבל נושא, בונה מתווה של 5 פרקים ומעצב קובץ מוכן להורדה.",)
        ]),
        ("4. בקרת איכות (QA & Safety)", [
            ("בדיקת 'מילות איסור': וידוא שאין מילים שאסור להשתמש בהן בפוסטים.",),
            ("מניעת AI Smell: וידוא שהטקסט נשמע אנושי ואותנטי, ותיקון אוטומטי אם נדרש.",)
        ]),
        ("5. פניות אישיות (Outreach DM)", [
            ("ניסוח הודעות אישיות: המערכת מזהה לידים חמים ומנסחת פנייה מותאמת אישית לתיבת ההודעות.",),
            ("תיעוד שיחות: רישום ומעקב אחרי ההודעות שנשלחו.",)
        ])
    ]
    
    for title, bullet_points in sections:
        c.setFillColorRGB(0.3, 0.28, 0.9)
        draw_hebrew_text(c, title, width - 50, y, 16)
        y -= 25
        
        c.setFillColorRGB(0.2, 0.25, 0.3)
        for point in bullet_points:
            draw_hebrew_text(c, "• " + point[0], width - 60, y, 12)
            y -= 20
        
        y -= 15
        
        if y < 100:
            c.showPage()
            y = height - 80

    c.save()
    print("PDF created successfully at", file_path)

if __name__ == "__main__":
    generate_pdf()
