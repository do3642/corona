from flask import Blueprint, render_template

bp = Blueprint(
  "domestic",
  __name__,
  template_folder="templates",
  static_folder="static"
  )

@bp.route('/')
def index():
  return render_template('domestic/index.html')