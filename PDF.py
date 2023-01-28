from fpdf import FPDF

class PDF(FPDF):
    def __init__(self, headers, footers):
        self.headers = headers
        self.footers = footers
        super().__init__()

    def header(self):
        self.set_font("helvetica", "", 12, )
        self.set_text_color(128)
        aligns = ["L", "C", "R"]
        if (len(self.headers) > 0):
            for i, header in enumerate(self.headers):
                if (i > 2):
                    break
                self.cell(0, 10, header, align=aligns[i])
                self.set_x(self.l_margin)
            self.ln(15)

    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", "I", 8)
        # Printing page number:
        self.cell(0, 10, f"Page {self.page_no()} / {{nb}}", align="C")