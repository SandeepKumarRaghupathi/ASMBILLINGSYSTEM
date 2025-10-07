import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile
import datetime
import os

# ---- Streamlit Page Config ----
st.set_page_config(page_title="ASM Transports Billing", page_icon="🚛", layout="centered")

st.title("🚛 ASM Transports - Billing System")
st.write("Generate a professional invoice PDF for your customers")

# ---- Input Form ----
with st.form("billing_form"):
    st.subheader("Customer Details")
    customer_name = st.text_input("Customer Name")
    customer_email = st.text_input("Email")
    customer_address = st.text_area("Address")

    st.subheader("Item Details")
    num_items = st.number_input("Number of Items", min_value=1, max_value=20, value=1)

    items = []
    for i in range(num_items):
        st.markdown(f"**Item {i + 1}**")
        item_name = st.text_input(f"Item Name {i + 1}", key=f"name_{i}")
        item_date = st.date_input(f"Date {i + 1}", key=f"date_{i}", value=datetime.date.today())
        item_qty = st.number_input(f"Quantity {i + 1}", min_value=1, value=1, key=f"qty_{i}")
        item_price = st.number_input(f"Price per Unit (₹) {i + 1}", min_value=0.0, value=0.0, key=f"price_{i}")
        items.append({"name": item_name, "date": item_date, "qty": item_qty, "price": item_price})

    st.subheader("Payment Details")
    bank_name = st.text_input("Bank Name", "State Bank of India")
    account_no = st.text_input("Account Number", "XXXXXXXXXXXX")
    ifsc_code = st.text_input("IFSC Code", "SBIN0000000")
    upi_id = st.text_input("UPI ID", "asmtransports@upi")

    submitted = st.form_submit_button("Generate Invoice")


# ---- PDF Generation ----
def generate_invoice(customer_name, customer_email, customer_address, items,
                     logo_path="ASMLOGO.png", bank_name="", account_no="", ifsc_code="", upi_id=""):
    company_name = "ASM Civil Suppliers and Earthmovers"
    company_address = "No:11, Pulavar Nagar, Pavanar Street, Rangapuram, Vellore"
    company_contact = "+91 7708793702, +91 9944808485"

    # Generate invoice number
    today = datetime.datetime.today()
    invoice_no = f"INV-{customer_name.replace(' ', '').upper()}-{today.strftime('%Y-%m-%d-%H%M%S')}"

    total_amount = sum([item["qty"] * item["price"] for item in items])
    grand_total = total_amount

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_file.name, pagesize=A4)
    width, height = A4

    # ---- Page Background ----
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, fill=1)

    # ---- Header Background ----
    header_height = 110
    c.setFillColor(colors.darkgreen)
    c.rect(0, height - header_height, width, header_height, fill=1)

    # ---- Logo in Header ----
    if logo_path and os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        logo_width = 1.2 * inch
        # Calculate y-coordinate from bottom-left
        logo_height = logo_width * logo.getSize()[1] / logo.getSize()[0]  # preserve aspect ratio
        logo_x = 110
        logo_y = height - logo_height - 20  # 20pt padding from top of page
        c.drawImage(logo, logo_x, logo_y, width=logo_width, height=logo_height, mask='auto')

    # ---- Company Info (moved to right side) ----
    company_x = 200  # increase X coordinate to move info to the right
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(company_x, height - 60, company_name)
    c.setFont("Helvetica", 11)
    c.drawString(company_x, height - 80, company_address)
    c.drawString(company_x, height - 95, f"Contact: {company_contact}")

    # ---- Invoice Title ----
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.black)
    c.drawString(230, height - 130, "INVOICE")
    c.setFont("Helvetica", 10)
    c.drawString(450, height - 155, f"Bill Date: {today.strftime('%d-%m-%Y')}")

    # ---- Customer Info ----
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 160, "Customer Details:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 180, f"{customer_name}")
    c.drawString(50, height - 195, f"{customer_email}")
    c.drawString(50, height - 210, f"{customer_address}")

    # ---- Table Headers with Border ----
    y = height - 250
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.setStrokeColor(colors.black)  # border color

    # Draw header background
    c.setFillColor(colors.darkgreen)
    c.rect(50, y - 5, 500, 20, fill=1, stroke=1)  # fill=1, stroke=1 adds border

    # Draw header text
    c.setFillColor(colors.black)
    c.drawString(50, y, "Item")
    c.drawString(230, y, "Date")
    c.drawString(320, y, "Qty")
    c.drawString(370, y, "Price")
    c.drawString(460, y, "Total")
    y -= 25

    # ---- Table Content with Alternating Row Colors ----
    c.setFont("Helvetica", 11)
    for i, item in enumerate(items):
        if y < 120:
            c.showPage()
            y = height - 100

        # row_color = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.black)  # border color
        c.rect(50, y - 5, 500, 20, fill=1, stroke=1)
        c.setFillColor(colors.black)

        total = item["qty"] * item["price"]
        c.drawString(50, y, item["name"])
        c.drawString(230, y, item["date"].strftime("%d-%m-%Y"))
        c.drawString(330, y, str(item["qty"]))
        c.drawString(372, y, f"{item['price']:.2f}")
        c.drawString(462, y, f"{total:.2f}")
        y -= 20

    # ---- Totals ----
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, y, "Grand Total:")
    c.drawString(470, y, f"{grand_total:.2f}")

    # ---- Payment Details ----
    y -= 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Payment Details:")
    c.setFont("Helvetica", 11)
    c.drawString(50, y - 20, f"Bank Name: {bank_name}")
    c.drawString(50, y - 35, f"Account Number: {account_no}")
    c.drawString(50, y - 50, f"IFSC Code: {ifsc_code}")
    c.drawString(50, y - 65, f"UPI ID: {upi_id}")

    # ---- Footer ----
    footer_height = 50
    c.setFillColor(colors.darkgreen)
    c.rect(0, 0, width, footer_height, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 10)
    c.drawString(50, 20, "Thank you for your business!")
    c.drawString(50, 5, "This is a system-generated invoice by ASM Transports.")

    c.save()
    return temp_file.name, invoice_no


# ---- Handle Form Submission ----
if submitted:
    if not customer_name or not any(item["name"] for item in items):
        st.error("⚠️ Please enter customer and item details.")
    else:
        logo_path = "ASMLOGO.png"  # uploaded image file
        pdf_path, invoice_no = generate_invoice(
            customer_name,
            customer_email,
            customer_address,
            items,
            logo_path,
            bank_name,
            account_no,
            ifsc_code,
            upi_id
        )

        with open(pdf_path, "rb") as pdf_file:
            st.success(f"✅ Invoice generated successfully! ({invoice_no})")
            st.download_button(
                label="⬇️ Download Invoice PDF",
                data=pdf_file,
                file_name=f"{invoice_no}.pdf",
                mime="application/pdf",
            )
