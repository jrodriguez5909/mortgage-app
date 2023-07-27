import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Title
st.title('Mortgage Payment Calculator in the Netherlands')

# Input parameters
house_price = st.number_input('House price (€)', value=500000, step=50000, format="%i")
down_payment = st.number_input('Down payment (€)', value=0, step=5000, format="%i")
annual_interest_rate = st.number_input('Annual interest rate (%)', value=4.5, step=0.1)
loan_term = st.number_input('Loan term (years)', value=30, step=1)
full_year_salary = st.number_input('Full Year Salary (€)', value=50000, step=5000, format="%i")
tax_deduction = st.checkbox('Apply tax deduction (hypotheekrenteaftrek)?')
mortgage_type = st.selectbox('Mortgage Type', ["annuity", "linear"])

tax_rate = 0.37  # fixed tax benefit rate

# Mortgage calculation
loan_amount = house_price - down_payment
monthly_interest_rate = (annual_interest_rate / 100) / 12
num_payments = loan_term * 12

if mortgage_type == "annuity":
    monthly_payment_gross = loan_amount * monthly_interest_rate / (1 - np.power(1 + monthly_interest_rate, -num_payments))
else:  # linear
    principal_monthly_payment = loan_amount / num_payments

# Calculate payment schedule
balance = loan_amount
schedule = []
for i in range(1, int(num_payments) + 1):
    if mortgage_type == "annuity":
        interest_payment = balance * monthly_interest_rate
        principal_payment = monthly_payment_gross - interest_payment
        monthly_payment_gross = interest_payment + principal_payment  # Gross payment remains constant for annuity
    else:  # linear
        interest_payment = balance * monthly_interest_rate
        principal_payment = principal_monthly_payment
        monthly_payment_gross = interest_payment + principal_payment  # Gross payment changes for linear

    if tax_deduction:
        interest_payment_net = interest_payment * (1 - tax_rate)
    else:
        interest_payment_net = interest_payment

    monthly_payment_net = principal_payment + interest_payment_net
    balance -= principal_payment
    schedule.append([i, monthly_payment_gross, monthly_payment_net, principal_payment, interest_payment_net, balance])

schedule_df = pd.DataFrame(schedule, columns=['Payment', 'Total Gross', 'Total Net', 'Principal', 'Interest Net', 'Balance'])

# Group by year
schedule_df['Year'] = (schedule_df['Payment'] - 1) // 12 + 1
schedule_year_df = schedule_df.groupby('Year').mean().reset_index()  # changed from sum to mean to reflect monthly payments

# Create a copy for displaying
display_df = schedule_year_df.copy()

# Format the display DataFrame
display_df['Total Gross'] = '€' + display_df['Total Gross'].round(2).apply('{:,.2f}'.format)
display_df['Total Net'] = '€' + display_df['Total Net'].round(2).apply('{:,.2f}'.format)
display_df['Principal'] = '€' + display_df['Principal'].round(2).apply('{:,.2f}'.format)
display_df['Interest Net'] = '€' + display_df['Interest Net'].round(2).apply('{:,.2f}'.format)
display_df['Balance'] = '€' + display_df['Balance'].round(2).apply('{:,.2f}'.format)

# Output
if tax_deduction:
    st.write(f'Average monthly payment (net): €{monthly_payment_net:,.2f}')
else:
    st.write(f'Average monthly payment (gross): €{monthly_payment_gross:,.2f}')

# Create stacked area chart using plotly
fig = go.Figure()

if tax_deduction:
    fig.add_trace(go.Scatter(
        x=schedule_year_df['Year'], y=schedule_year_df['Principal'], stackgroup='one',
        line=dict(width=0.5), name='Principal'
    ))
    fig.add_trace(go.Scatter(
        x=schedule_year_df['Year'], y=schedule_year_df['Interest Net'], stackgroup='one',
        line=dict(width=0.5), name='Interest (Net)'
    ))
else:
    fig.add_trace(go.Scatter(
        x=schedule_year_df['Year'], y=schedule_year_df['Principal'], stackgroup='one',
        line=dict(width=0.5), name='Principal'
    ))
    fig.add_trace(go.Scatter(
        x=schedule_year_df['Year'], y=schedule_year_df['Total Gross']-schedule_year_df['Principal'], stackgroup='one',
        line=dict(width=0.5), name='Interest (Gross)'
    ))

fig.update_layout(
    showlegend=True,
    xaxis_type='linear',
    xaxis=dict(
        title='Years',
    ),
    yaxis=dict(
        type='linear',
        title='Monthly Payments',
        ticksuffix=' €',
        hoverformat=',.2f'
    ),
    title='Monthly Principal and Interest over Time',
    hovermode='x',
    autosize=True,
)

st.plotly_chart(fig)

# Drop the 'Payment' column from the display DataFrame
display_df = display_df.drop(columns='Payment')

st.dataframe(display_df, width=800, height=800)
