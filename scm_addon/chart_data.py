# Copyright (c) 2026, VAPTECH
import frappe
from frappe.utils import today, add_days, get_first_day, get_last_day, \
    add_months, get_year_start, get_year_ending, getdate
from frappe import _
from datetime import date, timedelta


def _resolve_date_range(time_range=None, from_date=None, to_date=None):
    """
    Resolve from_date / to_date from either a preset time_range label
    or explicit from_date + to_date values.
    """
    today_date = today()

    if time_range and time_range != "Custom":
        td = getdate(today_date)

        if time_range == "Today":
            return today_date, today_date

        elif time_range == "Yesterday":
            d = add_days(today_date, -1)
            return d, d

        elif time_range == "This Week":
            start = td - timedelta(days=td.weekday())        # Monday
            end   = start + timedelta(days=6)                # Sunday
            return str(start), str(end)

        elif time_range == "Last Week":
            start = td - timedelta(days=td.weekday() + 7)
            end   = start + timedelta(days=6)
            return str(start), str(end)

        elif time_range == "This Month":
            return str(get_first_day(today_date)), str(get_last_day(today_date))

        elif time_range == "Last Month":
            first = get_first_day(add_months(today_date, -1))
            last  = get_last_day(add_months(today_date, -1))
            return str(first), str(last)

        elif time_range == "This Quarter":
            month = td.month
            q_start_month = ((month - 1) // 3) * 3 + 1
            q_start = date(td.year, q_start_month, 1)
            q_end_month = q_start_month + 2
            q_end = get_last_day(str(date(td.year, q_end_month, 1)))
            return str(q_start), str(q_end)

        elif time_range == "This Year":
            return str(get_year_start(today_date)), str(get_year_ending(today_date))

        elif time_range == "Last Year":
            last_year = td.year - 1
            return str(date(last_year, 1, 1)), str(date(last_year, 12, 31))

    # Fallback: explicit dates or default to today
    return (from_date or today_date), (to_date or today_date)


@frappe.whitelist(allow_guest=True)
def get_daily_sales_rep_performance(
    chart_name=None,
    time_range=None,
    from_date=None,
    to_date=None
):
    from_date, to_date = _resolve_date_range(time_range, from_date, to_date)

    # Get all distinct sales persons
    sales_persons = frappe.get_all("Sales Person", pluck="name", order_by="name")

    if not sales_persons:
        return {"labels": [], "datasets": []}

    # ── 1. Scheduled Visits (Route Plan) ──────────────────────────────────────
    scheduled_raw = frappe.db.sql("""
        SELECT rsr.sales_rep, COUNT(rpt.name) AS cnt
        FROM `tabRoute Plan` rp
        INNER JOIN `tabRoute Plan Sales Reps` rsr ON rsr.parent = rp.name
        INNER JOIN `tabRoute Plan Territory` rpt ON rpt.parent = rp.name
        WHERE rp.status = 1
          AND rp.start_date <= %(to_date)s
          AND rp.end_date   >= %(from_date)s
          AND rsr.sales_rep IN %(persons)s
        GROUP BY rsr.sales_rep
    """, {"from_date": from_date, "to_date": to_date, "persons": sales_persons}, as_dict=True)

    scheduled_map = {r.sales_rep: r.cnt for r in scheduled_raw}

    # ── 2. Visits Made (Customer Visit) ───────────────────────────────────────
    visits_raw = frappe.db.sql("""
        SELECT sales_person, COUNT(name) AS cnt
        FROM `tabCustomer Visit`
        WHERE date BETWEEN %(from_date)s AND %(to_date)s
          AND sales_person IN %(persons)s
        GROUP BY sales_person
    """, {"from_date": from_date, "to_date": to_date, "persons": sales_persons}, as_dict=True)

    visits_map = {r.sales_person: r.cnt for r in visits_raw}

    # ── 3. Orders (via Customer Visit.order_number) ───────────────────────────
    orders_raw = frappe.db.sql("""
        SELECT sales_person, COUNT(DISTINCT order_number) AS cnt
        FROM `tabCustomer Visit`
        WHERE date BETWEEN %(from_date)s AND %(to_date)s
          AND sales_person IN %(persons)s
          AND order_number IS NOT NULL
          AND order_number != ''
        GROUP BY sales_person
    """, {"from_date": from_date, "to_date": to_date, "persons": sales_persons}, as_dict=True)

    orders_map = {r.sales_person: r.cnt for r in orders_raw}

    # ── Build response ─────────────────────────────────────────────────────────
    labels = []
    scheduled_visits = []
    visits_made = []
    orders_count = []

    for person in sales_persons:
        s = scheduled_map.get(person, 0)
        v = visits_map.get(person, 0)
        o = orders_map.get(person, 0)

        if s == 0 and v == 0 and o == 0:
            continue

        labels.append(person)
        scheduled_visits.append(s)
        visits_made.append(v)
        orders_count.append(o)

    return {
        "labels": labels,
        "datasets": [
            {"name": _("Scheduled Visits"), "values": scheduled_visits, "chartType": "bar"},
            {"name": _("Visits Made"),       "values": visits_made,      "chartType": "bar"},
            {"name": _("Orders"),            "values": orders_count,     "chartType": "bar"},
        ]
    }
