from fpdf import FPDF

from project.schedule import Schedule
from datetime import datetime, timedelta
from project.pair import DaysOfWeek, StudentPairAttrib, SubgroupPairAttrib
from project import defaults

# yellow color: 255, 255, 129
# green color: 129, 255, 129


def export_to_pdf(schedule: Schedule, start_week, end_week):
    pdf = FPDF(orientation="L")
    pdf.add_font('DejaVu', '', './project/pdf_export/DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '')

    start = datetime.strptime(start_week, "%Y.%m.%d")
    end = datetime.strptime(end_week, "%Y.%m.%d")
    delta = timedelta(days=1)

    while True:
        pdf.add_page()
        data = [[{"text": "", "subgroup": None} for j in range(8)] for i in range(6)]

        for i in range(6):
            now = start.strftime("%Y.%m.%d")
            for j in range(8):
                pairs = schedule.pairs_by_index(i, j)
                for pair in pairs:
                    if now in pair.get_value(StudentPairAttrib.Date):
                        data[i][j]["text"] += str(pair) + "\n"
                        data[i][j]["subgroup"] = pair.get_value(StudentPairAttrib.Subgroup)

            start += delta

        x, y = float(pdf.get_x()), float(pdf.get_y())

        pdf.set_auto_page_break(True, margin=y)

        w = float(pdf.w) - 2 * float(pdf.get_x())
        h = float(pdf.h) - 2 * float(pdf.get_y()) - 6

        title = 10

        pdf.set_font_size(14)
        pdf.cell(w, title, txt="ИДБ-17-09. Зеленый цвет - А подгруппа, желтый цвет - Б подгруппа. "
                               "{}-{}".format((start + timedelta(days=-6)).strftime("%d.%m.%Y"),
                                              start.strftime("%d.%m.%Y")),
                 align="C", border=0)
        h -= title

        first_column, first_row = 4, 4

        step_column = (w - first_row) / 8
        step_row = (h - first_column) / 6

        for i in range(7):
            for j in range(9):
                if i == 0 and j == 0:
                    pdf.set_xy(x, y + title)
                    pdf.cell(first_column, first_row, border=1)
                elif i == 0:
                    pdf.set_xy(x + first_row + step_column * (j - 1), y + title)
                    pdf.set_font_size(8)
                    pdf.cell(step_column, first_row, txt=defaults.get_time_start_end(j - 1), align="C", border=1)
                elif j == 0:
                    pdf.set_xy(x, y + title + first_column + step_row * (i - 1) + step_row)
                    pdf.rotate(90)
                    pdf.set_font_size(8)
                    pdf.cell(step_row, first_row, txt=str(DaysOfWeek.value_of(i - 1)), align="C", border=1)
                    pdf.rotate(0)
                else:
                    pdf.set_xy(x + first_row + step_column * (j - 1),
                               y + title + first_column + step_row * (i - 1))

                    if data[i - 1][j - 1]["subgroup"] is not None:
                        if data[i - 1][j - 1]["subgroup"].get_subgroup() == SubgroupPairAttrib.A:
                            pdf.set_fill_color(129, 255, 129)
                            pdf.cell(step_column, step_row, border=1, fill=1)
                        elif data[i - 1][j - 1]["subgroup"].get_subgroup() == SubgroupPairAttrib.B:
                            pdf.set_fill_color(255, 255, 129)
                            pdf.cell(step_column, step_row, border=1, fill=1)
                        else:
                            pdf.cell(step_column, step_row, border=1)
                    else:
                        pdf.cell(step_column, step_row, border=1)

                    if data[i - 1][j - 1]["subgroup"] is not None:
                        size = 7
                        offset = 1
                        while size >= 1:
                            pdf.set_font_size(size)
                            lst = pdf.multi_cell(step_column, step_row,
                                                 txt=data[i - 1][j - 1]["text"], align="L", split_only=True)
                            hf = size / 2.8
                            if len(lst) * hf <= step_row - offset * 2:
                                for k, t in enumerate(lst):

                                    pdf.set_xy(x + first_row + step_column * (j - 1),
                                               y + title + first_column + step_row * (i - 1) + k * hf + offset)

                                    pdf.cell(step_column, hf, txt=t, align="L")
                                break
                            size -= 1

        start += delta

        if end <= start:
            print(start.strftime("%Y.%m.%d"))
            break

        print("work...")

    pdf.output("simple.pdf")
    print("Gone!")
