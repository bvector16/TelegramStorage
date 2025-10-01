import pdfplumber


def extract_table_from_blank(pdf_path):
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                tables.extend(page_tables)
        fields = [
                    "name",
                    "inn_name_customer",
                    "adress",
                    "type",
                    "inn_name_gen_contr",
                    "inn_name_subcontr",
                    "inn_name_buyer",
                    "inn_name_designer",
                    "purchase_type",
                    "blank_num",
                    "reg_date",
                    "manager",
                    "phone",
                    "email",
                ]
        fields_dict = {}
        counter = 0
        for table in tables:
            for row in table:
                try:
                    fields_dict[fields[counter]] = next(
                        iter(el for i, el in enumerate(row) if i != 0 and el)
                    )
                except:
                    fields_dict[fields[counter]] = "-"
                counter += 1
        return fields_dict
