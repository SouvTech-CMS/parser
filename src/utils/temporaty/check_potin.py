import openpyxl


def save_data_row(*,
                  data: str, f_name: str, count: int = 0):
    """data is id row"""
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.cell(row=count, column=1).value = data

    wb.save(f_name)
