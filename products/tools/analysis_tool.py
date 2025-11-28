import os
import io
import math
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy import stats

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

import arabic_reshaper
from bidi.algorithm import get_display

# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')


# ----------------- CONFIG: Arabic font file (place it next to the script) -----------------
ARABIC_FONT_PATH = "Amiri-Regular.ttf"   # <-- put your Arabic TTF here
AR_FONT_NAME = "Amiri"                   # internal font name used in ReportLab
EN_FONT_NAME = "Helvetica"               # Standard ReportLab font for English

# ----------------- Helper: Arabic shaping + bidi display -----------------
def arabize(text: str) -> str:
    """
    Reshape Arabic text and apply bidi algorithm.
    This function MUST be called on the *final* string before passing it to ReportLab.
    """
    try:
        # We need str() conversion just in case non-string types slip in
        reshaped = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped)
        return bidi_text
    except Exception:
        return str(text)

# ----------------- Register font (reportlab + matplotlib) -----------------
# Check for Arabic font and register it
if not os.path.exists(ARABIC_FONT_PATH):
    print(f"Warning: {ARABIC_FONT_PATH} not found. Arabic PDF text will likely show as boxes.")
    ARABIC_FONT_AVAILABLE = False
else:
    # ReportLab font registration
    pdfmetrics.registerFont(TTFont(AR_FONT_NAME, ARABIC_FONT_PATH))
    # Matplotlib font registration
    font_manager.fontManager.addfont(ARABIC_FONT_PATH)
    font = font_manager.FontProperties(fname=ARABIC_FONT_PATH)
    plt.rcParams['font.family'] = font.get_name()
    ARABIC_FONT_AVAILABLE = True


# ----------------- PLOTTING FUNCTIONS (No changes needed here for BiDi fix) -----------------

def generate_plot(df, x_col, y_col, r_value, p_value, lang='ar'):
    """ Scatter plot for Numeric vs Numeric """
    
    p_str = "p < 0.001" if p_value < 0.001 else f"p = {p_value:.3f}"
    if lang == 'ar':
        title = f"مخطط تبعثر: {x_col} مقابل {y_col} (r = {r_value:.4f}, {p_str})"
        title = arabize(title)
        x_label = arabize(x_col)
        y_label = arabize(y_col)
    else: # English
        title = f"Scatter Plot: {x_col} vs {y_col} (r = {r_value:.4f}, {p_str})"
        x_label = x_col
        y_label = y_col

    plt.figure(figsize=(8, 5))
    plt.scatter(df[x_col], df[y_col], alpha=0.5, c='blue')
    plt.title(title, fontsize=14)
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel(y_label, fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    plt.close()
    img_buffer.seek(0)
    return img_buffer

def generate_bar_plot(df, cat_col, y_col, lang='ar'):
    """ Bar plot for Categorical vs Numeric (Average of Y) """
    
    group_data = df.groupby(cat_col)[y_col].mean().sort_values()

    if lang == 'ar':
        title = f"متوسط {y_col} لكل مجموعة في {cat_col}"
        title = arabize(title)
        x_label = arabize(cat_col)
        y_label = arabize(f"متوسط {y_col}")
    else: # English
        title = f"Average {y_col} by {cat_col} Group"
        x_label = cat_col
        y_label = f"Average {y_col}"


    plt.figure(figsize=(8, 5))
    group_data.plot(kind='bar', color='teal', alpha=0.7)
    
    plt.title(title, fontsize=14)
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel(y_label, fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    plt.close()
    img_buffer.seek(0)
    return img_buffer

# ----------------- ANALYSIS FUNCTIONS (BiDi Fixes Applied Here) -----------------

def perform_analysis(df, x_col, y_col, lang='ar'):
    """ Numeric vs Numeric Analysis (Correlation) - Unified for both languages """
    
    correlation_r, p_value = stats.pearsonr(df[x_col], df[y_col])

    if math.isnan(correlation_r):
        correlation_r = 0.0
        p_value = 1.0

    r_sq = correlation_r ** 2
    r_abs = abs(correlation_r)
    is_significant = p_value < 0.05
    p_str = "p < 0.001" if p_value < 0.001 else f"p = {p_value:.3f}"

    # --- Language-Specific Text Generation ---
    if lang == 'ar':
        if r_abs >= 0.7:
            strength = "قوية"
            linearity = f"العلاقة خطية بدرجة عالية، حيث يشرح {x_col} نسبة {r_sq:.1%} من تباين {y_col}."
        elif r_abs >= 0.3:
            strength = "متوسطة"
            linearity = f"تظهر العلاقة خطية متوسطة، وتفسر {r_sq:.1%} من تباين {y_col}."
        else:
            strength = "ضعيفة"
            linearity = f"المطابقة ضعيفة؛ تُفسر فقط {r_sq:.1%} من التباين."

        significance = "ذات دلالة إحصائية" if is_significant else "ليست ذات دلالة إحصائية"
        
        if correlation_r > 0:
            direction = "طردية (موجبة)"
        elif correlation_r < 0:
            direction = "عكسية (سالبة)"
        else:
            direction = "محايدة"

        interpretation_raw = (
            f"أظهرت التحليلات علاقة {strength} و{direction} (r = {correlation_r:.4f}) بين {x_col} و {y_col}. "
            f"{linearity} هذه العلاقة {significance} ({p_str})."
        )
        # FIX 1: Apply arabize to the final interpretation string. This is crucial.
        interpretation = arabize(interpretation_raw)
        
    else: # English
        if r_abs >= 0.7:
            strength = "strong"
            linearity = f"The relationship is highly linear, with {x_col} explaining {r_sq:.1%} of the variance in {y_col}."
        elif r_abs >= 0.3:
            strength = "moderate"
            linearity = f"The relationship shows moderate linearity, explaining {r_sq:.1%} of the variance in {y_col}."
        else:
            strength = "weak"
            linearity = f"The fit is weak, explaining only {r_sq:.1%} of the variance."

        significance = "statistically significant" if is_significant else "not statistically significant"
        
        if correlation_r > 0:
            direction = "positive"
        elif correlation_r < 0:
            direction = "negative"
        else:
            direction = "neutral"

        interpretation = (
            f"The analysis showed a {strength} and {direction} relationship (r = {correlation_r:.4f}) between {x_col} and {y_col}. "
            f"{linearity} This relationship is considered {significance} ({p_str})."
        )
    
    plot_buffer = generate_plot(df, x_col, y_col, round(correlation_r, 4), p_value, lang)
    return round(correlation_r, 4), round(p_value, 4), plot_buffer, interpretation


def perform_categorical_analysis(df, cat_col, y_col, lang='ar'):
    """ Categorical vs Numeric Analysis - Unified for both languages """
    
    # 1. Frequency Analysis (Counts)
    counts = df[cat_col].value_counts()
    if counts.empty:
        return None, None, None
        
    most_freq_group = counts.idxmax()
    most_freq_count = counts.max()
    least_freq_group = counts.idxmin()
    least_freq_count = counts.min()

    # 2. Dependent Variable Analysis (Average of Y)
    means = df.groupby(cat_col)[y_col].mean()
    highest_y_group = means.idxmax()
    highest_y_val = means.max()
    lowest_y_group = means.idxmin()
    lowest_y_val = means.min()

    # 3. Generate Plot
    plot_buffer = generate_bar_plot(df, cat_col, y_col, lang)

    # 4. Create Summary Table Data (DataFrame labels depend on language)
    if lang == 'ar':
        summary_df = pd.DataFrame({
            'المجموعة (Group)': means.index,
            'العدد (Count)': df[cat_col].value_counts()[means.index],
            f'متوسط {y_col}': means.values
        }).reset_index(drop=True)
        # Sort by Average Y for the table display
        summary_df = summary_df.sort_values(by=f'متوسط {y_col}', ascending=False).head(5)
    else: # English
        summary_df = pd.DataFrame({
            'Group': means.index,
            'Count': df[cat_col].value_counts()[means.index],
            f'Average {y_col}': means.values
        }).reset_index(drop=True)
        # Sort by Average Y for the table display
        summary_df = summary_df.sort_values(by=f'Average {y_col}', ascending=False).head(5)

    # 5. Interpretation Text
    if lang == 'ar':
        interpretation_raw = (
            f"بتحليل المتغير التصنيفي '{cat_col}': \n"
            f"1. من حيث التكرار: المجموعة الأكثر شيوعاً هي '{most_freq_group}' (العدد={most_freq_count})، "
            f"بينما المجموعة الأقل شيوعاً هي '{least_freq_group}' (العدد={least_freq_count}). \n"
            f"2. بالنسبة للمتغير التابع '{y_col}': سجلت المجموعة '{highest_y_group}' أعلى متوسط "
            f"({highest_y_val:.2f})، بينما سجلت المجموعة '{lowest_y_group}' أقل متوسط ({lowest_y_val:.2f})."
        )
        # FIX 2: Apply arabize to the final interpretation string. This is crucial.
        interpretation = arabize(interpretation_raw)
    else: # English
        interpretation = (
            f"Analyzing the categorical variable '{cat_col}': \n"
            f"1. In terms of frequency: The most common group is '{most_freq_group}' (Count={most_freq_count}), "
            f"while the least common group is '{least_freq_group}' (Count={least_freq_count}). \n"
            f"2. For the dependent variable '{y_col}': The group '{highest_y_group}' recorded the highest average "
            f"({highest_y_val:.2f}), while the group '{lowest_y_group}' recorded the lowest average ({lowest_y_val:.2f})."
        )

    return summary_df, plot_buffer, interpretation


# ----------------- PDF GENERATION: BiDi Fixes Applied Here -----------------

def generate_report(df, y_feature, lang='ar'):
    """
    Generates a PDF report in a specified language.
    lang: 'ar' for Arabic, 'en' for English.
    """
    
    # 1. Configuration based on language
    if lang == 'ar':
        if not ARABIC_FONT_AVAILABLE:
             print("Skipping Arabic PDF generation as Arabic font file is missing.")
             return
        
        pdf_filename = "تقرير_تحليل_بيانات_ARABIC.pdf"
        report_title = "تقرير تحليل بيانات شامل" # Raw Arabic text
        y_feature_label = f"المتغير التابع (Y): {y_feature}"
        sec1_title = "القسم 1: تحليل المتغيرات الرقمية"
        sec2_title = "القسم 2: تحليل المتغيرات التصنيفية (الفئات)"
        # Use lambda to create the string, but do NOT arabize here.
        # We will arabize right before adding to the story.
        get_header_func = lambda x_col, idx: f"{idx}. العلاقة مع {x_col}"
        get_cat_header_func = lambda x_col, idx: f"{idx}. تأثير {x_col}"
        
        # ReportLab Styles
        font_name = AR_FONT_NAME
        styles = getSampleStyleSheet()
        # Alignment=4 means Right Alignment
        styles.add(ParagraphStyle(name='TitleStyle', parent=styles['Title'], fontName=font_name, fontSize=20, leading=26, alignment=1))
        styles.add(ParagraphStyle(name='H1Style', parent=styles['Heading1'], fontName=font_name, fontSize=16, leading=20, alignment=4))
        styles.add(ParagraphStyle(name='H2Style', parent=styles['Heading2'], fontName=font_name, fontSize=14, leading=18, alignment=4))
        styles.add(ParagraphStyle(name='NormalStyle', parent=styles['Normal'], fontName=font_name, fontSize=11, leading=14, alignment=4))
        
    else: # English
        pdf_filename = "Data_Analysis_Report_ENGLISH.pdf"
        report_title = "Comprehensive Data Analysis Report"
        y_feature_label = f"Dependent Variable (Y): {y_feature}"
        sec1_title = "Section 1: Numerical Variable Analysis"
        sec2_title = "Section 2: Categorical Variable Analysis"
        get_header_func = lambda x_col, idx: f"{idx}. Relationship with {x_col}"
        get_cat_header_func = lambda x_col, idx: f"{idx}. Effect of {x_col}"
        
        # ReportLab Styles
        font_name = EN_FONT_NAME
        styles = getSampleStyleSheet()
        # Default Left Alignment
        styles.add(ParagraphStyle(name='TitleStyle', parent=styles['Title'], fontName=font_name, fontSize=20, leading=26, alignment=1))
        styles.add(ParagraphStyle(name='H1Style', parent=styles['Heading1'], fontName=font_name, fontSize=16, leading=20))
        styles.add(ParagraphStyle(name='H2Style', parent=styles['Heading2'], fontName=font_name, fontSize=14, leading=18))
        styles.add(ParagraphStyle(name='NormalStyle', parent=styles['Normal'], fontName=font_name, fontSize=11, leading=14))

    print(f"\n--- Starting Analysis and PDF creation for: {lang.upper()} ---")

    # 2. Identify Column Types (omitted filter logic for brevity, it's correct)
    all_numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    all_cat_cols = [col for col in df.columns if df[col].dtype == 'object' or pd.api.types.is_categorical_dtype(df[col])]
    
    x_numeric = [col for col in all_numeric_cols if col != y_feature and col.lower() not in ["id", "observationid", "rowid", "index"] and df[col].std() >= 1e-6]
    x_categorical = [col for col in all_cat_cols if col != y_feature and 2 <= df[col].nunique() <= 20]

    # 3. Build Story
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    story = []

    # FIX 3: Apply arabize to main titles (only for Arabic)
    story.append(Paragraph(arabize(report_title) if lang == 'ar' else report_title, styles['TitleStyle']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(arabize(y_feature_label) if lang == 'ar' else y_feature_label, styles['H1Style']))
    story.append(Spacer(1, 24))

    # --- SECTION 1: NUMERICAL ANALYSIS ---
    if x_numeric:
        # FIX 4: Apply arabize to section headers
        story.append(Paragraph(arabize(sec1_title) if lang == 'ar' else sec1_title, styles['H1Style']))
        story.append(Spacer(1, 12))

        for idx, x_col in enumerate(x_numeric):
            print(f"Numerical Analysis: {x_col} vs {y_feature}")
            try:
                r_val, p_val, plt_buf, interp = perform_analysis(df, x_col, y_feature, lang)

                # FIX 5: Apply arabize to the generated header text
                header_text = get_header_func(x_col, idx+1)
                story.append(Paragraph(arabize(header_text) if lang == 'ar' else header_text, styles['H2Style']))
                
                # The 'interp' variable holds the BiDi-processed Arabic string 
                # (or the standard English string), so we use it directly.
                story.append(Paragraph(interp, styles['NormalStyle']))
                story.append(Spacer(1, 6))

                # Plot
                story.append(Image(plt_buf, width=400, height=250))
                story.append(Spacer(1, 12))
                
            except Exception as e:
                print(f"Error analyzing {x_col}: {e}")

    # --- SECTION 2: CATEGORICAL ANALYSIS ---
    if x_categorical:
        # FIX 6: Apply arabize to section headers
        story.append(Paragraph(arabize(sec2_title) if lang == 'ar' else sec2_title, styles['H1Style']))
        story.append(Spacer(1, 12))
        
        for idx, cat_col in enumerate(x_categorical):
            print(f"Categorical Analysis: {cat_col} vs {y_feature}")
            try:
                summary_df, plt_buf, interp = perform_categorical_analysis(df, cat_col, y_feature, lang)
                
                if summary_df is None: continue

                # FIX 7: Apply arabize to the generated header text
                header_text = get_cat_header_func(cat_col, idx+1)
                story.append(Paragraph(arabize(header_text) if lang == 'ar' else header_text, styles['H2Style']))
                
                # The 'interp' variable holds the BiDi-processed Arabic string
                story.append(Paragraph(interp, styles['NormalStyle']))
                story.append(Spacer(1, 8))

                # Table
                table_header = summary_df.columns.tolist()
                # If Arabic, apply arabize to the column headers for the table
                if lang == 'ar':
                    # Note: ReportLab handles Table cell text differently from Paragraphs, 
                    # so we apply arabize here.
                    table_header = [arabize(c) for c in table_header]
                
                table_body = summary_df.round(2).astype(str).values.tolist()
                table_data = [table_header] + table_body

                t = Table(table_data, hAlign='CENTER')
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), font_name),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ]))
                story.append(t)
                story.append(Spacer(1, 12))

                # Plot
                story.append(Image(plt_buf, width=400, height=250))
                story.append(Spacer(1, 24))

            except Exception as e:
                print(f"Error analyzing categorical {cat_col}: {e}")
                # import traceback; traceback.print_exc()

    # 4. Build PDF
    doc.build(story)
    print(f"\nReport successfully created and saved: {pdf_filename}")


# ----------------- MAIN EXECUTION BLOCK (No changes needed here) -----------------
if __name__ == "__main__":
    CONFIG_FILE_NAME = "config.json"
    
    # 1. Load Config
    if os.path.exists(CONFIG_FILE_NAME):
        with open(CONFIG_FILE_NAME, 'r', encoding='utf-8') as f:
            config = json.load(f)
        CSV_FILE_NAME = config.get("csv_file_name", "data.csv")
        Y_FEATURE_COLUMN = config.get("y_feature_column", "Score")
    else:
        CSV_FILE_NAME = "data_with_categories.csv"
        Y_FEATURE_COLUMN = "SatisfactionScore"
        print(f"Config file not found. Using default: {CSV_FILE_NAME}")

    # 2. Create Dummy Data (your existing logic)
    if not os.path.exists(CSV_FILE_NAME):
        print(f"Data file '{CSV_FILE_NAME}' not found. Generating dummy data...")
        N = 150
        np.random.seed(42)
        load_time = np.random.normal(3.5, 1.0, N).clip(1.5, 6.0)
        gender = np.random.choice(['Male', 'Female'], N, p=[0.4, 0.6])
        sub_type = np.random.choice(['Basic', 'Standard', 'Premium'], N, p=[0.5, 0.3, 0.2])
        base_score = 90 - (load_time * 5)
        
        score = []
        for i in range(N):
            s = base_score[i]
            if sub_type[i] == 'Premium': s += 15
            elif sub_type[i] == 'Standard': s += 5
            if gender[i] == 'Female': s += 2
            s += np.random.normal(0, 5)
            score.append(s)
            
        score = np.clip(score, 0, 100).astype(int)

        df_dummy = pd.DataFrame({
            "ObservationID": range(1, N + 1),
            "LoadTime_s": load_time,
            "Gender": gender,
            "SubscriptionPlan": sub_type,
            "SatisfactionScore": score
        })
        df_dummy.to_csv(CSV_FILE_NAME, index=False)
        print("Dummy data with categorical columns generated.")

    # 3. Load Data and Run for both languages
    try:
        data_df = pd.read_csv(CSV_FILE_NAME)
        if Y_FEATURE_COLUMN not in data_df.columns:
            raise ValueError(f"Column {Y_FEATURE_COLUMN} not found in CSV.")
            
            
        # Generate Arabic Report
        generate_report(data_df, Y_FEATURE_COLUMN, lang='ar')

        # Generate English Report
        generate_report(data_df, Y_FEATURE_COLUMN, lang='en')
        
    except Exception as e:
        print(f"A fatal error occurred: {str(e)}")
        import traceback
        traceback.print_exc()