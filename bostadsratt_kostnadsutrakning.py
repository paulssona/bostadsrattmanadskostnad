import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

# Funktion för att beräkna månadskostnader
def calculate_monthly_cost(loan_amount, interest_rate, monthly_fee, amortization):
    monthly_interest_cost = loan_amount * (interest_rate / 100) / 12
    total_cost_before_tax = monthly_interest_cost + monthly_fee + amortization
    tax_deduction = monthly_interest_cost * 0.3
    total_cost_after_tax = total_cost_before_tax - tax_deduction
    return total_cost_before_tax, total_cost_after_tax

# Funktion för att beräkna amortering baserat på låneandel
def calculate_amortization(loan_percentage, loan_amount):
    if loan_percentage > 70:
        return loan_amount * 0.02 / 12
    elif loan_percentage > 50:
        return loan_amount * 0.01 / 12
    else:
        return 0

# Layout för Streamlit-appen
st.title("Bostadsrätt Kostnadsuträkning (3 objekt)")
st.write("Ange parametrarna för tre objekt för att jämföra månadskostnader.")

# Dictionary för att lagra beräkningar som ska exporteras
calculations = {}

# Lista för räntesatserna i Objekt 1
interest_rates_obj1 = [0] * 5

# Inmatningsparametrar för tre objekt med utfällbara sektioner
for i in range(1, 4):
    with st.expander(f"Objekt {i}", expanded=(i == 1)):
        # Anpassningsbart namn
        custom_name = st.text_input(f"Namn för Objekt {i}", value=f"Objekt {i}")
        
        # Pris på bostaden
        property_price = st.number_input(f"Pris på bostaden för {custom_name} (kr):", min_value=0, step=100000, key=f"price_{i}")

        # Manuellt inmatningsfält för lånedelen
        loan_amount = st.number_input(f"Lånedel för {custom_name} (kr):", min_value=0, value=int(property_price * 0.85), step=10000, key=f"loan_amount_{i}")
        
        # Beräkna och visa låneandel och handpenning
        loan_percentage = min(85, loan_amount / property_price * 100) if property_price > 0 else 0
        st.write(f"Låneandel för {custom_name}: {loan_percentage:.1f}%")
        down_payment = property_price - loan_amount
        st.write(f"Handpenning för {custom_name}: {down_payment:,.2f} kr")

        # Amorteringsberäkning och fält
        amortization_auto = calculate_amortization(loan_percentage, loan_amount)
        amortization_input = st.number_input(f"Amortering för {custom_name} (kr/månad):", min_value=0, value=int(amortization_auto), step=100, key=f"amort_{i}")

        # Månadsavgift
        monthly_fee = st.number_input(f"Månadsavgift för {custom_name} (kr):", min_value=0, step=100, key=f"fee_{i}")

        # Räntor för objektet - fem olika räntor på samma rad
        st.write(f"Räntor för {custom_name} (%)")
        cols = st.columns(5)
        
        # Bestäm räntesatser
        if i == 1:
            # Objekt 1 - låt användaren fylla i räntesatser
            interest_rates_obj1 = [
                cols[j].number_input(f"Ränta {j+1}", min_value=0.0, max_value=100.0, step=0.1, key=f"rate_{i}_{j}")
                for j in range(5)
            ]
        else:
            # Kopiera räntesatserna från Objekt 1 som standardvärden, men låt användaren redigera dem
            interest_rates = [
                cols[j].number_input(f"Ränta {j+1}", min_value=0.0, max_value=100.0, value=interest_rates_obj1[j], step=0.1, key=f"rate_{i}_{j}")
                for j in range(5)
            ]

        # Beräkna och spara resultaten
        calculations[custom_name] = []
        for j, rate in enumerate(interest_rates_obj1 if i == 1 else interest_rates, start=1):
            total_cost_before_tax, total_cost_after_tax = calculate_monthly_cost(loan_amount, rate, monthly_fee, amortization_input)
            calculations[custom_name].append({
                "Ränta": rate,
                "Totalkostnad (före skatteavdrag)": total_cost_before_tax,
                "Totalkostnad (efter skatteavdrag)": total_cost_after_tax
            })
            
            # Visa beräkningar för varje ränta
            st.write(f"### {custom_name} - Ränta {j}: {rate}%")
            st.write(f"Totalkostnad per månad (före skatteavdrag): {total_cost_before_tax:,.2f} kr")
            st.write(f"Totalkostnad per månad (efter skatteavdrag): {total_cost_after_tax:,.2f} kr")
    st.write("---")

# PDF-genereringsfunktion
def generate_pdf(calculations):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica", 10)
    y_position = 800  # Startposition på PDF-sidan
    
    for obj_name, rates in calculations.items():
        pdf.drawString(30, y_position, f"{obj_name}:")
        y_position -= 20
        for rate_info in rates:
            rate = rate_info["Ränta"]
            cost_before_tax = rate_info["Totalkostnad (före skatteavdrag)"]
            cost_after_tax = rate_info["Totalkostnad (efter skatteavdrag)"]
            pdf.drawString(30, y_position, f"Ränta {rate}% - Före skatt: {cost_before_tax:,.2f} kr, Efter skatt: {cost_after_tax:,.2f} kr")
            y_position -= 20
            if y_position < 50:
                pdf.showPage()
                y_position = 800

        y_position -= 30  # Mellanrum mellan objekt
    
    pdf.save()
    buffer.seek(0)
    return buffer

# Knapp för PDF-export
if st.button("Ladda ner resultat som PDF"):
    pdf_buffer = generate_pdf(calculations)
    st.download_button(label="Ladda ner PDF", data=pdf_buffer, file_name="kostnadsutrakning.pdf", mime="application/pdf")
