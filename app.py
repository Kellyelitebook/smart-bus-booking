import streamlit as st
import random
from datetime import datetime, timedelta
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="NairobiRide",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {background-color: #0f172a; color: #e2e8f0;}
    h1, h2, h3 {color: #22d3ee !important;}
    .stButton>button {background-color: #22d3ee; color: black; font-weight: bold; border-radius: 8px;}
    .ticket-card {background-color: #1e2937; padding: 15px; border-radius: 10px; margin: 8px 0;}
    .success {color: #22c55e;}
</style>
""", unsafe_allow_html=True)

st.title("🚌 NairobiRide")
st.markdown("**Book Smart • Travel Smooth • Kenya's Best Bus Experience**")

# ================== DATA ==================
routes = {
    "Nairobi - Mombasa": {"dist": "480km", "time": "8-9h", "base": 1200},
    "Nairobi - Eldoret": {"dist": "320km", "time": "6-7h", "base": 950},
    "Nairobi - Kisumu": {"dist": "340km", "time": "6h", "base": 850},
    "Nairobi - Nakuru": {"dist": "160km", "time": "3h", "base": 500},
    "Nairobi - Nyeri": {"dist": "160km", "time": "3h", "base": 450},
    "Nairobi - Kitale": {"dist": "380km", "time": "7h", "base": 1100},
    "Nairobi - Malindi": {"dist": "520km", "time": "9h", "base": 1350},
    "Mombasa - Nairobi": {"dist": "480km", "time": "8-9h", "base": 1200},
    "Eldoret - Nairobi": {"dist": "320km", "time": "6-7h", "base": 950},
    "Kisumu - Nairobi": {"dist": "340km", "time": "6h", "base": 850},
}

companies = ["Modern Coast", "Guardian", "Easy Coach", "Kensilver", "Mash East", "Metro Trans"]
bus_models = ["Scania", "Mercedes Benz", "Volvo", "MAN", "Isuzu"]

# ================== SESSION STATE ==================
if 'bookings' not in st.session_state:
    st.session_state.bookings = []
if 'selected_route' not in st.session_state:
    st.session_state.selected_route = None
if 'booking_in_progress' not in st.session_state:
    st.session_state.booking_in_progress = None

# ================== SIDEBAR ==================
st.sidebar.header("🔍 Find Your Bus")

from_city = st.sidebar.selectbox("From", ["Nairobi", "Mombasa", "Eldoret", "Kisumu"])
to_city = st.sidebar.selectbox("To", ["Mombasa", "Eldoret", "Kisumu", "Nakuru", "Nyeri", "Kitale", "Malindi"])
travel_date = st.sidebar.date_input("Travel Date", datetime.today() + timedelta(days=1))

route_key = f"{from_city} - {to_city}" if f"{from_city} - {to_city}" in routes else f"{to_city} - {from_city}"

if st.sidebar.button("🔎 Search Buses", type="primary"):
    st.session_state.selected_route = route_key

# ================== MAIN LAYOUT ==================
col1, col2 = st.columns([7, 3])

with col1:
    if st.session_state.selected_route:
        st.subheader(f"🛣️ {st.session_state.selected_route}")
        info = routes.get(st.session_state.selected_route, {"dist": "N/A", "time": "N/A", "base": 1000})
        st.metric("Estimated Duration", info['time'], delta=info['dist'])

        st.subheader("🚌 Available Buses Today")

        for i in range(5):
            dep_time = (datetime.now() + timedelta(hours=i + 1)).strftime("%H:%M")
            price = info['base'] + random.randint(-300, 600)
            company = random.choice(companies)
            plate = random.choice(["KBA 345P", "KCA 678X", "KDA 112Z", "KMA 990T", "KSA 456Q"])
            model = random.choice(bus_models)
            seats_left = random.randint(8, 35)

            with st.container():
                st.write(f"**{dep_time} • {company}**")
                st.caption(f"**Plate:** {plate} | **Model:** {model} | **Seats Left:** {seats_left}")

                if st.button("Book Now", key=f"book_{i}", use_container_width=True):
                    st.session_state.booking_in_progress = {
                        "route": st.session_state.selected_route,
                        "time": dep_time,
                        "price": price,
                        "company": company,
                        "plate": plate,
                        "model": model,
                        "date": travel_date.strftime("%Y-%m-%d")
                    }
                    st.rerun()
                st.divider()
    else:
        st.info("👈 Please search for a route from the sidebar to see available buses.")

# ================== BOOKING WINDOW (Small Pop-up Style) ==================
if st.session_state.booking_in_progress:
    booking = st.session_state.booking_in_progress
    st.markdown("### 🎟️ Complete Booking")
    
    st.write(f"**Route:** {booking['route']}")
    st.write(f"**Departure:** {booking['time']} on {booking['date']}")
    st.write(f"**Company:** {booking['company']}")
    st.write(f"**Bus:** {booking['plate']} ({booking['model']})")
    st.write(f"**Price:** KES **{booking['price']}**")

    st.write("**Select Your Seat:**")
    seat_cols = st.columns(5)
    selected_seat = None
    for s in range(1, 21):
        if seat_cols[(s-1) % 5].button(f"S{s}", key=f"seatbtn_{s}"):
            selected_seat = f"S{s}"

    if selected_seat:
        st.success(f"✅ Selected Seat: **{selected_seat}**")

        if st.button("✅ Confirm Booking & Download Ticket", type="primary", use_container_width=True):
            final_booking = {**booking, "seat": selected_seat}
            st.session_state.bookings.append(final_booking)

            pdf_bytes = generate_ticket_pdf(final_booking)
            st.download_button(
                label="⬇️ Download PDF Ticket",
                data=pdf_bytes,
                file_name=f"NairobiRide_Ticket_{booking['plate']}.pdf",
                mime="application/pdf"
            )
            st.balloons()
            st.success("🎉 Booking Confirmed Successfully!")
            st.session_state.booking_in_progress = None
            st.rerun()

    if st.button("Cancel Booking", use_container_width=True):
        st.session_state.booking_in_progress = None
        st.rerun()

# ================== MY TICKETS (Right Column) ==================
with col2:
    st.subheader("🎟️ My Tickets")
    if st.session_state.bookings:
        for ticket in reversed(st.session_state.bookings):  # Show latest first
            with st.container():
                st.markdown(f"""
                <div class="ticket-card">
                    <strong>{ticket['route']}</strong><br>
                    {ticket['date']} • {ticket['time']}<br>
                    <small>Seat: {ticket['seat']} | Bus: {ticket['plate']}</small><br>
                    KES {ticket['price']}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No tickets yet.\nBook your first ride!")

# ================== LIVE TRACKING ==================
st.divider()
st.subheader("🚦 Live Bus Tracking")
if st.button("🔄 Refresh Live Positions"):
    st.write("**Buses currently on the road:**")
    for _ in range(3):
        progress = random.randint(35, 92)
        st.progress(progress, text=f"{random.choice(companies)} on {st.session_state.get('selected_route', 'Route')} — {progress}% complete")

st.caption("NairobiRide © 2026 | AI-Assisted Project | Built for Kenyan Travelers")

# ================== PDF GENERATOR ==================
def generate_ticket_pdf(booking):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(150, 780, "NAIROBIRIDE - E-TICKET")

    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Route: {booking['route']}")
    c.drawString(100, 690, f"Date: {booking['date']}   Departure: {booking['time']}")
    c.drawString(100, 660, f"Company: {booking['company']}")
    c.drawString(100, 630, f"Bus Plate: {booking['plate']}   Model: {booking['model']}")
    c.drawString(100, 600, f"Seat Number: {booking['seat']}")
    c.drawString(100, 570, f"Price: KES {booking['price']}")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 500, "✅ Ticket Confirmed - Safe Journey!")
    c.drawString(100, 470, "Please show this ticket at the terminal.")

    c.save()
    buffer.seek(0)
    return buffer