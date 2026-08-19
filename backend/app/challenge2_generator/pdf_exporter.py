import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.core.logger import logger
from app.core.config import settings


class PDFExporter:
    """
    Export generated questions as formatted PDF.
    Creates professional exam paper layout.
    """

    def _get_output_path(self, batch_id: str) -> str:
        """Get output file path for PDF."""
        output_dir = Path(settings.UPLOAD_DIR) / "exports"
        output_dir.mkdir(parents=True, exist_ok=True)
        return str(output_dir / f"paper_{batch_id}.pdf")

    def export_with_reportlab(
        self,
        questions: List[Dict[str, Any]],
        title: str,
        institution: Optional[str],
        include_answers: bool,
        batch_id: str,
        subject: str,
        total_marks: int
    ) -> str:
        """
        Export questions to PDF using ReportLab.
        Returns file path of created PDF.
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, cm
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph,
                Spacer, Table, TableStyle,
                HRFlowable
            )

            output_path = self._get_output_path(batch_id)

            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=16,
                textColor=colors.HexColor('#2563EB'),
                spaceAfter=6
            )

            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#4B5563'),
                spaceAfter=12
            )

            question_style = ParagraphStyle(
                'QuestionStyle',
                parent=styles['Normal'],
                fontSize=11,
                leading=16,
                spaceAfter=8,
                spaceBefore=8
            )

            answer_style = ParagraphStyle(
                'AnswerStyle',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#059669'),
                leftIndent=20,
                spaceAfter=6
            )

            # Build content
            story = []

            # Title
            story.append(Paragraph(title, title_style))
            if institution:
                story.append(Paragraph(institution, header_style))

            # Paper info
            story.append(Paragraph(
                f"Subject: {subject} | "
                f"Total Questions: {len(questions)} | "
                f"Total Marks: {total_marks}",
                header_style
            ))
            story.append(HRFlowable(
                width="100%",
                thickness=1,
                color=colors.HexColor('#E5E7EB')
            ))
            story.append(Spacer(1, 0.3*inch))

            # Questions
            for i, q in enumerate(questions, 1):
                # Question number and text
                q_text = (
                    f"<b>Q{i}.</b> "
                    f"{q.get('question_text', '')} "
                    f"<i>[{q.get('marks', 5)} marks]</i>"
                )
                story.append(Paragraph(q_text, question_style))

                # MCQ options
                if (
                    q.get("question_type") == "mcq" and
                    q.get("options")
                ):
                    for j, opt in enumerate(q["options"]):
                        opt_label = chr(65 + j)
                        story.append(Paragraph(
                            f"&nbsp;&nbsp;&nbsp;{opt_label}) {opt}",
                            question_style
                        ))

                # Answer section
                if include_answers and q.get("model_answer"):
                    story.append(Paragraph(
                        f"<b>Answer:</b> {q['model_answer'][:300]}",
                        answer_style
                    ))

                    if q.get("marking_scheme"):
                        story.append(Paragraph(
                            f"<b>Marking:</b> {q['marking_scheme']}",
                            answer_style
                        ))

                story.append(Spacer(1, 0.2*inch))

            # Build PDF
            doc.build(story)
            logger.info(f"PDF exported: {output_path}")
            return output_path

        except ImportError:
            logger.warning(
                "ReportLab not installed. "
                "Falling back to simple text PDF."
            )
            return self._export_simple_text(
                questions, title, batch_id,
                include_answers
            )

    def _export_simple_text(
        self,
        questions: List[Dict[str, Any]],
        title: str,
        batch_id: str,
        include_answers: bool
    ) -> str:
        """Simple text-based export fallback."""
        output_path = self._get_output_path(batch_id).replace(
            '.pdf', '.txt'
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"{title}\n")
            f.write("=" * 60 + "\n\n")

            for i, q in enumerate(questions, 1):
                f.write(
                    f"Q{i}. {q.get('question_text', '')} "
                    f"[{q.get('marks', 5)} marks]\n"
                )

                if q.get("options"):
                    for j, opt in enumerate(q["options"]):
                        f.write(f"   {chr(65+j)}) {opt}\n")

                if include_answers and q.get("model_answer"):
                    f.write(
                        f"Answer: {q['model_answer'][:200]}\n"
                    )

                f.write("\n")

        logger.info(f"Text export created: {output_path}")
        return output_path

    def export(
        self,
        questions: List[Dict[str, Any]],
        title: str = "Question Paper",
        institution: Optional[str] = None,
        include_answers: bool = False,
        batch_id: Optional[str] = None,
        subject: str = "General"
    ) -> str:
        """
        Main export method.
        Returns path to exported file.
        """
        batch_id = batch_id or str(uuid.uuid4())
        total_marks = sum(
            q.get("marks", 5) for q in questions
        )

        return self.export_with_reportlab(
            questions=questions,
            title=title,
            institution=institution,
            include_answers=include_answers,
            batch_id=batch_id,
            subject=subject,
            total_marks=total_marks
        )


# Singleton
pdf_exporter = PDFExporter()
