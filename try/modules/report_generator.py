from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.shared import RGBColor
import os
import configparser
import base64
from io import BytesIO
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.template_path = self.config['DEFAULT'].get('template_path', './templates')
        self.report_save_path = self.config['DEFAULT'].get('report_save_path', './reports')
        
        if not os.path.exists(self.report_save_path):
            os.makedirs(self.report_save_path)
    
    def create_report(self, task_info):
        try:
            doc = Document()
            
            section = doc.sections[0]
            section.left_margin = Cm(2.54)
            section.right_margin = Cm(2.54)
            section.top_margin = Cm(2.54)
            section.bottom_margin = Cm(2.54)
            
            title = doc.add_heading('实验报告', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_paragraph()
            
            info_table = doc.add_table(rows=4, cols=2)
            info_table.style = 'Table Grid'
            info_table.autofit = True
            
            info_cells = [
                ('课程名称', '网络安全实践'),
                ('实验项目', task_info.get('title', '未知任务')),
                ('姓名', ''),
                ('日期', datetime.now().strftime('%Y年%m月%d日'))
            ]
            
            for i, (label, value) in enumerate(info_cells):
                info_table.cell(i, 0).text = label
                info_table.cell(i, 1).text = value
                info_table.cell(i, 0).vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                info_table.cell(i, 1).vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            
            doc.add_paragraph()
            
            doc.add_heading('一、实验目的', level=1)
            purpose = doc.add_paragraph()
            purpose.add_run("1. ").bold = True
            purpose.add_run("理解并掌握")
            purpose.add_run(task_info.get('title', '相关')).bold = True
            purpose.add_run("的基本原理和操作方法。")
            
            doc.add_paragraph()
            
            doc.add_heading('二、实验环境', level=1)
            env_table = doc.add_table(rows=3, cols=2)
            env_table.style = 'Table Grid'
            env_table.autofit = True
            
            env_cells = [
                ('操作系统', 'Windows 10 / Linux'),
                ('虚拟机软件', 'VMware Workstation / VirtualBox'),
                ('实验工具', '根据任务要求')
            ]
            
            for i, (label, value) in enumerate(env_cells):
                env_table.cell(i, 0).text = label
                env_table.cell(i, 1).text = value
                env_table.cell(i, 0).vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                env_table.cell(i, 1).vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            
            doc.add_paragraph()
            
            doc.add_heading('三、实验步骤与详细参考', level=1)
            steps = doc.add_paragraph()
            steps.add_run("根据任务说明，按照以下步骤完成实验：\n")
            
            if task_info.get('description'):
                steps.add_run("详细参考说明：").bold = True
                steps.add_run("\n")
                steps.add_run(task_info['description'])
            
            doc.add_paragraph()
            
            doc.add_heading('四、实验过程截图', level=1)
            screenshots = task_info.get('screenshots', [])
            
            if screenshots:
                for idx, screenshot in enumerate(screenshots):
                    step_num = screenshot.get('step', idx + 1)
                    timestamp = screenshot.get('timestamp', '')
                    
                    caption = doc.add_paragraph()
                    caption.add_run(f"步骤 {step_num}（{timestamp}）：").bold = True
                    caption.add_run("执行操作截图")
                    
                    try:
                        image_data = base64.b64decode(screenshot['image'])
                        image_stream = BytesIO(image_data)
                        doc.add_picture(image_stream, width=Inches(6))
                        
                        last_paragraph = doc.paragraphs[-1]
                        last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    except Exception as e:
                        doc.add_paragraph(f"截图 {step_num} 添加失败: {str(e)}")
                    
                    explanation = doc.add_paragraph()
                    explanation.add_run("操作说明：").bold = True
                    explanation.add_run(f"此截图记录了实验步骤 {step_num} 的操作状态，根据详细参考说明，此步骤主要完成")
                    if task_info.get('description'):
                        desc_snippet = task_info['description'][:100] if len(task_info['description']) > 100 else task_info['description']
                        explanation.add_run(f"「{desc_snippet}...」")
                    else:
                        explanation.add_run("相关操作。")
                    
                    doc.add_paragraph()
            else:
                doc.add_paragraph("本次实验未记录截图。")
            
            doc.add_paragraph()
            
            doc.add_heading('五、实验结果', level=1)
            result = doc.add_paragraph()
            result.add_run("1. ").bold = True
            result.add_run("实验过程：")
            result.add_run("\n   - 按照任务要求完成了相应操作")
            result.add_run("\n   - 记录了实验过程中的关键步骤和现象")
            result.add_run(f"\n   - 共截取 {len(screenshots)} 张操作截图")
            result.add_run("\n\n2. ").bold = True
            result.add_run("实验数据：")
            result.add_run("\n   - 填写实验过程中获取的数据和截图说明")
            
            doc.add_paragraph()
            
            doc.add_heading('六、实验总结', level=1)
            summary = doc.add_paragraph()
            summary.add_run("通过本次实验，深入理解了")
            summary.add_run(task_info.get('title', '实验内容')).bold = True
            summary.add_run("的相关知识和操作技能。")
            if task_info.get('description'):
                summary.add_run("\n根据详细参考说明，本次实验主要完成了：")
                summary.add_run(task_info['description'][:150] if len(task_info['description']) > 150 else task_info['description'])
            
            doc.add_paragraph()
            
            save_name = f"实验报告_{task_info.get('title', '未知任务').replace('/', '_').replace('\\', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            save_path = os.path.join(self.report_save_path, save_name)
            
            doc.save(save_path)
            print(f"实验报告已生成: {save_path}")
            
            return save_path
        except Exception as e:
            print(f"生成实验报告失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_multiple_reports(self, tasks):
        reports = []
        for task in tasks:
            if task.get('status') != '已完成':
                report_path = self.create_report(task)
                if report_path:
                    reports.append(report_path)
        
        return reports
    
    def get_report_list(self):
        try:
            reports = []
            if os.path.exists(self.report_save_path):
                for file in os.listdir(self.report_save_path):
                    if file.endswith('.docx'):
                        reports.append({
                            'name': file,
                            'path': os.path.join(self.report_save_path, file),
                            'size': os.path.getsize(os.path.join(self.report_save_path, file))
                        })
            
            return sorted(reports, key=lambda x: x['name'], reverse=True)
        except Exception as e:
            print(f"获取报告列表失败: {str(e)}")
            return []