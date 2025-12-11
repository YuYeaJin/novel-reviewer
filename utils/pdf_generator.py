''' 분석 결과를 받아 PDF로 출력하는 파일
    제목, 섹션, 점수, 요약 결과 등 형식화'''

from fpdf import FPDF

def generate_pdf(report: dict, output_path: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "Novel Review Report", ln=True)

    for section, content in report.items():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"[{section}]", ln=True)

        pdf.set_font("Arial", size=12)
        if isinstance(content, dict) or isinstance(content, list):
            pdf.multi_cell(0, 8, str(content))
        else:
            pdf.multi_cell(0, 8, content)

        pdf.ln(5)

    pdf.output(output_path)
