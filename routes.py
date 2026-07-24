from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime, timedelta
from models import db, Booking, CalendarEvent

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

# ==========================================
# AUTH HELPER
# ==========================================

def login_required(f):
    """Blocks access to admin-only routes unless the session flag set at
    login is present. Without this, anyone who knows the URL could open
    /dashboard, /dashboard/orders, /dashboard/calendar, or the API."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access the dashboard.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Admin credentials configured for Owethu using gmail
        if email == 'owethu@gmail.com' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_name'] = 'Owethu'
            flash('Lashed by Owethu', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_name', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.home'))

# --- PRICING DICTIONARY ---
SERVICE_PRICES = {
    "Classic": 280,
    "Cat Eye Classic": 350,
    "Cat Eye": 380,
    "Mega Volume Cat Eye": 400,
    "Hybrid": 350,
    "Wet Eye Set": 450
}

# ==========================================
# PUBLIC ROUTES
# ==========================================

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/book', methods=['POST'])
def book():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    service = request.form.get('service')
    date = request.form.get('date')
    time = request.form.get('time')
    payment_method = request.form.get('payment_method')
    notes = request.form.get('notes')

    base_price = SERVICE_PRICES.get(service, 0)

    # Apply the 40% online discount
    if payment_method == 'online':
        final_price = int(base_price * 0.6)
        payment_status = 'Paid'
    else:
        final_price = base_price
        payment_status = 'Pending'

    new_booking = Booking(
        full_name=name,
        phone=phone,
        email=email,
        service=service,
        date=date,
        time=time,
        payment_method=payment_method,
        notes=notes,
        base_price=base_price,
        final_price=final_price,
        status='Pending',
        payment_status=payment_status
    )

    db.session.add(new_booking)
    db.session.commit()

    flash(f"Success! Your appointment for {service} is requested. Check your email for confirmation.", "success")
    return redirect(url_for('main.home', _anchor='booking'))


# ==========================================
# ADMIN DASHBOARD ROUTES
# ==========================================

def _available_months():
    """Builds the list of 'Month YYYY' options for the dashboard filter,
    based on distinct booking dates, always including the current month."""
    months = set()
    for (date_str,) in db.session.query(Booking.date).distinct():
        try:
            months.add(datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %Y'))
        except (ValueError, TypeError):
            continue
    months.add(datetime.now().strftime('%B %Y'))
    return sorted(months, key=lambda m: datetime.strptime(m, '%B %Y'), reverse=True)

@main.route('/dashboard')
@login_required
def dashboard():
    today_str = datetime.now().strftime('%Y-%m-%d')

    # Basic Stats
    today_bookings = Booking.query.filter_by(date=today_str).all()
    pending_orders = Booking.query.filter_by(status='Pending').count()

    # Revenue calculations (Completed bookings, all time)
    all_completed = Booking.query.filter_by(status='Completed').all()
    revenue_total = sum(b.final_price for b in all_completed)

    # Month filter
    available_months = _available_months()
    selected_month = request.args.get('month', datetime.now().strftime('%B %Y'))
    if selected_month not in available_months:
        selected_month = available_months[0]
    selected_month_label = selected_month
    sel_year_month = datetime.strptime(selected_month, '%B %Y').strftime('%Y-%m')
    revenue_monthly_value = sum(
        b.final_price for b in all_completed if b.date.startswith(sel_year_month)
    )

    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()

    # Data for charts
    chart_dates = [(datetime.now() - timedelta(days=i)).strftime('%m/%d') for i in range(6, -1, -1)]
    chart_date_values = [Booking.query.filter_by(date=(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')).count() for i in range(6, -1, -1)]

    chart_services = list(SERVICE_PRICES.keys())
    chart_service_values = [Booking.query.filter_by(service=s).count() for s in chart_services]

    return render_template(
        'dashboard.html',
        user={'name': session.get('admin_name', 'Owethu')},
        available_months=available_months,
        selected_month=selected_month,
        selected_month_label=selected_month_label,
        total_bookings_today=len(today_bookings),
        pending_orders=pending_orders,
        revenue_total=f"R{revenue_total}",
        revenue_monthly=f"R{revenue_monthly_value}",
        today_bookings=today_bookings,
        recent_bookings=recent_bookings,
        chart_dates=chart_dates,
        chart_date_values=chart_date_values,
        chart_services=chart_services,
        chart_service_values=chart_service_values
    )

@main.route('/dashboard/orders')
@login_required
def orders():
    all_bookings = Booking.query.order_by(Booking.date.desc(), Booking.time.asc()).all()
    all_events = CalendarEvent.query.order_by(CalendarEvent.date.asc()).all()

    for booking in all_bookings:
        client_visits = Booking.query.filter_by(email=booking.email, status='Completed').count()
        booking.client_completed_visits = client_visits
        booking.client_total_visits = Booking.query.filter_by(email=booking.email).count()

    return render_template('orders.html', public_bookings=all_bookings, events=all_events)

@main.route('/dashboard/calendar')
@login_required
def calendar():
    return render_template('calendar.html')

@main.route('/dashboard/events/add', methods=['POST'])
@login_required
def add_event():
    new_event = CalendarEvent(
        title=request.form.get('title'),
        category=request.form.get('category'),
        date=request.form.get('date'),
        description=request.form.get('description')
    )
    db.session.add(new_event)
    db.session.commit()
    return redirect(url_for('main.orders'))

@main.route('/dashboard/bookings/<int:booking_id>/status/<string:new_status>', methods=['POST'])
@login_required
def update_booking_status(booking_id, new_status):
    booking = Booking.query.get_or_404(booking_id)
    if new_status in ['Confirmed', 'Completed', 'Cancelled']:
        booking.status = new_status
        if new_status == 'Completed' and booking.payment_method == 'cash':
            booking.payment_status = 'Paid'

        db.session.commit()
    return redirect(request.referrer or url_for('main.dashboard'))

# ==========================================
# API ENDPOINTS (For JS Calendar)
# ==========================================

@main.route('/api/bookings')
@login_required
def api_bookings():
    bookings = Booking.query.all()
    events = CalendarEvent.query.all()

    bookings_data = [{
        "id": b.id,
        "name": b.full_name,
        "phone": b.phone,
        "service": b.service,
        "date": b.date,
        "time": b.time,
        "status": b.status,
        "price_charged": b.final_price,
        "payment_method": b.payment_method,
        "payment_status": b.payment_status,
        "notes": b.notes
    } for b in bookings]

    events_data = [{
        "id": e.id,
        "title": e.title,
        "category": e.category,
        "date": e.date,
        "description": e.description
    } for e in events]

    return jsonify({"bookings": bookings_data, "events": events_data})