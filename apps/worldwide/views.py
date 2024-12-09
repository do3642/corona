from flask import Blueprint, render_template

worldwide_bp = Blueprint(
    'worldwide',
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix='/worldwide'
    )

@worldwide_bp.route('/')
def worldwide_data():
    return render_template('worldwide/worldwide_data.html')
