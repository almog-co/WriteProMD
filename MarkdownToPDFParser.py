import datetime

class MarkdownToPDF:
    def __init__(self, markdown, pdf, default_font='Helvetica', default_font_size=12):
        self.markdown = markdown
        self.pdf = pdf
        self.default_font = 'Helvetica'
        self.default_font_size = 12
        self.parse()
    
    def parse_block(self, lines, end_symbol, join_symbol):
        block = []
        while (len(lines) > 0):
            line = lines.pop(0)
            if line.startswith(end_symbol):
                break
            block.append(line)
        return join_symbol.join(block)
    
    def parse(self):
        lines = self.markdown.splitlines()

        while (len(lines) > 0):
            line = lines.pop(0).strip()
            if line.startswith('#'):
                self.parse_heading(line)
            elif line.startswith('```'):
                codeblock = self.parse_block(lines, '```', '<br />')
                self.parse_codeblock(codeblock)
            elif line.startswith('@'):
                self.parse_command(line)
            elif line.startswith('$$') and line.endswith('$$'):
                latex = line[2:-2]
                img = latex_to_image(latex)
                self.pdf.ln(5)
                self.pdf.image(img, x=100)
                self.pdf.ln(5)
            else:
                self.parse_paragraph(line)
    
    def parse_heading(self, line):
        if line.startswith('#'):
            if line.startswith('###'):
                self.pdf.set_font(self.default_font, 'B', self.default_font_size)
                self.pdf.cell(0, 10, txt=line[3:].strip(), ln=1)
            elif line.startswith('##'):
                self.pdf.set_font(self.default_font, 'B', self.default_font_size + 2)
                self.pdf.cell(0, 10, txt=line[2:].strip(), ln=1)
            elif line.startswith('#'):
                # Draw text
                self.pdf.set_font(self.default_font, 'B', self.default_font_size + 8)
                self.pdf.cell(0, 10, txt=line[1:].strip(), ln=1)

                # Draw underline across page
                self.pdf.set_line_width(0.5)
                self.pdf.set_draw_color(r=0, g=0, b=0)
                self.pdf.line(x1=10, y1=self.pdf.get_y() + 2, x2=200, y2=self.pdf.get_y() + 2)
                
                # Add line break
                self.pdf.ln(5)
            
            
            # Reset font
            self.pdf.set_font(self.default_font, size=self.default_font_size)

    def replace_nearest_symbol(self, line, index, old, new):
        left_index = line[:index].rfind(old)
        right_index = line[index:].find(old)
        if left_index != -1 and (right_index == -1 or index - left_index <= right_index):
            return line[:left_index] + new + line[left_index + len(old):index + right_index]
        elif right_index != -1:
            return line[:index + right_index] + new + line[index + right_index + len(old):]
        else:
            return line

    def replace_paragraph_symbols(self, line, symbol, html):
        while symbol in line:
            line = self.replace_nearest_symbol(line, 0, symbol, f'<{html}>')
            line = self.replace_nearest_symbol(line, 0, symbol, f'</{html}>')
        return line
    
    def parse_paragraph(self, line):
        self.pdf.set_font(self.default_font, size=self.default_font_size)
        
        # Text
        line = self.replace_paragraph_symbols(line, '**', 'b')
        line = self.replace_paragraph_symbols(line, '__', 'u')
        line = self.replace_paragraph_symbols(line, '*', 'i')
        
        # In-line commands
        line = self.parse_inline_command(line)

        self.pdf.write_html(line)

    def parse_codeblock(self, lines):
        self.pdf.set_font('Courier', size=self.default_font_size)
        self.pdf.write_html(
            f'<blockquote>{lines}</blockquote>'
        )
    
    def parse_command_args(self, line):
        args = {}
        # Format is @command-arg1=value1-arg2=value2
        for arg in line.split('-')[1:]:
            args[arg.split('=')[0].strip()] = arg.split('=')[1].strip()
        return args

    def parse_command(self, line):
        if line.startswith('@'):
            if line.startswith('@newpage'):
                self.pdf.add_page()
            if line.startswith('@image'):
                width, height, file = 0, 0, None
                if '-' in line:
                    args = self.parse_command_args(line)
                    if 'width' in args:
                        width = int(args['width'])
                    if 'height' in args:
                        height = int(args['height'])
                    if 'file' in args:
                        file = args['file']

                if file:
                    self.pdf.image(file, w=width, h=height)
    
    def parse_inline_command(self, line):
        while '@' in line:
            if '@date' in line:
                date = datetime.datetime.now().strftime('%Y-%m-%d')
                line = self.replace_nearest_symbol(line, 0, '@date', date)
        
        return line

# def latex_to_image(latex):
#     from matplotlib.figure import Figure
#     from io import BytesIO

#     fig = Figure(figsize=(6, 4), facecolor="red")
#     gca = fig.gca()
#     gca.text(0, 0.5, r"$%s$" % latex, fontsize=20)
#     gca.axis("off")

#     img = BytesIO()
#     fig.savefig(img, format="svg")
    
#     # Save to file
#     fig.savefig('test.svg', format="svg")
    
#     return img

def latex_to_image(latex):
    # Code from https://stackoverflow.com/questions/14110709/creating-images-of-mathematical-expressions-from-tex-using-matplotlib
    from io import BytesIO
    import pylab
    
    img = BytesIO()
    img2 = BytesIO()
    formula = r'$%s$' % latex

    fig = pylab.figure(facecolor='white')
    text = fig.text(0, 0, formula)

    # Saving the figure will render the text.
    dpi = 300
    fig.savefig(img, dpi=dpi)

    # Now we can work with text's bounding box.
    bbox = text.get_window_extent()
    width, height = bbox.size / float(dpi) + 0.005
    # Adjust the figure size so it can hold the entire text.
    fig.set_size_inches((width, height))

    # Adjust text's vertical position.
    dy = (bbox.ymin/float(dpi))/height
    text.set_position((0, -dy))

    # Save the adjusted text.
    fig.savefig(img2, dpi=dpi)
    img2.seek(0)

    return img2