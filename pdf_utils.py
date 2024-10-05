import PyPDF2
from datetime import datetime
import os

def parse_pdf_date(pdf_date):
    pdf_date = pdf_date[2:] if pdf_date.startswith("D:") else pdf_date
    try:
        parsed_date = datetime.strptime(pdf_date[:14], "%Y%m%d%H%M%S")
        return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return "Неверный формат даты"

def compare_pdf_data(bank, file_data):
    standards = {
        'Сбербанк': {
            'version': '1.3',
            'creator': 'JasperReports Library version 6.5.1',
            'producer': '2.1.7 by 1T3XT'
        },
        'Т-Банк': {
            'version': '1.5',
            'creator': 'JasperReports Library version 6.20.3',
            'producer': 'OpenPDF 1.3.30.jaspersoft.2'
        }
    }

    standard = standards.get(bank)
    if not standard:
        return f"Неизвестный банк: {bank}"

    discrepancies = []
    if file_data['version'] != standard['version']:
        discrepancies.append(f"Версия PDF отличается: {file_data['version']} (должна быть {standard['version']})")

    trimmed_creator = file_data['creator'].split('-')[0].strip()
    if trimmed_creator != standard['creator']:
        discrepancies.append(f"Создатель отличается: {trimmed_creator} (должен быть {standard['creator']})")

    trimmed_producer = ' '.join(file_data['producer'].split(' ')[-3:])
    if trimmed_producer != standard['producer']:
        discrepancies.append(f"Производитель отличается: {trimmed_producer} (должен быть {standard['producer']})")

    if file_data['creation_date'] == 'Нет данных':
        discrepancies.append(f"Отсутствует дата создания")

    if discrepancies:
        output = (
                f"Обнаружены расхождения:\n"
                f"1) Вес файла: {file_data['size_kb']} кБ\n"
                f"2) Версия PDF: {file_data['version']}\n"
                f"3) Создатель: {file_data['creator']}\n"
                f"4) Производитель: {file_data['producer']}\n"
                f"5) Дата создания: {file_data['creation_date']}\n"
                + "\n".join(discrepancies)
        )
        return output
    else:
        return "Все данные соответствуют эталону."

def get_pdf_data(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        file_size = os.path.getsize(file_path) / 1024  # Размер файла в КБ
        pdf_version = reader.pdf_header[5:]  # Получаем версию (например, '1.5')
        metadata = reader.metadata

        creator = metadata.get("/Creator", "Нет данных")
        producer = metadata.get("/Producer", "Нет данных")
        creation_date = metadata.get("/CreationDate", "Нет данных")
        readable_creation_date = parse_pdf_date(creation_date) if creation_date != "Нет данных" else "Нет данных"

        return {
            'size_kb': file_size,
            'version': pdf_version,
            'creator': creator,
            'producer': producer,
            'creation_date': readable_creation_date
        }