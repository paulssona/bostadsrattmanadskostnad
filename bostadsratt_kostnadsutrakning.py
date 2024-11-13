import streamlit as st

def main():
    st.title("Kostnadsberäkning för Bostadsrätt - Beta 1.1")

    num_objects = 3  # Antal objekt att jämföra

    # Placeholder for objektets namn
    object_names = [st.text_input(f"Namn på objekt {i+1}", value=f"Objekt {i+1}") for i in range(num_objects)]

    # Skapa en sektion för varje objekt
    for i in range(num_objects):
        with st.expander(object_names[i], expanded=(i == 0)):
            st.subheader(f"Ekonomisk information för {object_names[i]}")

            # Användaren anger priset på bostaden
            total_price = st.number_input(f"Pris på bostaden för {object_names[i]} (SEK)", min_value=0, value=3000000, step=50000)

            # Slider för låneandel (0 - 85 %)
            loan_percentage = st.slider(f"Låneandel av priset för {object_names[i]} (%)", min_value=0.0, max_value=85.0, value=85.0, step=0.1)

            # Beräkning av lånebelopp baserat på låneandel och pris
            loan_amount = total_price * (loan_percentage / 100)
            st.write(f"Lånebelopp för {object_names[i]}: {loan_amount:.2f} SEK")

            # Beräkning av handpenning som skillnaden mellan pris och lånebelopp
            down_payment = total_price - loan_amount
            st.write(f"Handpenning för {object_names[i]}: {down_payment:.2f} SEK")

            # Räntor - visas på en rad
            st.write("## Räntor (%)")
            col1, col2, col3, col4, col5 = st.columns(5)
            interest_rates = [
                col1.number_input(f"Ränta 1", min_value=0.0, max_value=100.0, value=3.0, step=0.1),
                col2.number_input(f"Ränta 2", min_value=0.0, max_value=100.0, value=3.0, step=0.1),
                col3.number_input(f"Ränta 3", min_value=0.0, max_value=100.0, value=3.0, step=0.1),
                col4.number_input(f"Ränta 4", min_value=0.0, max_value=100.0, value=3.0, step=0.1),
                col5.number_input(f"Ränta 5", min_value=0.0, max_value=100.0, value=3.0, step=0.1)
            ]

            # Månatlig räntekostnad beräknas för varje ränta
            monthly_interest_costs = [(loan_amount * (rate / 100)) / 12 for rate in interest_rates]

            st.write("### Månatliga kostnader:")
            for j, rate in enumerate(interest_rates):
                st.write(f"Ränta {j+1} ({rate}%): {monthly_interest_costs[j]:.2f} SEK per månad")

            # Månadsavgift
            monthly_fee = st.number_input(f"Månadsavgift för {object_names[i]} (SEK)", min_value=0, value=4000, step=100)

            # Amorteringsbelopp baserat på låneandel
            if loan_percentage > 70:
                amortization = loan_amount * 0.02 / 12
            elif loan_percentage > 50:
                amortization = loan_amount * 0.01 / 12
            else:
                amortization = 0.0
            st.write(f"Amortering per månad för {object_names[i]}: {amortization:.2f} SEK")

            # Total månadskostnad före skatteavdrag
            total_cost_pre_tax = [monthly_interest_cost + monthly_fee + amortization for monthly_interest_cost in monthly_interest_costs]
            st.write("### Total månadskostnad (före skatteavdrag):")
            for j, cost in enumerate(total_cost_pre_tax):
                st.write(f"Med ränta {interest_rates[j]}%: {cost:.2f} SEK")

            # Skatteavdrag (30 % på räntekostnaden)
            tax_deduction = [monthly_interest_cost * 0.3 for monthly_interest_cost in monthly_interest_costs]

            # Total månadskostnad efter skatteavdrag
            total_cost_post_tax = [total_cost_pre_tax[j] - tax_deduction[j] for j in range(len(interest_rates))]
            st.write("### Total månadskostnad (efter skatteavdrag):")
            for j, cost in enumerate(total_cost_post_tax):
                st.write(f"Med ränta {interest_rates[j]}%: {cost:.2f} SEK")

if __name__ == "__main__":
    main()
