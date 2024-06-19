from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Required for flash messages
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_no = db.Column(db.String(50), unique=True)
    category = db.Column(db.String(50))
    make = db.Column(db.String(50))
    qty = db.Column(db.Integer)
    approved_not_approved = db.Column(db.String(20))
    billable_non_billable = db.Column(db.String(20))
    ordered_qty = db.Column(db.Integer)
    order_status = db.Column(db.String(20))
    podate = db.Column(db.String(50))
    delivery_period = db.Column(db.String(50))
    delivery_at = db.Column(db.String(50))
    supplied_qty = db.Column(db.Integer)
    delivery_status = db.Column(db.String(20))
    backlog_qty = db.Column(db.Integer)
    remarks = db.Column(db.Text)
    loc = db.Column(db.Text)
    po = db.Column(db.Text)
    cname = db.Column(db.Text)
    rev = db.Column(db.Text)

@app.route('/')
def index():
    products = Product.query.all()
    loc = session.get('loc', '')
    po = session.get('po', '')
    cname = session.get('cname', '')
    rev = session.get('rev','')
    no_and_date = session.get('noAndDate', '')
    rev_no_and_date = session.get('revNoAndDate', '')
    iof1 = session.get('iof1', '')
    iof2 = session.get('iof2', '')
    return render_template('index.html', products=products, loc=loc, po=po, no_and_date=no_and_date, 
                           rev_no_and_date=rev_no_and_date, iof1=iof1, iof2=iof2,cname = cname,rev = rev)

@app.route('/add_product', methods=['POST'])
def add_product():
    part_nos = request.form.getlist('partNo[]')
    categories = request.form.getlist('category[]')
    makes = request.form.getlist('make[]')
    qtys = request.form.getlist('qty[]')
    approved_not_approveds = request.form.getlist('approvedNotapproved[]')
    billable_non_billables = request.form.getlist('billableNonBillable[]')
    ordered_qtys = request.form.getlist('orderedQty[]')
    order_statuses = request.form.getlist('orderStatus[]')
    podates = request.form.getlist('podate[]')
    delivery_periods = request.form.getlist('deliveryPeriod[]')
    delivery_ats = request.form.getlist('deliveryAt[]')
    supplied_qtys = request.form.getlist('suppliedQty[]')
    delivery_statuses = request.form.getlist('deliveryStatus[]')
    backlog_qtys = request.form.getlist('backlogQty[]')
    remarks_list = request.form.getlist('remarks[]')

    # Store loc, po, noAndDate, revNoAndDate, iof1, and iof2 in session
    session['loc'] = request.form.get('loc')
    session['po'] = request.form.get('po')
    session['cname'] = request.form.get('cname')
    session['noAndDate'] = request.form.get('noAndDate')
    session['rev'] = request.form.get('rev')
    session['iof1'] = request.form.get('iof1')
    session['iof2'] = request.form.get('iof2')

    for i in range(len(part_nos)):
        part_no = part_nos[i]
        existing_product = Product.query.filter_by(part_no=part_no).first()
        
        if existing_product:
            # Update existing product
            existing_product.category = categories[i]
            existing_product.make = makes[i]
            existing_product.qty = int(qtys[i]) if qtys[i] else 0
            existing_product.approved_not_approved = approved_not_approveds[i]
            existing_product.billable_non_billable = billable_non_billables[i]
            existing_product.ordered_qty = int(ordered_qtys[i]) if ordered_qtys[i] else 0
            existing_product.order_status = order_statuses[i]
            existing_product.podate = podates[i]
            existing_product.delivery_period = delivery_periods[i]
            existing_product.delivery_at = delivery_ats[i]
            existing_product.supplied_qty = int(supplied_qtys[i]) if supplied_qtys[i] else 0
            existing_product.delivery_status = delivery_statuses[i]
            existing_product.backlog_qty = int(backlog_qtys[i]) if backlog_qtys[i] else 0
            existing_product.remarks = remarks_list[i]
        else:
            # Create new product
            new_product = Product(
                part_no=part_no,
                category=categories[i],
                make=makes[i],
                qty=int(qtys[i]) if qtys[i] else 0,
                approved_not_approved=approved_not_approveds[i],
                billable_non_billable=billable_non_billables[i],
                ordered_qty=int(ordered_qtys[i]) if ordered_qtys[i] else 0,
                order_status=order_statuses[i],
                podate=podates[i],
                delivery_period=delivery_periods[i],
                delivery_at=delivery_ats[i],
                supplied_qty=int(supplied_qtys[i]) if supplied_qtys[i] else 0,
                delivery_status=delivery_statuses[i],
                backlog_qty=int(backlog_qtys[i]) if backlog_qtys[i] else 0,
                remarks=remarks_list[i],
                loc=session.get('loc'),  # Retrieve loc from session
                cname=session.get('cname'), 
                po=session.get('po') ,     # Retrieve po from session
                rev = session.get('rev')
            )
            db.session.add(new_product)
    
    db.session.commit()

    flash('Products added successfully!', 'success')
    return redirect(url_for('display'))

@app.route('/delete_product/<int:id>', methods=['GET', 'POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/display')
def display():
    rev = session.get('rev', '')
    loc = session.get('loc', '')
    po = session.get('po', '')
    cname = session.get('cname', '')
    
    products = Product.query.all()
    total_parts = Product.query.distinct(Product.part_no).count()
    approved_tds = sum(1 for product in products if product.approved_not_approved == 'approved')
    not_approved_tds = total_parts - approved_tds
    pending_orders = sum(1 for product in products if product.order_status == 'pending')
    confirmed_orders = sum(1 for product in products if product.order_status == 'confirmed')
    cancelled_orders = sum(1 for product in products if product.order_status == 'cancelled')
    pending_deliveries = sum(1 for product in products if product.delivery_status == 'pending')
    completed_deliveries = sum(1 for product in products if product.delivery_status == 'completed')
    delayed_deliveries = sum(1 for product in products if product.delivery_status == 'delayed')
    return render_template('display.html', loc=loc, po=po,cname = cname, rev = rev,
                           products=products,
                           total_parts=total_parts,
                           approved_tds=approved_tds,
                           not_approved_tds=not_approved_tds,
                           pending_orders=pending_orders,
                           confirmed_orders=confirmed_orders,
                           cancelled_orders=cancelled_orders,
                           pending_deliveries=pending_deliveries,
                           completed_deliveries=completed_deliveries,
                           delayed_deliveries=delayed_deliveries)

def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
