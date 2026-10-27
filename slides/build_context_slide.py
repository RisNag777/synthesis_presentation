"""One context slide: disability and restraint/isolation in WA middle schools."""

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

INK = RGBColor(0x1C, 0x19, 0x17)
MUTED = RGBColor(0x57, 0x53, 0x4E)
FAINT = RGBColor(0xA8, 0xA2, 0x9E)
PAPER = RGBColor(0xF7, 0xF5, 0xF2)
TRACK = RGBColor(0xE7, 0xE5, 0xE4)
SWD = RGBColor(0x1F, 0x4E, 0x5F)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def set_run(run, text, size, color, bold=False):
    run.text = text
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.name = "Calibri"


def add_text(slide, left, top, width, height, text, size, color, bold=False, align=PP_ALIGN.LEFT):
    shape = slide.shapes.add_textbox(left, top, width, height)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    p = tf.paragraphs[0]
    p.alignment = align
    p.space_before = Pt(0)
    p.space_after = Pt(0)
    set_run(p.add_run(), text, size, color, bold)
    return shape


def add_rect(slide, left, top, width, height, fill):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    # Drop the default shadow if the theme adds one.
    sp_pr = shape._element.spPr
    effect = sp_pr.find(qn("a:effectLst"))
    if effect is not None:
        sp_pr.remove(effect)
    return shape


def add_bar(slide, top, label, detail, share, swd_label):
    add_text(slide, Inches(0.7), top, Inches(8.2), Inches(0.32), label, 16, INK, bold=True)
    add_text(
        slide,
        Inches(8.9),
        top,
        Inches(3.7),
        Inches(0.32),
        detail,
        16,
        MUTED,
        align=PP_ALIGN.RIGHT,
    )
    bar_top = top + Inches(0.4)
    bar_left = Inches(0.7)
    bar_width = Inches(11.9)
    bar_height = Inches(0.42)
    add_rect(slide, bar_left, bar_top, bar_width, bar_height, TRACK)
    swd_width = int(bar_width * share)
    if swd_width > 0:
        add_rect(slide, bar_left, bar_top, swd_width, bar_height, SWD)
    # Percent sits just inside the filled portion when it is wide enough,
    # and just to the right of a short fill.
    if share >= 0.25:
        add_text(
            slide,
            bar_left + Inches(0.16),
            bar_top + Inches(0.04),
            Inches(1.4),
            Inches(0.34),
            swd_label,
            14,
            WHITE,
            bold=True,
        )
    else:
        add_text(
            slide,
            bar_left + swd_width + Inches(0.12),
            bar_top + Inches(0.04),
            Inches(1.2),
            Inches(0.34),
            swd_label,
            14,
            SWD,
            bold=True,
        )


def build():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    prs.core_properties.title = "Disability and restraint in Washington middle schools"
    prs.core_properties.subject = "Context slide, OSPI 2023-24"

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, PAPER)

    add_text(
        slide,
        Inches(0.7),
        Inches(0.42),
        Inches(12),
        Inches(0.32),
        "WASHINGTON MIDDLE SCHOOLS   ·   2023–24",
        13,
        MUTED,
        bold=True,
    )
    title = add_text(
        slide,
        Inches(0.7),
        Inches(0.9),
        Inches(12),
        Inches(1.55),
        "Students with disabilities are 15% of enrollment",
        32,
        INK,
        bold=True,
    )
    second = title.text_frame.add_paragraph()
    second.alignment = PP_ALIGN.LEFT
    second.space_before = Pt(0)
    second.space_after = Pt(0)
    set_run(second.add_run(), "and 89% of restraint and isolation incidents.", 32, INK, bold=True)
    title.text_frame.paragraphs[0].line_spacing = 1.0
    second.line_spacing = 1.0

    add_bar(
        slide,
        Inches(2.85),
        "Share of middle school enrollment",
        "32,147 of 218,387 students",
        32147 / 218387,
        "15%",
    )
    add_bar(
        slide,
        Inches(4.25),
        "Share of restraint and isolation incidents",
        "1,176 of 1,325 incidents",
        1176 / 1325,
        "89%",
    )

    add_text(
        slide,
        Inches(0.7),
        Inches(5.85),
        Inches(11.9),
        Inches(0.7),
        "Students without disabilities account for 81 of those incidents. Another 68 are in schools where OSPI suppressed the disability count. The same pattern shows up in 2019–20, when counts of one and two were still published: 97% of middle school restraint incidents and 97% of isolation incidents involved students with disabilities.",
        15,
        MUTED,
    )
    add_text(
        slide,
        Inches(0.7),
        Inches(6.85),
        Inches(11.9),
        Inches(0.4),
        "Source: OSPI restraint and isolation files, schools with “middle” in the name. “Students with disabilities” is the IDEA category, broader than an emotional or behavioral label. Counts under 3 incidents are suppressed in 2023–24.",
        12,
        FAINT,
    )

    notes = slide.notes_slide.notes_text_frame
    notes.text = (
        "Context slide for restraint and isolation, not suspension or expulsion. "
        "Those are not in this dataset. "
        "2023–24 middle schools: 347 schools whose names contain middle and do not also say high school. "
        "Enrollment is the sum of school enrollments: 218,387 for all students, 32,147 for students with disabilities (14.7%). "
        "Published incidents: 1,325 all students, 1,176 students with disabilities (88.8%), 81 students without disabilities. "
        "The remaining 68 incidents are in all-students rows whose disability breakdown is suppressed. "
        "OSPI suppresses 2023–24 cells under 3 incidents, under 3 students, or under 10 enrolled, plus some cross-group cells. "
        "2019–20 school sheets, middle schools with any incidents: restraint incidents 751 of 770 (97.5%) were students with disabilities; "
        "isolation incidents 490 of 507 (96.6%). "
        "Do not describe this as emotional/behavioral disability only."
    )
    return prs


if __name__ == "__main__":
    out = r"C:\Users\risha\Documents\Projects\synthesis_presentation\slides\middle-school-disability-context.pptx"
    build().save(out)
    print(out)
