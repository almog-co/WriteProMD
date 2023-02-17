import datetime
import os

class MarkdownToPDF:
    def __init__(self, markdown, pdf, default_font='Helvetica', default_font_size=12):
        self.markdown = markdown
        self.pdf = pdf
        self.font = default_font
        self.font_size = default_font_size
        self.parse()
    
    def parse_block(self, lines, end_symbol, join_symbol):
        block = []
        while (len(lines) > 0):
            line = lines.pop(0)
            if line.startswith(end_symbol):
                break
            block.append(line)
        return join_symbol.join(block)

    def parse_table(self, table):
        # headers
        headers = [x.strip() for x in table[0].split('|')]
        headers = headers[1:-1]

        # row
        data = []
        for line in table[2:]:
            data.append([x.strip() for x in line.split('|')][1:-1])
        #print(data)

        # set up table
        
        line_height = self.font_size * 0.8
        col_width = self.pdf.epw / len(headers)
        #self.pdf.ln(line_height)
        #self.pdf.set_left_margin(self.pdf.l_margin + col_width * len(headers))
        for i, header in enumerate(headers):
            self.pdf.multi_cell(col_width, line_height, header, border=1,
            new_x="RIGHT", new_y="TOP", max_line_height=self.font_size, markdown=True)
        self.pdf.ln(line_height)
        for row in data:
            for datum in row:
                self.pdf.multi_cell(col_width, line_height, datum, border=1,
                new_x="RIGHT", new_y="TOP", max_line_height=self.font_size)
            self.pdf.ln(line_height)
        #self.pdf.ln(5)
        #self.pdf.set_left_margin(self.pdf.l_margin - col_width * len(headers))

    
    def parse(self):
        lines = self.markdown.splitlines()

        while (len(lines) > 0):
            line = lines.pop(0).strip()
            if line.startswith('#'):
                self.parse_heading(line)
            elif line.startswith('```'):
                codeblock = self.parse_block(lines, '```', '\n')
                self.parse_codeblock(codeblock)
            elif line.startswith('@'):
                self.parse_command(line)
            elif line.startswith('$$') and line.endswith('$$'):
                latex = line[2:-2]
                img = latex_to_image(latex)
                self.pdf.ln(5)
                self.pdf.image(img, x=100, w=10)
                self.pdf.ln(5)
            elif line.startswith('| '):
                table = [line]
                while(len(lines) > 0):
                    line = lines.pop(0)
                    if line.startswith('| '):
                        table.append(line)
                    else:
                        lines.insert(0, line)
                        break
                self.parse_table(table)
            # Add line break if number of empty lines is greater than 1
            elif line.strip() == '':
                newlines = 1
                while (len(lines) > 0):
                    line = lines[0].strip()
                    if line.strip() != '':
                        break
                    newlines += 1
                    lines.pop(0)
                if newlines > 1:
                    for i in range(newlines - 1):
                        self.pdf.ln(5)

            else:
                self.parse_paragraph(line)
    
    def parse_heading(self, line):
        if line.startswith('#'):
            if line.startswith('###'):
                self.pdf.set_font(self.font, 'B', self.font_size)
                self.pdf.cell(0, 10, txt=line[3:].strip(), ln=1)
            elif line.startswith('##'):
                self.pdf.set_font(self.font, 'B', self.font_size + 2)
                self.pdf.cell(0, 10, txt=line[2:].strip(), ln=1)
            elif line.startswith('#'):
                # Draw text
                self.pdf.set_font(self.font, 'B', self.font_size + 8)
                self.pdf.cell(0, 10, txt=line[1:].strip(), ln=1)

                # Draw underline across page
                self.pdf.set_line_width(0.3)
                self.pdf.set_draw_color(r=0, g=0, b=0)
                self.pdf.line(x1=10, y1=self.pdf.get_y() + 1, x2=205, y2=self.pdf.get_y() + 1)
                
                # Add line break
                self.pdf.ln(5)
            
            
            # Reset font
            self.pdf.set_font(self.font, size=self.font_size)

    def replace_nearest_symbol(self, line, index, old, new):
        left_index = line[:index].rfind(old)
        right_index = line[index:].find(old)
        if left_index != -1 and (right_index == -1 or index - left_index <= right_index):
            return line[:left_index] + new + line[left_index + len(old):index + right_index]
        elif right_index != -1:
            return line[:index + right_index] + new + line[index + right_index + len(old):]
        else:
            return line

    def replace_paragraph_symbols_html(self, line, symbol, html):
        while symbol in line:
            line = self.replace_nearest_symbol(line, 0, symbol, f'<{html}>')
            line = self.replace_nearest_symbol(line, 0, symbol, f'</{html}>')
        return line
    
    def parse_paragraph(self, line):
        self.pdf.set_font(self.font, size=self.font_size)
        
        # Text
        # line = self.replace_paragraph_symbols_html(line, '**', 'b')
        # line = self.replace_paragraph_symbols_html(line, '__', 'u')
        # line = self.replace_paragraph_symbols_html(line, '*', 'i')
        
        # In-line commands
        line, alignment = self.parse_inline_command(line)

        # Links
        line = self.parse_links(line)

        # Empty line
        if (line.strip() == ''):
            return

        # Ignore lines
        if '@header' in line or '@footer' in line:
            line = None

        # New line
        if line is not None:
            self.pdf.multi_cell(0, self.font_size * 0.5, txt=line, align=alignment, ln=1, markdown=True)
                    

    def parse_codeblock(self, lines):
        self.pdf.set_font('Courier', size=self.font_size)
        for line in lines.split('\n'):
            self.pdf.cell(0, 5, txt=line, ln=1)
        self.pdf.set_font(self.font, size=self.font_size)

    
    def parse_command_args(self, line):
        args = {}
        # Format is @command -arg1=value1 -arg2=value2
        for arg in line.split(' ')[1:]:
            args[arg.split('=')[0].strip('-')] = arg.split('=')[1].strip('-')
        return args

    def parse_command(self, line):
        if line.startswith('@'):
            if line.startswith('@newpage'):
                self.pdf.add_page()
            elif line.startswith('@image'):
                width, height, file = 0, 0, None
                if '-' in line:
                    args = self.parse_command_args(line)
                    if 'width' in args:
                        width = int(args['width'])
                    if 'height' in args:
                        height = int(args['height'])
                    if 'file' in args:
                        file = args['file']
                        if not os.path.exists(file):
                            print(f'File {file} does not exist')
                            return

                if file:
                    self.pdf.image(file, w=width, h=height)
            elif line.startswith('@size'):
                font_size = None
                try:
                    font_size = int(line.split(' ')[1].strip())
                    if (not font_size or font_size < 4 or font_size > 72):
                        raise ValueError
                except:
                    print('Invalid use of @size. Use @size <font size>')
                    return
                
                self.font_size = font_size
                self.pdf.set_font(self.font, size=font_size)
            elif line.startswith('@font'):
                font = None
                try:
                    font = line.split(' ')[1].strip()
                    if (not font):
                        raise ValueError(f'Invalid use of @font. Use @font <font name>')
                    if (font not in self.pdf.defined_fonts):
                        raise ValueError(f'Font {font} does not exist')
                except ValueError as e:
                    print(e)
                    return
                except:
                    print('Invalid use of @font. Use @font <font name>')
                    return
                
                self.font = font
                self.pdf.set_font(font, size=self.font_size)
            else:
                self.parse_paragraph(line)
    
    def parse_inline_command(self, line):
        while '@' in line:
            if '@date' in line:
                date = datetime.datetime.now().strftime('%Y-%m-%d')
                line = self.replace_nearest_symbol(line, 0, '@date', date)
                print(line)
            elif '@pagenumber' in line:
                line = self.replace_nearest_symbol(line, 0, '@pagenumber', str(self.pdf.page_no()))
            elif '@header' in line or '@footer' in line:
                break
            elif ('@center' in line or '@right' in line or '@left' in line):
                alignment = 'C'
                if '@right' in line:
                    alignment = 'R'
                elif '@left' in line:
                    alignment = 'L'
                line = self.replace_nearest_symbol(line, 0, '@center ', '')
                line = self.replace_nearest_symbol(line, 0, '@right ', '')
                line = self.replace_nearest_symbol(line, 0, '@left ', '')
                return line, alignment
            else:
                print(f'Unknown inline command in line: {line}')
                break
        
        return line, 'L'

    def parse_links(self, line):
        while '[' in line:
            left_index = line.find('[')
            right_index = line.find(']')
            if right_index == -1:
                print(f'Error parsing link in line: {line}')
                break
            link = line[left_index + 1:right_index]
            link_text = link
            if '|' in link:
                link_text = link.split('|')[0]
                link = link.split('|')[1]
            line = line[:left_index] + f'<a href="{link}">{link_text}</a>' + line[right_index + 1:]
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