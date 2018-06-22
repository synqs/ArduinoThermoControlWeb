from app.errors import bp

from flask import render_template, flash
# error handling
@bp.app_errorhandler(500)
def internal_error(error):
    flash('An error occured {}'.format(error), 'error')
    return render_template('500.html'), 500

@bp.app_errorhandler(404)
def page_does_not_exist(error):
    flash('Page does not exist: {}'.format(error), 'error')
    return render_template('404.html'), 404
