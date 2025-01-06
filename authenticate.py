# from flask import Flask, request, send_file, render_template, jsonify
# from docx import Document
# import os
# from datetime import datetime, timedelta
# from num2words import num2words
# from docx.shared import Pt
# import logging
# import re
# import inflect
#
# # call inflect
# p = inflect.engine()
#
# # At the top of your script
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
#
# app = Flask(__name__)
#
# # Serve the frontend page
# @app.route("/")
# def index():
#     return render_template("frontend.html")
#
#
# @app.route("/generate", methods=["POST"])
# def generate_lease():
#     try:
#
#         # Collect data from the UI
#         data = request.json
#         tenant_name = data.get("tenant_name").upper()  # Convert to uppercase
#         phone_number = data.get("phone_number")
#         email_address = data.get("email_address")
#         physical_address = data.get("physical_address")
#         date_of_lease_entry = data.get("date_of_lease_entry", None)
#         start_date = data.get("start_date", None)
#         end_date = data.get("end_date", None)
#         lease_duration = data.get("lease_duration")
#         floor_plan = data.get("floor_plan")
#         office_number = data.get("office_number")
#         floor_number = data.get("floor_number").upper()
#         po_box = data.get("po_box")
#         post_code = data.get("post_code")
#         town = data.get("town")
#         parking_capacity = data.get("parking_capacity")
#         escalation_rate = (data.get("escalation_rate"))
#         escalation_type = data.get("type_of_escalation")
#         yearly_rent = int(data.get("yearly_rent", 0))
#         monthly_rent = yearly_rent // 12
#         new_or_renew = data.get("new_or_renew")
#
#         # Convert date to "DD-MM-YYYY"
#         def format_date(date_str):
#             # Check if date_str is None or an empty string
#             if not date_str:
#                 # Use current date as default if no date is provided
#                 return datetime.now().strftime("%d-%m-%Y")
#
#             try:
#                 # Attempt to parse the date
#                 date_obj = datetime.strptime(date_str, "%Y-%m-%d")
#                 return date_obj.strftime("%d-%m-%Y")
#             except ValueError:
#                 # If date format is invalid, use current date
#                 return datetime.now().strftime("%d-%m-%Y")
#         # Use the modified format_date function
#         start_date_formatted = format_date(start_date)
#         end_date_formatted = format_date(end_date)
#         lease_entry_formatted = format_date(date_of_lease_entry)
#
#         # Calculate subsequent years of term
#         def calculate_years_of_term(start_date, end_date, terms=5):
#             """
#             Calculate subsequent years of term with specific logic:
#             1. First year uses the original start and end dates
#             2. Subsequent years start 7 days after the previous year's end date
#             3. Each subsequent year ends one year from its start date
#
#             Args:
#                 start_date (str): Initial start date in YYYY-MM-DD format
#                 end_date (str): Initial end date in YYYY-MM-DD format
#                 terms (int): Number of years to calculate (default 5)
#
#             Returns:
#                 List of tuples with (start_date, end_date) for each year of term
#             """
#             dates = []
#
#             # Convert initial dates to datetime objects
#             start = datetime.strptime(start_date, "%Y-%m-%d")
#             end = datetime.strptime(end_date, "%Y-%m-%d")
#
#             # First year uses the original dates
#             dates.append((start.strftime("%d-%m-%Y"), end.strftime("%d-%m-%Y")))
#
#             # Calculate subsequent years
#             for _ in range(terms - 1):
#                 # Add 7 days to the previous end date for the new start date
#                 new_start = dates[-1][1]
#                 new_start_date = datetime.strptime(new_start, "%d-%m-%Y") + timedelta(days=7)
#
#                 # End date is one year from new start date
#                 new_end_date = new_start_date + timedelta(days=365)
#
#                 dates.append((new_start_date.strftime("%d-%m-%Y"), new_end_date.strftime("%d-%m-%Y")))
#
#             return dates
#
#         years_of_term = calculate_years_of_term(start_date, end_date)
#
#         # Calculate remainder dates
#         def calculate_remainder(end_date):
#             """
#             Calculate remainder dates based on the last year's end date
#
#             Args:
#                 end_date (str): Last year's end date in DD-MM-YYYY format
#
#             Returns:
#                 Tuple of (remainder_start_date, remainder_end_date)
#             """
#             end_date_obj = datetime.strptime(end_date, "%d-%m-%Y")
#
#             # First day of the month
#             start_of_month = end_date_obj.replace(day=1)
#
#             # Last day of the month
#             end_of_month = start_of_month + timedelta(days=31)
#             end_of_month = end_of_month.replace(day=1) - timedelta(days=1)
#
#             return start_of_month.strftime("%d-%m-%Y"), end_of_month.strftime("%d-%m-%Y")
#
#         remainder_start, remainder_end = calculate_remainder(years_of_term[-1][1])
#
#         # Parse escalation
#         def parse_escalation_rate(rate_str):
#             """
#             Parse escalation rate from a string like 'Ten(10)' to a float (e.g., 0.10).
#             """
#             match = re.search(r'\((\d+)\)', rate_str)  # Extract the numeric portion in parentheses
#             if match:
#                 rate_percentage = int(match.group(1))
#                 return rate_percentage / 100  # Convert percentage to decimal
#             raise ValueError(f"Invalid rate format: {rate_str}")
#
#         # Calculate rent escalation
#         def calculate_escalation(base_rent, rate_str, escalation_type, terms=5):
#             """
#             Calculate rent escalation based on base rent, escalation rate, and type.
#             Args:
#                 base_rent (int): The initial yearly rent.
#                 rate_str (str): Escalation rate in a format like 'Ten(10)'.
#                 escalation_type (str): Type of escalation ('Yearly', 'After-First-Two-Years', 'Every-Two-Years').
#                 terms (int): Total number of terms to calculate (default is 5).
#             Returns:
#                 list: A list of escalated rents for each year.
#             """
#             try:
#                 # Parse escalation rate
#                 rate = parse_escalation_rate(rate_str)
#                 base_rent = int(base_rent)
#
#                 # Handle None or empty escalation_type
#                 if not escalation_type:
#                     escalation_type = "Yearly"  # Default to "Yearly" if not provided
#
#                 normalized_type = escalation_type.lower().replace("-", "").replace(" ", "")
#
#                 # Initialize rent escalation list
#                 escalations = [base_rent]
#
#                 # Escalation logic
#                 for year in range(1, terms):
#                     if normalized_type == "yearly":
#                         # Yearly escalation
#                         base_rent += base_rent * rate
#                         escalations.append(int(base_rent))
#                     elif normalized_type in ["afterfirsttwoyears", "aftertwoyears"]:
#                         # Escalation starts after first two years
#                         if year > 2:
#                             base_rent += base_rent * rate
#                         escalations.append(int(base_rent))
#                     elif normalized_type in ["everytwoyears", "twoyears"]:
#                         # Escalation every two years
#                         if year % 2 == 0:
#                             base_rent += base_rent * rate
#                         escalations.append(int(base_rent))
#                     else:
#                         # Default to yearly escalation for unknown types
#                         logger.warning(f"Unknown escalation type '{escalation_type}'. Defaulting to Yearly.")
#                         base_rent += base_rent * rate
#                         escalations.append(int(base_rent))
#
#                 logger.info(f"Calculated Escalations: {escalations}")
#                 return escalations
#             except Exception as e:
#                 logger.error(f"Error calculating escalation: {e}", exc_info=True)
#                 return [base_rent] * terms
#
#         escalated_rents = calculate_escalation(yearly_rent, escalation_rate, escalation_type)
#
#         # Convert dates to words
#         def date_to_words(date_str):
#             date_obj = datetime.strptime(date_str, "%Y-%m-%d")
#             day = int(date_obj.strftime("%d"))
#             day_words = {1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth", 6: "Sixth", 7: "Seventh", 8: "Eighth", 9: "Ninth", 10: "Tenth", 11: "Eleventh", 12: "Twelfth", 13: "Thirteenth", 14: "Fourteenth", 15: "Fifteenth", 16: "Sixteenth", 17: "Seventeenth", 18: "Eighteenth", 19: "Nineteenth", 20: "Twentieth", 21: "Twenty-first", 22: "Twenty-second", 23: "Twenty-third", 24: "Twenty-fourth", 25: "Twenty-fifth", 26: "Twenty-sixth", 27: "Twenty-seventh", 28: "Twenty-eighth", 29: "Twenty-ninth", 30: "Thirtieth", 31: "Thirty-first"}.get(day)
#             month_words = date_obj.strftime("%B")
#             year_words = date_obj.strftime("%Y")
#             return f"{day_words} {month_words} {year_words}"
#
#         start_date_words = date_to_words(start_date)
#         end_date_words = date_to_words(end_date)
#
#         # Convert numbers to words
#         def number_to_words(number):
#             from num2words import num2words
#             return num2words(number, lang="en").capitalize()
#
#         yearly_rent_words = number_to_words(yearly_rent)
#         monthly_rent_words = number_to_words(monthly_rent)
#
#         yearly_rent_text = f"{yearly_rent_words}: KSH {yearly_rent}"
#         monthly_rent_text = f"{monthly_rent_words}: KSH {monthly_rent}"
#
#         # Ensure the template exists
#         script_dir = os.path.dirname(os.path.abspath(__file__))
#         template_path = os.path.join(script_dir, "Golden Ivy Lease Template.docx")
#         output_path = os.path.join(script_dir, "generated_lease.docx")
#
#         if not os.path.exists(template_path):
#             return jsonify({"error": "Template file not found!"}), 500
#
#         # Load the lease document template
#         document = Document(template_path)
#
#         # Replacing escalation terms
#         def replace_escalation_terms(escalated_rents):
#             """
#             Generate replacements for escalation terms in the document template.
#             """
#             escalation_replacements = {}
#
#             def number_to_words(number):
#                 """Convert a number to words."""
#                 return num2words(number, lang="en").capitalize()
#
#             def get_ordinal_suffix(number):
#                 """Get ordinal suffix for a number."""
#                 if 11 <= (number % 100) <= 13:
#                     suffix = "th"
#                 else:
#                     suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
#                 return f"{number}{suffix}"
#
#             for i, rent in enumerate(escalated_rents[1:], start=2):  # Start from the 2nd year
#                 ordinal_suffix = get_ordinal_suffix(i)
#                 rent_words = number_to_words(rent)
#                 monthly_rent = rent // 12
#                 monthly_rent_words = number_to_words(monthly_rent)
#
#                 yearly_key = f"{ordinal_suffix} Year of Term Rental Year Calculation"
#                 monthly_key = f"{ordinal_suffix} Year of Term Rental Month Calculation"
#
#                 escalation_replacements[yearly_key] = f"{rent_words}: KSH {rent}"
#                 escalation_replacements[monthly_key] = f"{monthly_rent_words}: KSH {monthly_rent}"
#
#             return escalation_replacements
#
#         def generate_replacements(data, escalated_rents):
#             """
#             Generate a comprehensive replacements' dictionary.
#
#             Args:
#                 data (dict): Input data from the frontend
#                 escalated_rents (list): List of calculated rents for each year of the term
#
#             Returns:
#                 dict: Comprehensive dictionary of replacements
#             """
#             # Basic replacements from input data
#             replacements = {
#                 "Tenant Name": data.get("tenant_name", "").upper(),
#                 "Phone Number": data.get("phone_number", ""),
#                 "Email Address": data.get("email_address", ""),
#                 "Physical Address": data.get("physical_address", ""),
#                 "Office Number": data.get("office_number", ""),
#                 "Floor Number": data.get("floor_number", "").upper(),
#                 "Date of Lease Entry": format_date(data.get("date_of_lease_entry")),
#                 "Start Date": format_date(data.get("start_date")),
#                 "End Date": format_date(data.get("end_date")),
#                 "Start_Date_in_words": date_to_words(data.get("start_date")),
#                 "End_Date_in_words": date_to_words(data.get("end_date")),
#                 "New or Renew": data.get("new_or_renew", ""),
#                 "Yearly Rent": f"{number_to_words(yearly_rent)}: KSH {yearly_rent}",
#                 "Monthly Rent": f"{number_to_words(monthly_rent)}: KSH {monthly_rent}",
#                 "Lease Term": data.get("lease_duration", ""),
#                 "PO Box number": data.get("po_box", ""),
#                 "post code": data.get("post_code", ""),
#                 "Town of residence": data.get("town", ""),
#                 "Floor plan in Sq foot": data.get("floor_plan", ""),
#                 "Parking Capacity": data.get("parking_capacity", ""),
#                 "Rate of escalation": data.get("escalation_rate", ""),
#                 # Add subsequent dates from years_of_term
#                 "Second Subsequent Starting Date": years_of_term[1][0],
#                 "Second Subsequent Ending Date": years_of_term[1][1],
#                 "Third Subsequent Starting Date": years_of_term[2][0],
#                 "Third Subsequent Ending Date": years_of_term[2][1],
#                 "Fourth Subsequent Starting Date": years_of_term[3][0],
#                 "Fourth Subsequent Ending Date": years_of_term[3][1],
#                 "Fifth Subsequent Starting Date": years_of_term[4][0],
#                 "Fifth Subsequent Ending Date": years_of_term[4][1],
#                 "Remainder Beginning Date": remainder_start,
#                 "Remainder Ending Date": remainder_end,
#                 # Add replacements for escalated rents (yearly and monthly)
#                 "1st Year of Term Rental Year Calculation": "",
#                 "1st Year of Term Rental Month Calculation": "",
#                 "2nd Year of Term Rental Year Calculation": "",
#                 "2nd Year of Term Rental Month Calculation": "",
#                 "3rd Year of Term Rental Year Calculation": "",
#                 "3rd Year of Term Rental Month Calculation": "",
#                 "4th Year of Term Rental Year Calculation": "",
#                 "4th Year of Term Rental Month Calculation": "",
#                 "5th Year of Term Rental Year Calculation":  "",
#                 "5th Year of Term Rental Month Calculation":  ""
#
#             }
#
#             # Add escalation-related replacements
#             escalation_replacements = replace_escalation_terms(escalated_rents)
#
#             # Merge the dictionaries
#             replacements.update(escalation_replacements)
#
#             return replacements
#
#         # In the generate_lease function, replace the existing replacements creation with:
#         replacements = generate_replacements(data, escalated_rents)
#
#         # Replace Text in document and add style formatting
#         def replace_text_with_formatting(document, replacements):
#             """
#             Replace placeholders in all parts of the document, including
#             paragraphs, tables, headers, and footers.
#             """
#
#             def replace_in_paragraph(paragraph):
#                 for key, value in replacements.items():
#                     if key in paragraph.text:
#                         # Completely replace the text in the paragraph
#                         paragraph.text = paragraph.text.replace(key, str(value))
#                         logger.info(f"Replaced '{key}' with '{value}' in paragraph.")
#
#                         # Apply special formatting for specific keys
#                         if key == "Tenant Name":
#                             for run in paragraph.runs:
#                                 run.bold = True
#                                 Pt(14)
#
#             # Replace in body paragraphs
#             for paragraph in document.paragraphs:
#                 replace_in_paragraph(paragraph)
#
#             # Replace in tables
#             for table in document.tables:
#                 for row in table.rows:
#                     for cell in row.cells:
#                         for paragraph in cell.paragraphs:
#                             replace_in_paragraph(paragraph)
#
#             # Replace in headers and footers
#             for section in document.sections:
#                 for header_footer in [section.header, section.footer, section.first_page_header,
#                                       section.first_page_footer]:
#                     if header_footer:
#                         for paragraph in header_footer.paragraphs:
#                             replace_in_paragraph(paragraph)
#
#         replace_text_with_formatting(document, replacements)
#
#         # logging of keys that have not been replaced
#         def log_unmatched_keys(replacements, document):
#             """
#             Log placeholders that are not matched in the document.
#             """
#             original_text = ""
#
#             # Collect all text from the document
#             for paragraph in document.paragraphs:
#                 original_text += paragraph.text
#             for table in document.tables:
#                 for row in table.rows:
#                     for cell in row.cells:
#                         for paragraph in cell.paragraphs:
#                             original_text += paragraph.text
#             for section in document.sections:
#                 for header_footer in [section.header, section.footer, section.first_page_header,
#                                       section.first_page_footer]:
#                     if header_footer:
#                         for paragraph in header_footer.paragraphs:
#                             original_text += paragraph.text
#
#             unmatched_keys = [key for key in replacements if key not in original_text]
#             if unmatched_keys:
#                 logger.warning(f"Unmatched placeholders in the document: {unmatched_keys}")
#
#         # Load the lease document template
#         document = Document(template_path)
#
#         # Call the function to replace placeholders in the document
#         replace_text_with_formatting(document, replacements)
#
#         # Log any unreplaced keys - Add this line right before saving the document
#         log_unmatched_keys(replacements, document)
#
#         # Save the updated document
#         document.save(output_path)
#
#         # Send the generated document to the client
#         return send_file(output_path, as_attachment=True)
#
#     # In your generate_lease function, replace the generic exception handler
#     except Exception as e:
#         logger.error(f"Lease generation error: {str(e)}", exc_info=True)
#         return jsonify({"error": "Failed to generate the lease. Please check your input and try again."}), 500
#
#
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000)
