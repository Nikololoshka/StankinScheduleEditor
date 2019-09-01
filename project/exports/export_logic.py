# coding: utf-8

# imports
from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QColor
from fpdf import FPDF  # PyFPDF2

from project.schedule import Schedule
from project import schedule_editor_window
from project.pair import DaysOfWeek, SubgroupPairAttrib, TimePair

import datetime
import math

FPDF.FPDF_CACHE_MODE = 1  # no cache


def export_weeks_to_pdf(schedule_ref: Schedule, title_text: str, add_date: bool, file_path: str,
                        font_name: str, font_path: str, encoding: str,
                        start: datetime.date, end: datetime.date,
                        color_a: QColor, color_b: QColor, progress=None) -> None:
    """
    Method for exports to PDF file
    """

    file = QFileInfo(file_path)

    # pdf
    pdf = FPDF(orientation="L")

    # encoding
    if encoding == "UTF-8":
        pdf.add_font(font_name, "", font_path, uni=True)
    else:
        pdf.add_font(font_name, "", font_path)
        pdf.set_doc_option("core_fonts_encoding", encoding)

    # processing
    week_step = 100 / (end - start).days / 7
    count = 0

    pdf.set_font(font_name)

    while True:
        pdf.add_page()

        schedule = schedule_ref.create_week_schedule(start,
                                                     start + datetime.timedelta(days=6))

        indexes = schedule.indexes()
        table_widget = schedule_editor_window.ScheduleTableWidget()
        table_widget.set_schedule(schedule)

        start += datetime.timedelta(days=6)

        x, y = float(pdf.get_x()), float(pdf.get_y())
        w = float(pdf.w) - 2 * float(pdf.get_x())
        h = float(pdf.h) - 2 * float(pdf.get_y()) - 6

        pdf.set_auto_page_break(True, margin=y)

        title = 10
        title_page = title_text
        if add_date:
            start_week = (start + datetime.timedelta(days=-6)).strftime("%d.%m.%Y")
            end_week = start.strftime("%d.%m.%Y")
            title_page += f". {start_week} - {end_week}"

        pdf.set_font_size(14)
        pdf.cell(w, title, txt=title_page, align="C", border=0)
        h -= title

        first_column, first_row = 4, 4

        step_column = (w - first_row) / 8
        step_row = (h - first_column) / 6

        i = 0
        while i < 7:
            j = 0
            while j < 9:
                if i == 0 and j == 0:
                    # upper-left cell
                    pdf.set_xy(x, y + title)
                    pdf.cell(first_column,
                             first_row,
                             border=1)
                    j += 1
                elif i == 0:
                    # top cells with time
                    pdf.set_xy(x + first_row + step_column * (j - 1), y + title)
                    pdf.set_font_size(8)
                    pdf.cell(step_column,
                             first_row,
                             txt=TimePair.time_start_end(j - 1),
                             align="C",
                             border=1)
                    j += 1
                elif j == 0:
                    # left cells with days of the week
                    pdf.set_xy(x, y + title + first_column + step_row * (i - 1) + step_row)
                    pdf.rotate(90)
                    pdf.set_font_size(8)
                    pdf.cell(step_row,
                             first_row,
                             txt=str(DaysOfWeek.value_of(i - 1)),
                             align="C",
                             border=1)
                    pdf.rotate(0)
                    j += 1
                else:
                    # cells inside the table
                    pdf.set_xy(x + first_row + step_column * (j - 1),
                               y + title + first_column + step_row * (i - 1))

                    simple_row = (step_row / indexes[i - 1])
                    prev_x, prev_y = pdf.get_x(), pdf.get_y()

                    start_index = sum(indexes[r] for r in range(i - 1))
                    number_row = 0
                    for m in range(start_index, start_index + indexes[i - 1]):
                        item = table_widget.item(m, j - 1)
                        if item is not None:
                            x_span_count = table_widget.columnSpan(m, j - 1)
                            y_span_count = table_widget.rowSpan(m, j - 1)

                            pdf.set_xy(prev_x, prev_y + number_row * simple_row)

                            # pdf.cell(step_column * x_span_count,
                            #          simple_row * y_span_count,
                            #          border=1)

                            day, number, duration = i - 1, j - 1, x_span_count
                            pairs = schedule.pairs_by_index(day, number, duration, number_row)

                            # select color for cell
                            if all(pair["subgroup"].get_subgroup() == SubgroupPairAttrib.Common
                                   for pair in pairs):
                                # common
                                pdf.cell(step_column * x_span_count,
                                         simple_row * y_span_count,
                                         border=1)

                            elif all(pair["subgroup"].get_subgroup() == SubgroupPairAttrib.A
                                     for pair in pairs):
                                # A subgroup
                                pdf.set_fill_color(color_a.red(), color_a.green(), color_a.blue())
                                pdf.cell(step_column * x_span_count,
                                         simple_row * y_span_count,
                                         border=1,
                                         fill=1)
                            elif all(pair["subgroup"].get_subgroup() == SubgroupPairAttrib.B
                                     for pair in pairs):
                                # B subgroup
                                pdf.set_fill_color(color_b.red(), color_b.green(), color_b.blue())
                                pdf.cell(step_column * x_span_count,
                                         simple_row * y_span_count,
                                         border=1,
                                         fill=1)
                            else:
                                # A and B subgroup
                                prev_x = pdf.get_x()
                                prev_y = pdf.get_y()

                                toggle = True

                                row = 5
                                column = math.ceil(step_column * x_span_count / step_row * row)

                                for t in range(column):
                                    for n in range(row):
                                        pdf.set_xy(prev_x + t * step_column * x_span_count / column,
                                                   prev_y + n * step_row / row)

                                        if toggle:
                                            color = color_a
                                            toggle = False
                                        else:
                                            color = color_b
                                            toggle = True

                                        pdf.set_fill_color(color.red(), color.green(), color.blue())
                                        pdf.cell(step_column * x_span_count / column,
                                                 simple_row * y_span_count / row,
                                                 border=0)

                                pdf.set_xy(prev_x, prev_y)
                                pdf.cell(step_column * x_span_count,
                                         simple_row * y_span_count,
                                         border=1)

                            if len(pairs) != 0:
                                text = "\n".join(str(pair) for pair in pairs)
                                draw_text(pdf, x + first_row + step_column * (j - 1),
                                          y + title + first_column + step_row
                                          * (i - 1) + simple_row * number_row,
                                          step_column * x_span_count,
                                          simple_row * y_span_count,
                                          text)
                        number_row += 1
                        pdf.set_xy(prev_x, prev_y)
                    j += 1

                    # old
                    # pairs = schedule.pairs_by_index(i - 1, j - 1, 1) \
                    #     + schedule.pairs_by_index(i - 1, j - 1, 2)
                    #
                    # max_duration = max([1, *[pair["time"].duration() for pair in pairs]])
                    #
                    # # select color for cell
                    # if all(pair["subgroup"].get_subgroup() == SubgroupPairAttrib.Common
                    #        for pair in pairs):
                    #     # common
                    #     pdf.cell(step_column * max_duration,
                    #              step_row,
                    #              border=1)
                    # elif all(pair["subgroup"].get_subgroup() == SubgroupPairAttrib.A
                    #          for pair in pairs):
                    #     # A subgroup
                    #     pdf.set_fill_color(color_a.red(), color_a.green(), color_a.blue())
                    #     pdf.cell(step_column * max_duration,
                    #              step_row,
                    #              border=1,
                    #              fill=1)
                    # elif all(pair["subgroup"].get_subgroup() == SubgroupPairAttrib.B
                    #          for pair in pairs):
                    #     # B subgroup
                    #     pdf.set_fill_color(color_b.red(), color_b.green(), color_b.blue())
                    #     pdf.cell(step_column * max_duration,
                    #              step_row,
                    #              border=1,
                    #              fill=1)
                    # else:
                    #     # A and B subgroup
                    #     prev_x = pdf.get_x()
                    #     prev_y = pdf.get_y()
                    #
                    #     toggle = True
                    #
                    #     row = 5
                    #     column = math.ceil(step_column * max_duration / step_row * row)
                    #
                    #     for m in range(column):
                    #         for n in range(row):
                    #             pdf.set_xy(prev_x + m * step_column * max_duration / column,
                    #                        prev_y + n * step_row / row)
                    #
                    #             if toggle:
                    #                 color = color_a
                    #                 toggle = False
                    #             else:
                    #                 color = color_b
                    #                 toggle = True
                    #
                    #             pdf.set_fill_color(color.red(), color.green(), color.blue())
                    #             pdf.cell(step_column * max_duration / column,
                    #                      step_row / row,
                    #                      border=0,
                    #                      fill=1)
                    #     pdf.set_xy(prev_x, prev_y)
                    #     pdf.cell(step_column * max_duration,
                    #              step_row,
                    #              border=1)
                    # text = ""
                    # for pair in pairs:
                    #     text += str(pair) + "\n"
                    #
                    # if text != "":
                    #     draw_text(pdf,
                    #               x + first_row + step_column * (j - 1),
                    #               y + title + first_column + step_row
                    #               * (i - 1),
                    #               step_column * max_duration,
                    #               step_row,
                    #               text)
                    # j += max_duration
            i += 1

        if progress is not None:
            count += 1
            progress.setValue(week_step * count)
            if progress.wasCanceled():
                break

        start += datetime.timedelta(days=1)
        if end <= start:
            break

    pdf.output(file.absoluteFilePath())


def export_full_to_pdf(schedule_ref: Schedule, title_text: str, file_path: str,
                       font_name: str, font_path: str, encoding: str, progress=None) -> None:
    """
    Method for exports to PDF file
    """
    file = QFileInfo(file_path)

    # pdf
    pdf = FPDF(orientation="L")

    # encoding
    if encoding == "UTF-8":
        pdf.add_font(font_name, "", font_path, uni=True)
    else:
        pdf.add_font(font_name, "", font_path)
        pdf.set_doc_option("core_fonts_encoding", encoding)

    pdf.set_font(font_name)
    pdf.add_page()

    x, y = float(pdf.get_x()), float(pdf.get_y())
    w = float(pdf.w) - 2 * float(pdf.get_x())
    h = float(pdf.h) - 2 * float(pdf.get_y()) - 6

    pdf.set_auto_page_break(True, margin=y)

    title = 10

    pdf.set_font_size(14)
    pdf.cell(w, title, txt=title_text, align="C", border=0)
    h -= title

    first_column, first_row = 4, 4

    step_column = (w - first_row) / 8
    step_row = (h - first_column) / 6

    indexes = schedule_ref.indexes()
    table_widget = schedule_editor_window.ScheduleTableWidget()
    table_widget.set_schedule(schedule_ref)

    # processing
    week_step = 100 / 7
    count = 0

    i = 0
    while i < 7:
        j = 0
        while j < 9:
            if i == 0 and j == 0:
                # upper-left cell
                pdf.set_xy(x, y + title)
                pdf.cell(first_column,
                         first_row,
                         border=1)
                j += 1
            elif i == 0:
                # top cells with time
                pdf.set_xy(x + first_row + step_column * (j - 1), y + title)
                pdf.set_font_size(8)
                pdf.cell(step_column,
                         first_row,
                         txt=TimePair.time_start_end(j - 1),
                         align="C",
                         border=1)
                j += 1
            elif j == 0:
                # left cells with days of the week
                pdf.set_xy(x, y + title + first_column + step_row * (i - 1) + step_row)
                pdf.rotate(90)
                pdf.set_font_size(8)
                pdf.cell(step_row,
                         first_row,
                         txt=str(DaysOfWeek.value_of(i - 1)),
                         align="C",
                         border=1)
                pdf.rotate(0)
                j += 1
            else:
                # cells inside the table
                pdf.set_xy(x + first_row + step_column * (j - 1),
                           y + title + first_column + step_row * (i - 1))

                simple_row = (step_row / indexes[i - 1])
                prev_x, prev_y = pdf.get_x(), pdf.get_y()

                start_index = sum(indexes[r] for r in range(i - 1))
                number_row = 0
                for m in range(start_index, start_index + indexes[i - 1]):
                    item = table_widget.item(m, j - 1)
                    if item is not None:
                        x_span_count = table_widget.columnSpan(m, j - 1)
                        y_span_count = table_widget.rowSpan(m, j - 1)

                        pdf.set_xy(prev_x, prev_y + number_row * simple_row)

                        pdf.cell(step_column * x_span_count,
                                 simple_row * y_span_count,
                                 border=1)

                        text = item.text()
                        if text != "":
                            draw_text(pdf, x + first_row + step_column * (j - 1),
                                      y + title + first_column + step_row
                                      * (i - 1) + simple_row * number_row,
                                      step_column * x_span_count,
                                      simple_row * y_span_count,
                                      text)
                    number_row += 1
                    pdf.set_xy(prev_x, prev_y)
                j += 1
        i += 1

        if progress is not None:
            count += 1
            progress.setValue(week_step * count)
            if progress.wasCanceled():
                break

    pdf.output(file.absoluteFilePath())


def draw_text(pdf, x, y, w, h, text):
    # calculates the font size and draws the text
    size = 7
    offset = 1
    while size >= 1:
        pdf.set_font_size(size)
        # a list with the cells needed to be displayed
        lst = pdf.multi_cell(w, h, txt=text,
                             align="L", split_only=True)
        hf = size / 2.8
        if len(lst) * hf <= h - offset * 2 \
                - offset / 2 * len(lst):
            for k, t in enumerate(lst):
                line_interval = offset / 2 if k > 0 else 0
                pdf.set_xy(x,
                           y + k * hf + offset
                           + line_interval * k)
                pdf.cell(w, hf, txt=t, align="L")
            break
        size -= 0.2
